import json

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .decorators import staff_required
from .forms import AdminUserCreationForm, DepartmentForm, KPIFileUploadForm, UserProfileForm
from .models import Department, KPIFile, UserProfile

# Map department names to template folders
DEPT_TEMPLATES = {
    'Food Safety Agency': 'dept_fsa',
    'ISCM': 'dept_iscm',
    'Eclick': 'dept_eclick',
    'Magnum Opus': 'dept_magnum',
}


SUPER_ADMIN_DEPT = 'Magnum Opus'


def _dept_template(department, template_name):
    if department and department.name in DEPT_TEMPLATES:
        return f"accounts/{DEPT_TEMPLATES[department.name]}/{template_name}"
    return f"accounts/{template_name}"


def _is_super_admin(user):
    """Magnum Opus managers can see everything."""
    profile = getattr(user, 'profile', None)
    if not profile:
        try:
            profile = UserProfile.objects.get(user=user)
        except UserProfile.DoesNotExist:
            return False
    return profile.department and profile.department.name == SUPER_ADMIN_DEPT


def _visible_departments(user):
    """Return departments this manager is allowed to see."""
    if _is_super_admin(user):
        return Department.objects.all()
    profile = getattr(user, 'profile', None)
    if profile and profile.department:
        return Department.objects.filter(pk=profile.department_id)
    return Department.objects.none()


def _can_view_department(user, department):
    """Check if this manager can access a specific department."""
    if _is_super_admin(user):
        return True
    profile = getattr(user, 'profile', None)
    return profile and profile.department_id == department.id


def _can_view_user(manager, target_user):
    """Check if this manager can view a target user."""
    if _is_super_admin(manager):
        return True
    manager_profile = getattr(manager, 'profile', None)
    target_profile = getattr(target_user, 'profile', None)
    if not target_profile:
        try:
            target_profile = UserProfile.objects.get(user=target_user)
        except UserProfile.DoesNotExist:
            return False
    if not manager_profile or not manager_profile.department:
        return False
    return target_profile.department_id == manager_profile.department_id


def _admin_ctx(request, extra=None, view_dept=None):
    is_super = _is_super_admin(request.user)
    profile = getattr(request.user, 'profile', None)
    user_dept = profile.department if profile else None
    # Use the viewed department's branding when provided, otherwise the user's own
    dept = view_dept or user_dept
    brand_name = dept.name if dept else 'Admin Center'
    if not view_dept and is_super:
        brand_name = 'Magnum Opus Consultants'
    ctx = {
        'sidebar_departments': _visible_departments(request.user),
        'is_super_admin': is_super,
        'brand_name': brand_name,
        'brand_primary': dept.brand_primary if dept else '#054B70',
        'brand_hover': dept.brand_hover if dept else '#043d5c',
        'brand_accent': dept.brand_accent if dept else '#8CB7C4',
        'dept_logo': dept.logo if dept and dept.logo else None,
    }
    if extra:
        ctx.update(extra)
    return ctx


@login_required
def home(request):
    if request.user.is_staff:
        return redirect('admin_center')
    return redirect('user_dashboard')


# ─── Admin/Manager Views ────────────────────────────────────

@login_required
@staff_required
def admin_center(request):
    visible_depts = _visible_departments(request.user)
    departments = visible_depts.prefetch_related('members__user')
    users = User.objects.select_related('profile__department').filter(
        profile__department__in=visible_depts
    )
    return render(request, 'accounts/admin_center.html', _admin_ctx(request, {
        'users': users,
        'departments': departments,
        'total_users': users.count(),
        'total_departments': departments.count(),
    }))


@login_required
@staff_required
def admin_manage(request):
    user_form = AdminUserCreationForm()
    show_modal = ''

    if request.method == 'POST':
        action = request.POST.get('action', '')

        if action == 'add_user':
            user_form = AdminUserCreationForm(request.POST)
            if user_form.is_valid():
                user = user_form.save()
                role = 'Manager' if user.is_staff else 'Employee'
                messages.success(request, f'{role} "{user.username}" created and assigned to {user.profile.department}.')
                return redirect('admin_manage')
            show_modal = 'user'

        elif action == 'add_department':
            name = request.POST.get('dept_name', '').strip()
            description = request.POST.get('dept_description', '').strip()
            if name:
                if Department.objects.filter(name=name).exists():
                    messages.error(request, f'Department "{name}" already exists.')
                else:
                    Department.objects.create(name=name, description=description)
                    messages.success(request, f'Department "{name}" created.')
                    return redirect('admin_manage')
            else:
                messages.error(request, 'Department name is required.')
            show_modal = 'dept'

    visible_depts = _visible_departments(request.user)
    departments = visible_depts.prefetch_related('members')
    users = User.objects.select_related('profile__department').filter(
        profile__department__in=visible_depts
    )
    return render(request, 'accounts/admin_manage.html', _admin_ctx(request, {
        'user_form': user_form,
        'all_departments': departments,
        'all_users': users,
        'show_modal': show_modal,
    }))


