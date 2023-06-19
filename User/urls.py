from django.urls import path
from .import views

urlpatterns = [
    path('signup/',views.UserSignUpView.as_view(),name='UserSignup'),
    path('UserLogin/',views.UserLoginView.as_view(),name='UserLogin'),
    path('UserVerifyotp/',views.UserVerifyotp.as_view(),name='UserVerifyotp'),
    path('request-reset-email/',views.ForgotPasswordEmail.as_view(),name='request-reset-email'),
    path('password-reset/<uidb64>/<token>/',views.PasswordTokenCheck.as_view(),name='password-reset-confirm'),
    path('password-reset-complete/',views.SetNewPassword.as_view(),name='password-reset-complete')
]