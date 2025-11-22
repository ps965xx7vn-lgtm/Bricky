from django.urls import path

from users import views

app_name = "users"

urlpatterns = [
    path('login/', views.LoginView.as_view(), name='login'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('profile/edit/', views.ProfileEditView.as_view(), name='profile_edit'),
    path('logout/', views.user_logout, name='logout'),
    path('verify-email/<uidb64>/<token>/', views.EmailVerifyView.as_view(), name='verify_email'),
]