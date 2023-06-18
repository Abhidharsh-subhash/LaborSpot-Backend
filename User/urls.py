from django.urls import path
from .import views

urlpatterns = [
    path('signup/',views.UserSignUpView.as_view(),name='UserSignup'),
    path('UserLogin/',views.UserLoginView.as_view(),name='UserLogin'),
    path('UserVerifyotp/',views.UserVerifyotp.as_view(),name='UserVerifyotp'),
    path('privacy/',views.UserPrivacy.as_view(),name='privacy'),
]