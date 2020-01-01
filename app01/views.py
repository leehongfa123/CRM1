import random
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

from django.views import View
from django.contrib import auth
from django.db.models import Q
from django.conf import settings
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, HttpResponse, reverse, redirect

from app01.page import Pagination
from app01.models import Customer, ConsultRecord
from app01.forms import UserInfoForm, CustomerModerForm, ConsultRecordModelForm

from app01.models import UserInfo


class LoginRequiredMixin(object):
    @classmethod
    def as_view(cls, *args, **kwargs):
        view = super(LoginRequiredMixin, cls).as_view(*args, **kwargs)
        return login_required(view)


def get_validcode(request):
    def get_random_color():
        '''
        该函数是随机生成背景色的，用rgb模式表示
        :return:
        '''
        import random
        return (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

    # 实例化一个Image对象
    img = Image.new("RGB", (300, 32), get_random_color())

    # 画布
    draw = ImageDraw.Draw(img)
    # 设置字体
    font = ImageFont.truetype("static/font/kumo.ttf", 32)

    # 生成6个随机字符，作为验证码
    # 将下面随机生成的验证码保存起来，并放到session当中，方便后面进行验证
    validcode = ""
    for i in range(6):
        # 生成随机数字、大小写字母
        nums = str(random.randint(0, 10))
        low_letter = chr(random.randint(97, 122))
        upp_letter = chr(random.randint(65, 90))

        # 从上面三选一作为验证码
        choice = random.choice([nums, low_letter, upp_letter])
        # 写入到图片当中
        draw.text((i * 30 + 50, 0), choice, get_random_color(), font=font)

        validcode += choice

    # 将生成的图片临时保存在内存中
    f = BytesIO()
    img.save(f, "png")
    data = f.getvalue()

    print('validcode', validcode)

    # 将验证码存在各自的session中

    request.session['validcode'] = validcode

    return HttpResponse(data)


# 登录视图类
class Login(View):

    def get(self, request):

        get_validcode(request)
        after_login_path = request.GET.get('next')

        return render(request, "login.html", {"after_login_path": after_login_path})


    def post(self, request):

        user = request.POST.get('user')
        pwd = request.POST.get('pwd')
        validcode = request.POST.get('validcode')

        response = {"user": "", "error_msg": ""}
        if validcode == request.session.get('validcode'):
            '''
            验证码正确后进行用户名和密码的验证
            '''
            user_obj = auth.authenticate(username=user, password=pwd)

            if user_obj:
                auth.login(request, user_obj)
                response['user'] = user


                # 登陆的时候就将当前用户的权限取出来，并注入到session中
                login_user_permission = UserInfo.objects.filter(pk=user_obj.pk).values("role__permissions__url").distinct()
                permission_list = []
                for permission in login_user_permission:
                    permission_list.append(permission['role__permissions__url'])
                request.session['permission_list'] = permission_list


            else:
                response['error_msg'] = '用户名或密码错误！'
        else:
            response['error_msg'] = '验证码错误！'

        return JsonResponse(response)

# 注销视图类
class Logout(View):

    def get(self, request):

        request.session.flush()

        return redirect(reverse("login"))



# 注册视图函数
# forms组件进行验证

class Reg(View):

    def get(self, request):
        forms = UserInfoForm()
        return render(request, "reg.html", locals())

    def post(self, request):
        forms = UserInfoForm(request.POST)

        response = {"user": None, "err_msg": None}
        if forms.is_valid():
            # 注册成功
            response['user'] = request.POST.get('username')

            user = forms.cleaned_data.get("username")
            pwd = forms.cleaned_data.get("password")
            email = forms.cleaned_data.get("email")

            user = UserInfo.objects.create_user(username=user, password=pwd, email=email)

        else:
            # 将错误返回给浏览器

            response['error_msg'] = forms.errors

        # 返回response对象
        return JsonResponse(response)


@login_required
def index(request):
    username = request.user
    return render(request, "starter.html", {"username": username})


class CustomerView(LoginRequiredMixin, View):

    def get(self, request):

        if reverse('customers') == request.path:
            label = "公户列表"
            customer_list = Customer.objects.filter(consultant__isnull=True)
        else:
            label = "我的客户"
            customer_list = Customer.objects.filter(consultant=request.user)

        field = request.GET.get('field')
        val = request.GET.get('value')

        q = Q()
        if val:
            q.children.append((field + "__contains", val))
            customer_list = customer_list.filter(q)

        username = request.user

        # 分页
        current_page_num = request.GET.get("page", 1)

        pagination = Pagination(current_page_num, customer_list.count(), request)
        current_page_numbering = (int(current_page_num) - 1) * pagination.per_page_num
        customer_list = customer_list[pagination.start:pagination.end]

        return render(request, "customers.html",
                      {"customer_list": customer_list, "username": username, "pagination": pagination, "label": label,
                       "current_page_numbering": current_page_numbering})

    def post(self, request):

        action_fun = request.POST.get('action')
        action_list = request.POST.getlist('selected_pk_list')
        action_obj = Customer.objects.filter(pk__in=action_list)

        if not hasattr(self, action_fun):
            return HttpResponse('非法输入')
        else:
            fun = getattr(self, action_fun)
            fun(request, action_obj)

            print(request.path)
            return redirect(request.path)

    def patch_reverse_public(self, request, action_obj):
        action_obj.update(consultant=request.user)

    def patch_reverse_private(self, request, action_obj):
        action_obj.update(consultant=None)

    def patch_delete(self, request, action_obj):
        action_obj.delete()


class AddEditCustomer(View):

    def get(self, request, edit_id=None):

        if request.path.startswith('/del_customer/'):

            del_obj = Customer.objects.filter(pk=edit_id).first()

            del_obj.delete()
            if del_obj.consultant:

                return redirect(reverse('mycustomers'))
            else:
                return redirect(reverse('customers'))

        username = request.user
        if edit_id:
            edit_obj = Customer.objects.get(pk=edit_id)
            form = CustomerModerForm(instance=edit_obj)
        else:
            form = CustomerModerForm()

        return render(request, "add_customer.html", {"form": form, "username": username})

    def post(self, request, edit_id=None):

        if edit_id:
            edit_obj = Customer.objects.get(pk=edit_id)
            form = CustomerModerForm(request.POST, instance=edit_obj)
        else:
            form = CustomerModerForm(request.POST)

        if form.is_valid():
            form.save()
            if request.POST.get('consultant'):
                return redirect(reverse('mycustomers'))
            else:
                return redirect(reverse('customers'))
        else:
            return render(request, "add_customer.html", {"form": form})


class ConsultRecordView(View):

    def get(self, request):
        username = request.user

        consult_record_list = ConsultRecord.objects.filter(consultant=request.user)
        customer_id = request.GET.get("customer_id")

        # 看具体某个人的跟进记录
        if customer_id:
            consult_record_list = consult_record_list.filter(customer_id=customer_id)

        return render(request, "consultrecord.html", {"consult_record_list": consult_record_list, "username": username})


class AddConsultRecordView(View):

    def get(self, request):

        # 获取当前登陆人，并将setting文件中当前登录人pk进行修改
        user_obj = request.user
        settings.CURRENT_USER_PK = user_obj.pk

        form = ConsultRecordModelForm()
        return render(request, "add_consult.html", {"form": form})

    def post(self, request):

        form = ConsultRecordModelForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect(reverse('consult_records'))

        else:
            return render(request, "add_consult.html", {"form": form})
