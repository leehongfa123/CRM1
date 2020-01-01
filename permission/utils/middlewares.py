import re
from django.shortcuts import HttpResponse
from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import render, HttpResponse, reverse, redirect

class PermissionMiddleWares(MiddlewareMixin):

    def process_request(self, request):

        for reg in ["/login/", "/reg/", "/get_validcode/", "/admin/*"]:
            if re.search(reg, request.path):
                return None
        else:

            # 登录成功以后再进行权限验证
            if request.session.get('permission_list'):

                for reg in request.session.get('permission_list'):
                    reg = "^%s$" % reg
                    if re.search(reg, request.path):
                        return None
                return HttpResponse('没有访问权限')

            # 登录失败，重定位到登录界面
            else:
                return redirect('/login/')
