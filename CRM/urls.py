"""CRM URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
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
from django.urls import path, re_path
from app01 import views

urlpatterns = [
    path('admin/', admin.site.urls),
    # 登陆
    path('login/', views.Login.as_view(), name = "login"),
    path('logout/', views.Logout.as_view(), name = "logout"),

    # 验证码
    path('get_validcode/', views.get_validcode, name = "validcode"),
    # 注册
    path('reg/', views.Reg.as_view()),
    #*****************************************************
    path('index/', views.index, name = "index"),


    path('mycustomers/', views.CustomerView.as_view(), name = 'mycustomers'),
    path('customers/', views.CustomerView.as_view(), name = 'customers'),
    # 批量处理部分
    path('patch_action/',views.CustomerView.as_view(), name = 'patch_action'),

    path('add_customer/', views.AddEditCustomer.as_view(), name='add_customer'),
    re_path('edit_customer/(\d+)', views.AddEditCustomer.as_view(), name='edit_customer'),
    re_path('del_customer/(\d+)', views.AddEditCustomer.as_view(), name='del_customer'),

    # 跟进记录
    path('consult_records/', views.ConsultRecordView.as_view(),name="consult_records"),

    path('consult_add/', views.AddConsultRecordView.as_view(),name="consult_add"),

]
