from django.urls import path
from .import views

urlpatterns = [
    path('UserSignup/',views.UserSignUpView.as_view(),name='UserSignup'),
]