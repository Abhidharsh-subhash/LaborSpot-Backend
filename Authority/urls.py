from django.urls import path
from .import views

urlpatterns = [
    path('login/',views.AuthorityLoginApiview.as_view(),name='authoritylogin'),
    path('UserList/',views.UserListView.as_view(),name='UserList'),
    path('Category/',views.CategoryView.as_view(),name='Category'),
    path('Category/<int:cat_id>/',views.CategoryView.as_view(),name='Category'),
]