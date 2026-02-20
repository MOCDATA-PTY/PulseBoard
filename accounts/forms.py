from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Department, KPIFile, UserProfile


class AdminUserCreationForm(UserCreationForm):
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

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].help_text = ''
        self.fields['password2'].help_text = ''

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.is_staff = self.cleaned_data['is_manager']
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
        field_order = ['first_name', 'last_name', 'email', 'department', 'phone_number', 'job_title', 'is_manager', 'profile_picture']
        self.order_fields(field_order)

    def save(self, commit=True):
        profile = super().save(commit=commit)
        if commit:
            user = profile.user
            user.first_name = self.cleaned_data['first_name']
            user.last_name = self.cleaned_data['last_name']
            user.email = self.cleaned_data['email']
            user.is_staff = self.cleaned_data['is_manager']
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
