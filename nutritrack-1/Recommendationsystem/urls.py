"""Recommendationsystem URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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
from django.urls import path,include
from . import index
##from . import UserDashboard
##from . import index
from django.conf import settings
from django.conf.urls.static import static
# from .index import upload_food_image

urlpatterns = [
   
    path('index', index.index),
    
    path('accounts/', include('django.contrib.auth.urls')),  # Default auth views 
    path('about', index.about),
    path('team', index.team),
    path('login', index.login, name="login"),
    path("update_profile/", index.update_profile, name="update_profile"),
    path("dashboard/", index.user_dashboard, name="user_dashboard"),
    path('profile/edit/', index.edit_profile, name='edit_profile'),
    path("upload_food/", index.upload_food_image, name="upload_image"),
    path('log_meal/', index.log_meal, name='log_meal'),
    path('dologin', index.dologin),
    path('registration', index.registration),
    path('Reg', index.Reg),
    

    path('logout', index.logout),
    
]+static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
#+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

