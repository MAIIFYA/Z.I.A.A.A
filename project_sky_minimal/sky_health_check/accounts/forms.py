from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, UserChangeForm as BaseUserChangeForm
from django.contrib.auth import get_user_model
from allauth.account.forms import SignupForm, LoginForm
from .models import User

# Get the custom User model
UserModel = get_user_model()

class CustomSignupForm(SignupForm):
    """
    Custom signup form for Sky Health Check
    """
    ROLE_CHOICES = (
        ("engineer", "Engineer"),
    )

    full_name = forms.CharField(max_length=100, required=True)
    role = forms.ChoiceField(choices=ROLE_CHOICES, initial="engineer", disabled=True)

    def save(self, request):
        user = super(CustomSignupForm, self).save(request)
        user.first_name = self.cleaned_data["full_name"].split()[0]
        if len(self.cleaned_data["full_name"].split()) > 1:
            user.last_name = " ".join(self.cleaned_data["full_name"].split()[1:])
        user.role = self.cleaned_data["role"]
        user.save()
        return user

class CustomLoginForm(LoginForm):
    """
    Custom login form for Sky Health Check
    """
    remember_me = forms.BooleanField(required=False, initial=False)

    def __init__(self, *args, **kwargs):
        super(CustomLoginForm, self).__init__(*args, **kwargs)
        self.fields["login"].label = "Email Address"
        self.fields["login"].widget.attrs.update({"placeholder": "johndoe@example.com"})
        self.fields["password"].widget.attrs.update({"placeholder": "••••••••••"})

class UserProfileForm(forms.ModelForm):
    """
    Form for updating user profile
    """
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "username"]

    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({"class": "form-control"})

# --- Admin Forms --- 

class UserAdminCreationForm(UserCreationForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password.
    """
    class Meta(UserCreationForm.Meta):
        model = UserModel
        fields = ("username", "email", "role", "team") # Add custom fields

class UserAdminChangeForm(BaseUserChangeForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin\\\\'s
    password hash display field.
    """
    class Meta(BaseUserChangeForm.Meta):
        model = UserModel
        fields = ("username", "email", "first_name", "last_name", "role", "team", "is_active", "is_staff", "is_superuser", "groups", "user_permissions") # Add custom fields

