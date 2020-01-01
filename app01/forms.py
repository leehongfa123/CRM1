from django import forms
from app01.models import UserInfo, Customer, ConsultRecord
from django.contrib import auth
from django.core.exceptions import ValidationError
from django.forms import widgets
from multiselectfield.forms.fields import MultiSelectFormField
from django.conf import settings

class UserInfoForm(forms.Form):

    username = forms.CharField(min_length=5, label="用户名", error_messages={'required':'不能为空'})
    password = forms.CharField(min_length=8, label="密码", widget=widgets.PasswordInput())
    r_password = forms.CharField(min_length=8, label="确认密码", widget=widgets.PasswordInput())
    email = forms.EmailField(label="邮箱")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for filed in self.fields.values():
            filed.widget.attrs.update({'class': 'form-control'})


    def clean_username(self):
        val = self.cleaned_data.get('username')
        user = UserInfo.objects.filter(username = val).first()
        if user:
        #用户名重复
            raise ValidationError('用户已经存在！')
        else:
            return val

    def clean_password(self):
        val = self.cleaned_data.get('password')
        if val.isdigit():
            # 是纯数字
            raise ValidationError('密码不能使纯数字！')
        else:
            return val

    def clean_email(self):
        val = self.cleaned_data.get('email')
        if val.endswith('163.com'):
            return val
        else:
            raise ValidationError('必须是163邮箱！')

    def clean(self):
        password = self.cleaned_data.get('password')
        r_password = self.cleaned_data.get('r_password')

        if password and r_password and password != r_password:
            self.add_error("r_password", ValidationError("两次密码不一致！"))
            # raise ValidationError('两次密码不一致')
        else:
            return self.cleaned_data



class CustomerModerForm(forms.ModelForm):

    class Meta:
        model = Customer
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():

            if not isinstance(field, MultiSelectFormField):
                field.widget.attrs.update({'class': 'form-control'})




class ConsultRecordModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        user_obj = UserInfo.objects.get(pk = settings.CURRENT_USER_PK)
        self.fields["consultant"].widget.choices = [(user_obj.pk, user_obj.username)]

        user_customers = Customer.objects.filter(consultant=user_obj)
        customers = []
        for item in user_customers:
            each = (item.pk, item.name)
            customers.append(each)

        self.fields["customer"].widget.choices = customers

        for field in self.fields.values():

            if not isinstance(field, MultiSelectFormField):
                field.widget.attrs.update({'class': 'form-control'})
    class Meta:
        model = ConsultRecord
        # fields="__all__"
        exclude = ["delete_status"]