@login_required
@staff_required
def admin_edit_user(request, user_id):
    target_user = get_object_or_404(User, pk=user_id)
    if not _can_view_user(request.user, target_user):
        return HttpResponseForbidden("You don't have access to this user.")
    profile, _ = UserProfile.objects.get_or_create(user=target_user)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, f'Updated "{target_user.username}".')
            return redirect('admin_users')
    else:
        form = UserProfileForm(instance=profile)
    return render(request, 'accounts/admin_edit_user.html', _admin_ctx(request, {
        'form': form,
        'target_user': target_user,
    }))


@login_required
@staff_required
def admin_department_detail(request, dept_id):
    department = get_object_or_404(Department, pk=dept_id)
    if not _can_view_department(request.user, department):
        return HttpResponseForbidden("You don't have access to this department.")
    members = department.members.select_related('user').all()

    return render(request, 'accounts/admin_department_detail.html', _admin_ctx(request, {
        'department': department,
        'members': members,
    }, view_dept=department))


@login_required
@staff_required
def admin_edit_department(request, dept_id):
    department = get_object_or_404(Department, pk=dept_id)
    if not _can_view_department(request.user, department):
        return HttpResponseForbidden("You don't have access to this department.")
    if request.method == 'POST':
        form = DepartmentForm(request.POST, request.FILES, instance=department)
        if form.is_valid():
            form.save()
            messages.success(request, f'Department "{department.name}" updated.')
            return redirect('admin_manage')
    else:
        form = DepartmentForm(instance=department)
    return render(request, 'accounts/admin_edit_department.html', _admin_ctx(request, {
        'form': form,
        'department': department,
    }, view_dept=department))


@login_required
@staff_required
def employee_kpi(request, user_id):
    employee = get_object_or_404(User, pk=user_id)
    if not _can_view_user(request.user, employee):
        return HttpResponseForbidden("You don't have access to this employee.")
    employee_profile, _ = UserProfile.objects.get_or_create(user=employee)
    department = employee_profile.department
    now = timezone.now()
    current_year = now.year

    # Allow viewing other years via query param
    view_year = int(request.GET.get('year', current_year))

    if request.method == 'POST':
        quarter = request.POST.get('quarter')
        upload_year = int(request.POST.get('year', view_year))
        if quarter in ('Q1', 'Q2', 'Q3', 'Q4') and 'file' in request.FILES:
            # Delete existing file for this quarter if replacing
            existing = KPIFile.objects.filter(employee=employee, quarter=quarter, year=upload_year)
            for old in existing:
                old.file.delete()
                old.delete()
            kpi_file = KPIFile(
                employee=employee,
                uploaded_by=request.user,
                file=request.FILES['file'],
                title=f"{employee.first_name} {employee.last_name} {quarter} {upload_year}",
                quarter=quarter,
                year=upload_year,
            )
            kpi_file.save()
            messages.success(request, f'KPI uploaded for {quarter} {upload_year}.')
            return redirect(f"{request.path}?year={upload_year}")

    # Build quarter data
    quarters = []
    for q_code, q_label in KPIFile.QUARTER_CHOICES:
        kpi = KPIFile.objects.filter(employee=employee, quarter=q_code, year=view_year).first()
        quarters.append({
            'code': q_code,
            'label': q_label,
            'file': kpi,
        })

    return render(request, 'accounts/admin_employee_kpi.html', _admin_ctx(request, {
        'employee': employee,
        'employee_profile': employee_profile,
        'department': department,
        'quarters': quarters,
        'view_year': view_year,
        'current_year': current_year,
    }, view_dept=department))


