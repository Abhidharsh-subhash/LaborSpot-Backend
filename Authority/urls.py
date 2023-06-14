from django.urls import path
from .import views

urlpatterns = [
    path('login/',views.AuthorityLoginApiview.as_view(),name='authoritylogin'),
    path('UserView/',views.UserView.as_view(),name='UserList'),
    path('UserView/<int:user_id>/',views.UserView.as_view(),name='UserList'),
    path('Category/',views.CategoryView.as_view(),name='Category'),
    path('Category/<int:cat_id>/',views.CategoryView.as_view(),name='Category'),
    path('BlockUser/<int:user_id>/',views.BlockUser.as_view(),name='BlockUser'),
    path('UnblockUser/<int:user_id>/',views.UnblockUser.as_view(),name='UnblockUser'),
    path('WorkerView/',views.WorkerView.as_view(),name='WorkerView'),
    path('WorkerView/<int:worker_id>/',views.WorkerView.as_view(),name='WorkerView'),
    path('BlockWorker/<int:worker_id>/',views.BlockWorker.as_view(),name='BlockWorker'),
    path('UnblockWorker/<int:worker_id>/',views.UnblockWorker.as_view(),name='UnblockWorker'),
]