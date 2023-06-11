from django.urls import path
from .import views

urlpatterns = [
    path('login/',views.AuthorityLoginApiview.as_view(),name='authoritylogin'),
]