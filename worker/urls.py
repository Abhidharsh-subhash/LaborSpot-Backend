from django.urls import path
from .import views

urlpatterns= [
    path('WorkerSignUpView/',views.WorkerSignUpView.as_view(),name='WorkerSignUpView'),
    path('WorkerLoginView/',views.WorkerLoginView.as_view(),name='WorkerLoginView'),
    path('WorkerVerifyotp/',views.WorkerVerifyotp.as_view(),name='WorkerVerifyotp'),
    path('forgot-password/',views.ForgotPassword.as_view(),name='forgot-password'),
]