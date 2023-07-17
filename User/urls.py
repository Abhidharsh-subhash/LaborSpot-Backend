from django.urls import path
from .import views

urlpatterns = [
    path('signup/',views.UserSignUpView.as_view(),name='UserSignup'),
    path('login/',views.UserLoginView.as_view(),name='login'),
    path('verifyotp/',views.UserVerifyotp.as_view(),name='verifyotp'),
    path('resend-otp/',views.ResendOtp.as_view(),name='resend-otp'),
    path('request-reset-email/',views.ForgotPasswordEmail.as_view(),name='request-reset-email'),
    path('password-reset/',views.PasswordTokenCheck.as_view(),name='password-reset-confirm'),
    path('password-reset-complete/',views.SetNewPassword.as_view(),name='password-reset-complete'),
    path('worker-list/',views.WorkerList.as_view(),name='worker-list'),
    path('profile/',views.UserProfileView.as_view(),name='profile'),
    path('privacy/',views.UserPrivacy.as_view(),name='privacy'),
    path('booking/',views.WorkerBooking.as_view(),name='booking'),
    path('booking-history/',views.BookingHistory.as_view(),name='booking-history'),
    path('completefeedback/',views.CompleteFeedback.as_view(),name='completefeedback'),
    path('payment/',views.Makepayment.as_view(),name='payment'),
    path('payment_confirmation/',views.PaymentConfirmation.as_view(),name='payment_confirmation'),
]