from django.contrib.auth.models import User
from django.db import models


class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    logo = models.ImageField(upload_to='dept_logos/', blank=True)
    brand_primary = models.CharField(max_length=7, default='#054B70')
    brand_hover = models.CharField(max_length=7, default='#043d5c')
    brand_accent = models.CharField(max_length=7, default='#8CB7C4')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'company'
        verbose_name_plural = 'companies'

    def __str__(self):
        return self.name


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='members',
        verbose_name='company',
    )
    phone_number = models.CharField(max_length=20, blank=True)
    job_title = models.CharField(max_length=100, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True)
    hierarchy_order = models.IntegerField(default=100)
    reports_to = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='direct_reports',
    )

    def __str__(self):
        dept_name = self.department.name if self.department else 'No Department'
        return f"{self.user.username} - {dept_name}"


class KPIFile(models.Model):
    QUARTER_CHOICES = [
        ('Q1', 'Q1 (Jan - Mar)'),
        ('Q2', 'Q2 (Apr - Jun)'),
        ('Q3', 'Q3 (Jul - Sep)'),
        ('Q4', 'Q4 (Oct - Dec)'),
    ]

    employee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='kpi_files')
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='kpi_uploads')
    file = models.FileField(upload_to='kpi_files/')
    title = models.CharField(max_length=200)
    quarter = models.CharField(max_length=2, choices=QUARTER_CHOICES, default='Q1')
    year = models.IntegerField(default=2026)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['year', 'quarter']
        unique_together = ['employee', 'quarter', 'year']

    def __str__(self):
        return f"{self.employee.username} - {self.quarter} {self.year}"
