from django import forms
from django.contrib.auth import get_user_model
from phonenumber_field.formfields import PhoneNumberField
User=get_user_model()

class UserRegisterForm(forms.ModelForm):
    username = forms.CharField(
        label="Username",
        widget=forms.TextInput(attrs={'class': 'form-control','placeholder' : 'Enter your Username'}),
        error_messages = {
            'required' : "Username can't be empty."
        }
    )
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': "Enter your Email"}),
        error_messages={
            'required': "Email can't be empty.",
            'invalid': "Please enter a valid email address."
        }
    )
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': "Enter your Password"}),
        error_messages={
            'required': "Password can't be empty",
        }
    )
    confirm_password = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': "Confirm your Password"}),
        error_messages={
            'required': "Password confirmation can't be empty",
        }
    )
    phone = PhoneNumberField(
        label="Phone Number",
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': "Enter your Phone Number (optional)"})
    )
    
    class Meta:
        model = User
        fields = ["username", "email", "phone"]

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        
        if password and confirm_password:
            if password != confirm_password:
                raise forms.ValidationError("Passwords do not match.")
        
        return cleaned_data


class ProfileEditForm(forms.ModelForm):
    """Form for editing user profile with password change option"""
    username = forms.CharField(
        label="Username",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your username'}),
        error_messages={
            'required': "Username can't be empty."
        }
    )
    email = forms.EmailField(
        label="Email Address",
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter your email'}),
        error_messages={
            'required': "Email can't be empty.",
            'invalid': "Please enter a valid email address."
        }
    )
    password = forms.CharField(
        label="New Password (leave blank to keep current)",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter new password (optional)'}),
        required=False,
        error_messages={
            'required': "Password can't be empty",
        }
    )
    confirm_password = forms.CharField(
        label="Confirm New Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm new password (optional)'}),
        required=False,
        error_messages={
            'required': "Password confirmation can't be empty",
        }
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'phone', 'picture']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your first name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your last name'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your phone number'}),
            'picture': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def clean_username(self):
        username = self.cleaned_data.get('username')
        # Check if username is taken by another user
        if User.objects.filter(username=username).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("This username is already taken.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        # Check if email is used by another user
        if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("This email is already registered.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        
        # Only validate if password is being changed
        if password or confirm_password:
            if password and confirm_password:
                if password != confirm_password:
                    raise forms.ValidationError("Passwords do not match.")
            elif password or confirm_password:
                raise forms.ValidationError("Please fill in both password fields or leave both empty.")
        
        return cleaned_data
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered.")
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("This username is already taken.")
        return username


class UserLoginForm(forms.Form):
    username = forms.CharField(
        label="Username",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your Username'}),
        error_messages={
            'required': "Username can't be empty."
        }
    )
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': "Enter your Password"}),
        error_messages={
            'required': "Password can't be empty",
        }
    )


class ForgotPasswordForm(forms.Form):
    """Form for requesting password reset"""
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': "Enter your email address"}),
        error_messages={
            'required': "Email can't be empty.",
            'invalid': "Please enter a valid email address."
        }
    )

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is not registered with us.")
        return email


class ResetPasswordForm(forms.Form):
    """Form for resetting password with new password"""
    password = forms.CharField(
        label="New Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': "Enter your new password"}),
        error_messages={
            'required': "Password can't be empty",
        }
    )
    confirm_password = forms.CharField(
        label="Confirm New Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': "Confirm your new password"}),
        error_messages={
            'required': "Password confirmation can't be empty",
        }
    )

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        
        if password and confirm_password:
            if password != confirm_password:
                raise forms.ValidationError("Passwords do not match.")
        
        return cleaned_data
