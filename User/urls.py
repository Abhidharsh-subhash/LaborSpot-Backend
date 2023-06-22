from django.urls import path
from .import views

urlpatterns = [
    path('signup/',views.UserSignUpView.as_view(),name='UserSignup'),
    path('login/',views.UserLoginView.as_view(),name='login'),
    path('verifyotp/',views.UserVerifyotp.as_view(),name='verifyotp'),
    path('request-reset-email/',views.ForgotPasswordEmail.as_view(),name='request-reset-email'),
    path('password-reset/',views.PasswordTokenCheck.as_view(),name='password-reset-confirm'),
    path('password-reset-complete/',views.SetNewPassword.as_view(),name='password-reset-complete'),
    path('user-home/',views.WorkerList.as_view(),name='user-home'),
    path('profile/',views.UserProfileView.as_view(),name='profile'),
    path('privacy/',views.UserPrivacy.as_view(),name='privacy'),
]