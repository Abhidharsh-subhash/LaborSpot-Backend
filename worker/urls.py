from django.urls import path
from .import views

urlpatterns= [
    path('WorkerSignUpView/',views.WorkerSignUpView.as_view(),name='WorkerSignUpView'),
]