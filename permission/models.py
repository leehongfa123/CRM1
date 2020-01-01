#-*-coding:utf-8 -*-
from django.db import models
from app01.models import UserInfo

class Permission(models.Model):
    name = models.CharField(max_length=32, verbose_name="权限名称")
    url = models.CharField(max_length=32, verbose_name="权限路径")
    is_menu = models.BooleanField(default=False, verbose_name='是否是菜单')
    icon = models.CharField(max_length=32, verbose_name='图标', null=True, blank=True)
    menu_number = models.CharField(max_length=32, verbose_name='菜单栏编号', null=True, blank=True)
    pmenu_title = models.CharField(max_length=32, verbose_name='父标签名称', null=True, blank=True)

    def __str__(self):
        return self.name

class Role(models.Model):
    name = models.CharField(max_length=32, verbose_name = "角色名称")
    permissions = models.ManyToManyField(to='Permission', verbose_name="权限", blank=True)
    users = models.ManyToManyField(to=UserInfo, verbose_name='用户', blank=True)

    def __str__(self):
        return self.name