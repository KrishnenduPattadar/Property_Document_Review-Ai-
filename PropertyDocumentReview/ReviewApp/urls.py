from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Custom Views
    path('register/', views.signup_view, name='signup'),
    path('profile/', views.profile_view, name='profile'),

    # Built-in Login / Logout
    path('login/', auth_views.LoginView.as_view(
        template_name='ReviewApp/form_generic.html',
        extra_context={'title': 'Login', 'btn_text': 'Login'}
    ), name='login'),
    
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),

    # Password Reset Flow
    path('password-reset/', auth_views.PasswordResetView.as_view(
        template_name='ReviewApp/form_generic.html',
        email_template_name='ReviewApp/password_reset_email.html',
        extra_context={'title': 'Reset Password', 'btn_text': 'Email Me Link'}
    ), name='password_reset'),

    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='ReviewApp/message.html'
    ), name='password_reset_done'),

    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='ReviewApp/form_generic.html',
        extra_context={'title': 'Set New Password', 'btn_text': 'Change Password'}
    ), name='password_reset_confirm'),

    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='ReviewApp/message.html'
    ), name='password_reset_complete'),
    path('download_report/<int:doc_id>/', views.download_report, name='download_report'),
]