@login_required
@staff_required
def view_kpi_file(request, file_id):
    kpi_file = get_object_or_404(KPIFile, pk=file_id)
    employee = kpi_file.employee
    if not _can_view_user(request.user, employee):
        return HttpResponseForbidden("You don't have access to this file.")
    employee_profile, _ = UserProfile.objects.get_or_create(user=employee)
    department = employee_profile.department
    file_url = kpi_file.file.url
    file_name = kpi_file.file.name.split('/')[-1]
    ext = file_name.rsplit('.', 1)[-1].lower() if '.' in file_name else ''
    is_viewable = ext in ('pdf', 'png', 'jpg', 'jpeg', 'gif', 'webp')
    is_office = ext in ('xlsx', 'xls', 'docx', 'doc', 'pptx', 'ppt', 'csv')
    return render(request, 'accounts/admin_view_kpi.html', _admin_ctx(request, {
        'kpi_file': kpi_file,
        'employee': employee,
        'employee_profile': employee_profile,
        'department': department,
        'file_url': file_url,
        'file_name': file_name,
        'ext': ext,
        'is_viewable': is_viewable,
        'is_office': is_office,
    }))


@login_required
@staff_required
def delete_kpi_file(request, file_id):
    kpi_file = get_object_or_404(KPIFile, pk=file_id)
    if not _can_view_user(request.user, kpi_file.employee):
        return HttpResponseForbidden("You don't have access to this file.")
    employee_id = kpi_file.employee_id
    year = kpi_file.year
    if request.method == 'POST':
        kpi_file.file.delete()
        kpi_file.delete()
        messages.success(request, 'KPI file deleted.')
    from django.urls import reverse
    return redirect(f"{reverse('employee_kpi', args=[employee_id])}?year={year}")


@login_required
@staff_required
def org_chart(request):
    # Only Magnum Opus managers can see the all-departments org chart
    if not _is_super_admin(request.user):
        # Non-Magnum Opus managers get redirected to their own department org chart
        profile = getattr(request.user, 'profile', None)
        if profile and profile.department:
            return redirect('dept_org_chart', dept_id=profile.department_id)
        return HttpResponseForbidden("You don't have access to this page.")

    departments = Department.objects.prefetch_related('members__user').all()
    dept_data = []
    for dept in departments:
        managers = []
        employees = []
        for member in dept.members.select_related('user').all():
            entry = {'profile': member, 'user': member.user}
            if member.user.is_staff:
                managers.append(entry)
            else:
                employees.append(entry)
        dept_data.append({
            'department': dept,
            'managers': managers,
            'employees': employees,
            'total': len(managers) + len(employees),
        })
    # Unassigned users
    unassigned = UserProfile.objects.filter(department__isnull=True).select_related('user')
    return render(request, 'accounts/admin_org_chart.html', _admin_ctx(request, {
        'dept_data': dept_data,
        'unassigned': unassigned,
    }))


@login_required
@staff_required
def dept_org_chart(request, dept_id):
    department = get_object_or_404(Department, pk=dept_id)
    if not _can_view_department(request.user, department):
        return HttpResponseForbidden("You don't have access to this department.")
    members = department.members.select_related(
        'user', 'reports_to__user'
    ).prefetch_related('direct_reports__user').order_by('hierarchy_order')

    def build_tree(parent_id=None):
        nodes = []
        for m in members:
            parent = m.reports_to_id
            if parent == parent_id:
                children = build_tree(m.id)
                nodes.append({
                    'id': m.id,
                    'user_id': m.user.id,
                    'first_name': m.user.first_name,
                    'last_name': m.user.last_name,
                    'job_title': m.job_title or 'No title',
                    'is_staff': m.user.is_staff,
                    'has_picture': bool(m.profile_picture),
                    'picture_url': m.profile_picture.url if m.profile_picture else '',
                    'initials': (m.user.first_name[:1] + m.user.last_name[:1]),
                    'children': children,
                })
        return nodes

    tree = build_tree(None)

    # Also get unassigned members (those with reports_to pointing outside dept)
    member_ids = set(m.id for m in members)
    assigned_ids = set()
    def collect_ids(nodes):
        for n in nodes:
            assigned_ids.add(n['id'])
            collect_ids(n['children'])
    collect_ids(tree)
    unassigned = [m for m in members if m.id not in assigned_ids]

    return render(request, 'accounts/admin_dept_org_chart.html', _admin_ctx(request, {
        'department': department,
        'tree_json': json.dumps(tree),
        'unassigned': unassigned,
        'member_count': len(list(members)),
    }, view_dept=department))


