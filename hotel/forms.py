from django.contrib.auth.forms import AuthenticationForm
from django import forms
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Room, Table, Finance


class CustomAuthenticationForm(AuthenticationForm):
    role = forms.CharField(widget=forms.HiddenInput(), required=False)

class RegisterForm(UserCreationForm):
    role = forms.ChoiceField(choices=User.ROLE_CHOICES, required=True, label="角色")

    class Meta:
        model = User
        fields = ['username', 'password1', 'password2', 'role']
class AddRoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ['name', 'id_card', 'phone_number', 'check_in_date', 'check_out_date', 'room_number']

class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ['name', 'id_card', 'phone_number', 'check_in_date', 'check_out_date', 'room_number', 'status']
# 点菜表单

class TableForm(forms.ModelForm):
    class Meta:
        model = Table
        fields = ['table_number', 'customer_name', 'customer_phone', 'table_status', 'check_in_time']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 将 table_number 字段设置为只读
        self.fields['table_number'].widget.attrs['readonly'] = True  # 设置只读
class FinanceForm(forms.ModelForm):
    class Meta:
        model = Finance
        fields = ['finance_type', 'responsible_person', 'amount', 'additional_service_amount', 'details']
        widgets = {
            'finance_type': forms.Select(attrs={'class': 'form-control'}),
            'responsible_person': forms.TextInput(attrs={'class': 'form-control'}),
            'details': forms.Textarea(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 可以根据需要自定义字段的初始化方式，例如：
        self.fields['additional_service_amount'].initial = 0