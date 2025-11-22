from typing import Any

from django.contrib.auth import login, authenticate, logout, get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views.generic import TemplateView, UpdateView
from django.urls import reverse_lazy

from users.forms import UserLoginForm, UserRegisterForm
from users.models import CustomUser


class LoginView(TemplateView):
    """
    View for user login
    POST: process login form
    GET: display login form
    """
    template_name = 'users/login.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.method == "POST":
            context['form'] = UserLoginForm(self.request.POST)
        else:
            context['form'] = UserLoginForm()
        return context

    def post(self, request, *args, **kwargs):
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                return redirect('core:index')
        return self.get(request, *args, **kwargs)


class RegisterView(TemplateView):
    """
    View for user registration
    POST: process registration form
    GET: display registration form
    """
    template_name = 'users/register.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.method == "POST":
            context['form'] = UserRegisterForm(self.request.POST)
        else:
            context['form'] = UserRegisterForm()
        return context

    def post(self, request, *args, **kwargs):
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            password = form.cleaned_data.get("password")
            user.set_password(password)
            user.is_active = True
            user.save()
            send_verification(request, user)
            login(request, user)
            return redirect('core:index')
        return self.get(request, *args, **kwargs)


class ProfileView(LoginRequiredMixin, TemplateView):
    """
    View for user profile
    GET: display user profile information
    """
    template_name = 'users/profile.html'
    login_url = 'users:login'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        return context


class ProfileEditView(LoginRequiredMixin, UpdateView):
    """
    View for editing user profile
    GET: display edit profile form
    POST: process edit profile form
    """
    model = CustomUser
    template_name = 'users/profile_edit.html'
    fields = ['username', 'email', 'first_name', 'last_name', 'phone', 'picture']
    success_url = reverse_lazy('users:profile')
    login_url = 'users:login'

    def get_object(self, queryset=None):
        return self.request.user


def user_logout(request) -> Any:
    """
    View for user logout
    GET: log out the user and redirect to homepage
    """
    logout(request)
    return redirect('core:index')


def send_verification(request, user) -> Any:
    """
    Send email verification link to the user
    """
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    domain = get_current_site(request).domain
    link = reverse("users:verify_email", kwargs={"uidb64": uid, "token": token})
    verify_url = f"http://{domain}{link}"
    subject = "Email confirmation"
    message = render_to_string("users/email_verify.html", {
        "user": user,
        "verify_url": verify_url,
    })

    send_mail(subject, message, None, [user.email])


class EmailVerifyView(TemplateView):
    """
    View to verify user's email address
    GET: verify email using uid and token from the link
    Renders success or failure template based on verification result
    """
    template_name = 'users/email_verified_success.html'

    def get(self, request, uidb64, token, *args, **kwargs):
        User = get_user_model()
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except Exception:
            user = None

        if user and default_token_generator.check_token(user, token):
            user.email_is_verified = True
            user.save()
            return render(request, 'users/email_verified_success.html')
        return render(request, 'users/email_verified_failed.html')