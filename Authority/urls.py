from django.urls import path
from .import views

urlpatterns = [
    path('login/',views.AuthorityLoginApiview.as_view(),name='authoritylogin'),
    path('UserList/',views.UserListView.as_view(),name='UserList'),
    path('AddCategory/',views.AddCategoryView.as_view(),name='AddCategoty'),
]