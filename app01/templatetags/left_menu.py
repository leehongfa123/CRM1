# -*-coding:utf-8 -*-
from django import template
# from article.models import Article
from permission.models import Permission

register = template.Library()


@register.inclusion_tag('menu.html')
def get_menu(request):
    path = request.path

    # 根据登陆人的权限，查找其菜单权限，将有的权限显示再左侧菜单栏中
    menus = {}
    for url in request.session.get('permission_list'):

        permission_obj = Permission.objects.filter(url=url).first()
        if permission_obj.is_menu:

            # 先看是否已经出先过父标签
            if menus.get(permission_obj.menu_number):
                children = menus.get(permission_obj.menu_number).get('children')
            else:
                children = []

            #这是为了对标签添加active效果
            if request.path == permission_obj.url:
                children.append({
                    'ctitle': permission_obj.name,
                    'curl': permission_obj.url,
                    'class' : 'active'
                })
            else:
                children.append({
                    'ctitle': permission_obj.name,
                    'curl': permission_obj.url,
                })


            # 这是为了父级标签的展示效果设计,思路为先找到当前url的父级标签编号
            # 再判断当与请求url父级标签编号一致时添加class，
            # 就添加pclass = "menu-open"

            menu_num = Permission.objects.filter(url=request.path).first().menu_number
            if menu_num == permission_obj.menu_number:
                menus[permission_obj.menu_number] = {
                    'title': permission_obj.pmenu_title,
                    'pclass' : 'menu-open',
                    'children': children

                }
            else:
                menus[permission_obj.menu_number] = {
                    'title': permission_obj.pmenu_title,
                    'children': children
                }

    return {"menus": menus}
