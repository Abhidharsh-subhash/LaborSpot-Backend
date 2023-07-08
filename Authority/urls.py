from django.urls import path
from .import views

urlpatterns = [
    path('login/',views.AuthorityLoginApiview.as_view(),name='authoritylogin'),
    path('UserView/',views.UserView.as_view(),name='UserList'),
    path('Category/',views.CategoryView.as_view(),name='Category'),
    path('BlockUser/',views.BlockUser.as_view(),name='BlockUser'),
    path('UnblockUser/',views.UnblockUser.as_view(),name='UnblockUser'),
    path('WorkerView/',views.WorkerView.as_view(),name='WorkerView'),
    path('BlockWorker/',views.BlockWorker.as_view(),name='BlockWorker'),
    path('UnblockWorker/',views.UnblockWorker.as_view(),name='UnblockWorker'),
    path('logout/',views.AuthorityLogoutView.as_view(),name='AuthorityLogoutView'),
    path('bookings/',views.Bookings.as_view(),name='bookings'),
    path('privacy/',views.AuthorityPrivacy.as_view(),name='privacy'),
]