from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from .models import Department, KPIFile, UserProfile


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'


class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'created_at')
    search_fields = ('name',)


@admin.register(KPIFile)
class KPIFileAdmin(admin.ModelAdmin):
    list_display = ('employee', 'title', 'uploaded_by', 'uploaded_at')
    search_fields = ('employee__username', 'employee__first_name', 'title')


admin.site.unregister(User)
admin.site.register(User, UserAdmin)