@login_required
@staff_required
@require_POST
def reorder_hierarchy(request, dept_id):
    department = get_object_or_404(Department, pk=dept_id)
    if not _can_view_department(request.user, department):
        return JsonResponse({'status': 'error', 'msg': 'Access denied'}, status=403)
    try:
        data = json.loads(request.body)
        action = data.get('action', '')

        if action == 'set_parent':
            profile_id = data.get('profile_id')
            parent_id = data.get('parent_id')  # None = make root
            profile = UserProfile.objects.get(pk=profile_id, department=department)
            if parent_id:
                parent = UserProfile.objects.get(pk=parent_id, department=department)
                # Prevent circular reference
                check = parent
                while check.reports_to_id:
                    if check.reports_to_id == profile_id:
                        return JsonResponse({'status': 'error', 'msg': 'Circular reference'}, status=400)
                    check = check.reports_to
                profile.reports_to = parent
            else:
                profile.reports_to = None
            profile.save()
            return JsonResponse({'status': 'ok'})

        elif action == 'reorder':
            order = data.get('order', [])
            for i, pid in enumerate(order):
                UserProfile.objects.filter(pk=pid, department=department).update(hierarchy_order=i)
            return JsonResponse({'status': 'ok'})

        return JsonResponse({'status': 'error', 'msg': 'Unknown action'}, status=400)
    except (json.JSONDecodeError, TypeError, UserProfile.DoesNotExist):
        return JsonResponse({'status': 'error'}, status=400)


@login_required
@staff_required
def admin_users(request):
    visible_depts = _visible_departments(request.user)
    users = User.objects.select_related('profile__department').filter(
        profile__department__in=visible_depts
    )
    departments = visible_depts

    # Filtering
    dept_filter = request.GET.get('department', '')
    role_filter = request.GET.get('role', '')

    if dept_filter:
        if dept_filter == 'unassigned' and _is_super_admin(request.user):
            users = User.objects.select_related('profile__department').filter(
                profile__department__isnull=True
            )
        else:
            users = users.filter(profile__department_id=dept_filter)

    if role_filter == 'manager':
        users = users.filter(is_staff=True)
    elif role_filter == 'employee':
        users = users.filter(is_staff=False)

    return render(request, 'accounts/admin_users.html', _admin_ctx(request, {
        'users': users,
        'departments': departments,
        'dept_filter': dept_filter,
        'role_filter': role_filter,
        'total_users': users.count(),
    }))


@login_required
@staff_required
@require_POST
def delete_user(request, user_id):
    target_user = get_object_or_404(User, pk=user_id)
    if target_user == request.user:
        messages.error(request, "You cannot delete yourself.")
        return redirect('admin_manage')
    if not _can_view_user(request.user, target_user):
        return HttpResponseForbidden("You don't have access to this user.")
    username = target_user.username
    target_user.delete()
    messages.success(request, f'User "{username}" has been deleted.')
    return redirect('admin_manage')


@login_required
@staff_required
@require_POST
def delete_department(request, dept_id):
    department = get_object_or_404(Department, pk=dept_id)
    if not _can_view_department(request.user, department):
        return HttpResponseForbidden("You don't have access to this department.")
    dept_name = department.name
    # Delete all users belonging to this department (except the current user)
    User.objects.filter(profile__department=department).exclude(pk=request.user.pk).delete()
    department.delete()
    messages.success(request, f'Department "{dept_name}" and all its members have been deleted.')
    return redirect('admin_manage')


# ─── Regular User Views ─────────────────────────────────────

@login_required
def user_dashboard(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    department = profile.department
    colleagues = []
    if department:
        colleagues = department.members.select_related('user').exclude(user=request.user)

    return render(request, _dept_template(department, 'dashboard.html'), {
        'profile': profile,
        'department': department,
        'colleagues': colleagues,
    })


@login_required
def department_page(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    department = profile.department
    if not department:
        return render(request, 'accounts/department_page.html', {'department': None, 'members': []})
    members = department.members.select_related('user').all()
    return render(request, _dept_template(department, 'department_detail.html'), {
        'department': department,
        'members': members,
    })


@login_required
def member_profile(request, user_id):
    target_user = get_object_or_404(User, pk=user_id)
    target_profile, _ = UserProfile.objects.get_or_create(user=target_user)
    my_profile, _ = UserProfile.objects.get_or_create(user=request.user)

    if not request.user.is_staff:
        if not my_profile.department or not target_profile.department:
            return redirect('user_dashboard')
        if my_profile.department != target_profile.department:
            return redirect('user_dashboard')

    return render(request, _dept_template(target_profile.department, 'member_profile.html'), {
        'target_user': target_user,
        'target_profile': target_profile,
    })
