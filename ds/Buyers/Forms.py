import re

from django.forms import ModelForm
from rest_framework.exceptions import ValidationError

from Buyers.models import *

class UserForm(ModelForm):
    class Meta:
        model = Buyer
        fields = '__all__'
        error_messages = {
            "email": {
                "required": "必须给我选一个邮箱！",
                'invalid' :'邮箱格式错误'

            },
            "password": {

                "required": "必须选择一个密码",


            },
            'yzm' : {
                "required": "必须选择一个密码",
                'invalid': '验证码错误'
        }
        }

        def clean_password(self,password):

            if re.search(r'[^0-9a-zA-Z]',password):
                return self.clean_data['name']

            else:
                raise ValidationError('密码格式不正确')

        def clean_email(self, email):

            if 
                return self.clean_data['name']

            else:
                raise ValidationError('密码格式不正确')
