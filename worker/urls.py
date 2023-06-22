from django.urls import path
from .import views

urlpatterns= [
    path('signup/',views.WorkerSignUpView.as_view(),name='signup'),
    path('login/',views.WorkerLoginView.as_view(),name='login'),
    path('verifyotp/',views.WorkerVerifyotp.as_view(),name='verifyotp'),
    path('forgot-password/',views.ForgotPassword.as_view(),name='forgot-password'),
    path('profile/',views.WorkerProfile.as_view(),name='profile'),
    path('privacy/',views.WorkerPrivacy.as_view(),name='privacy'),
]