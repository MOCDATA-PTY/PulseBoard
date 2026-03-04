from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    # Admin/Manager views
    path('admin-center/', views.admin_center, name='admin_center'),
    path('admin-center/manage/', views.admin_manage, name='admin_manage'),
    path('admin-center/edit-user/<int:user_id>/', views.admin_edit_user, name='admin_edit_user'),
    path('admin-center/department/<int:dept_id>/', views.admin_department_detail, name='admin_department_detail'),
    path('admin-center/edit-department/<int:dept_id>/', views.admin_edit_department, name='admin_edit_department'),
    path('admin-center/kpi/<int:user_id>/', views.employee_kpi, name='employee_kpi'),
    path('admin-center/kpi/view/<int:file_id>/', views.view_kpi_file, name='view_kpi_file'),
    path('admin-center/kpi/delete/<int:file_id>/', views.delete_kpi_file, name='delete_kpi_file'),
    path('admin-center/org-chart/', views.org_chart, name='org_chart'),
    path('admin-center/department/<int:dept_id>/org-chart/', views.dept_org_chart, name='dept_org_chart'),
    path('admin-center/department/<int:dept_id>/reorder/', views.reorder_hierarchy, name='reorder_hierarchy'),
    path('admin-center/users/', views.admin_users, name='admin_users'),
    path('admin-center/delete-user/<int:user_id>/', views.delete_user, name='delete_user'),
    path('admin-center/delete-department/<int:dept_id>/', views.delete_department, name='delete_department'),

    # User views
    path('dashboard/', views.user_dashboard, name='user_dashboard'),
    path('my-department/', views.department_page, name='department_page'),
    path('profile/<int:user_id>/', views.member_profile, name='member_profile'),
]
