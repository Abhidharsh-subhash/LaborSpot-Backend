"""LaborSpot URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include,re_path
from rest_framework_simplejwt.views import (TokenObtainPairView,TokenRefreshView,TokenVerifyView)
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
   openapi.Info(
      title="LaborSpot Project API",
      default_version='v1',
      description="""LaborSpot is an innovative platform that connects users with skilled workers on an hourly basis. Whether you need assistance 
      with household chores, professional services, or specialized tasks, LaborSpot makes it easy to find and hire workers for short-term projects. 
      With a simple and intuitive interface, users can browse through a diverse range of workers, view their profiles, and book them based on their 
      availability and expertise. Say goodbye to lengthy contracts and commitments - LaborSpot empowers users to conveniently access reliable workers 
      on an hourly basis, providing flexibility, affordability, and quality service at your fingertips""",
      contact=openapi.Contact(email="abhidharsh1999@gmail.com"),
   ),
   public=True,
   permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    re_path(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('admin/', admin.site.urls),
    path('authority/',include('Authority.urls')),
    path('user/',include('User.urls')),
    path('worker/',include('Worker.urls')),
]
