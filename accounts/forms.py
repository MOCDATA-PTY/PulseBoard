from django import forms
from django.contrib.auth.models import User

from .models import Department, KPIFile, UserProfile


class AdminUserCreationForm(forms.ModelForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    department = forms.ModelChoiceField(
        queryset=Department.objects.all(),
        required=True,
        empty_label='-- Select Company --',
    )
    phone_number = forms.CharField(max_length=20, required=False)
    job_title = forms.CharField(max_length=100, required=False)
    is_manager = forms.BooleanField(required=False, label='Manager',
                                     help_text='Grant manager access to the Admin Center')
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput, required=False)
    password2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput, required=False)

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')

    def clean(self):
        cleaned_data = super().clean()
        is_manager = cleaned_data.get('is_manager')
        pw1 = cleaned_data.get('password1')
        pw2 = cleaned_data.get('password2')
        if is_manager:
            if not pw1:
                self.add_error('password1', 'Password is required for managers.')
            elif pw1 != pw2:
                self.add_error('password2', 'Passwords do not match.')
        return cleaned_data

    def save(self, commit=True):
        user = User(
            username=self.cleaned_data['username'],
            email=self.cleaned_data['email'],
            first_name=self.cleaned_data['first_name'],
            last_name=self.cleaned_data['last_name'],
            is_staff=self.cleaned_data['is_manager'],
        )
        if self.cleaned_data['is_manager']:
            user.set_password(self.cleaned_data['password1'])
        else:
            user.set_unusable_password()
        if commit:
            user.save()
            profile = user.profile
            profile.department = self.cleaned_data['department']
            profile.phone_number = self.cleaned_data.get('phone_number', '')
            profile.job_title = self.cleaned_data.get('job_title', '')
            profile.save()
        return user


class UserProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(required=False)
    is_manager = forms.BooleanField(required=False, label='Manager',
                                     help_text='Grant manager access to the Admin Center')
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput, required=False)
    password2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput, required=False)

    class Meta:
        model = UserProfile
        fields = ('department', 'phone_number', 'job_title', 'profile_picture')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.initial['first_name'] = self.instance.user.first_name
            self.initial['last_name'] = self.instance.user.last_name
            self.initial['email'] = self.instance.user.email
            self.initial['is_manager'] = self.instance.user.is_staff
        field_order = ['first_name', 'last_name', 'email', 'department', 'phone_number', 'job_title', 'is_manager', 'password1', 'password2', 'profile_picture']
        self.order_fields(field_order)

    def clean(self):
        cleaned_data = super().clean()
        is_manager = cleaned_data.get('is_manager')
        was_manager = self.instance.user.is_staff if self.instance and self.instance.user else False
        pw1 = cleaned_data.get('password1')
        pw2 = cleaned_data.get('password2')
        # Require password when promoting an employee to manager
        if is_manager and not was_manager:
            if not pw1:
                self.add_error('password1', 'Password is required when making someone a manager.')
            elif pw1 != pw2:
                self.add_error('password2', 'Passwords do not match.')
        # If already a manager and password provided, validate match
        if is_manager and was_manager and pw1:
            if pw1 != pw2:
                self.add_error('password2', 'Passwords do not match.')
        return cleaned_data

    def save(self, commit=True):
        profile = super().save(commit=commit)
        if commit:
            user = profile.user
            user.first_name = self.cleaned_data['first_name']
            user.last_name = self.cleaned_data['last_name']
            user.email = self.cleaned_data['email']
            user.is_staff = self.cleaned_data['is_manager']
            # Set password if provided (new manager or password change)
            pw1 = self.cleaned_data.get('password1')
            if pw1:
                user.set_password(pw1)
            # If demoted from manager to employee, remove password
            if not self.cleaned_data['is_manager'] and user.has_usable_password():
                user.set_unusable_password()
            user.save()
        return profile


class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ('name', 'description', 'logo', 'brand_primary', 'brand_hover', 'brand_accent')
        widgets = {
            'brand_primary': forms.TextInput(attrs={'type': 'color'}),
            'brand_hover': forms.TextInput(attrs={'type': 'color'}),
            'brand_accent': forms.TextInput(attrs={'type': 'color'}),
        }
        labels = {
            'brand_primary': 'Primary Color',
            'brand_hover': 'Hover Color',
            'brand_accent': 'Accent Color',
            'logo': 'Company Logo',
        }


class KPIFileUploadForm(forms.ModelForm):
    class Meta:
        model = KPIFile
        fields = ('file',)
