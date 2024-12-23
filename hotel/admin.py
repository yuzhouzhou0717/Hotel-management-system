from django.contrib import admin
from .models import User, Finance


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'role', 'is_staff', 'is_active')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('role',)}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'is_superuser')}),
    )
from .models import Room

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'room_number', 'check_in_date', 'check_out_date', 'id_card')  # 显示的字段
    search_fields = ('name', 'room_number')  # 可搜索的字段
    list_filter = ('check_in_date', 'check_out_date')  # 筛选器
from .models import Table,Order,Dish
# 或者你也可以直接使用：
# admin.site.register(Room)
admin.site.register(Table)
admin.site.register(Order)
admin.site.register(Dish)
admin.site.register(Finance)