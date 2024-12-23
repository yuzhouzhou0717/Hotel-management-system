from django.urls import path
from . import views

urlpatterns = [
    path('', views.user_login, name='home'),  # 将首页指向 login 视图
    path('login/', views.user_login, name='login'),  # 确保 login 路由存在
    path('register/', views.register, name='register'),
    # 其他视图路由
    path('logout/', views.logout_view, name='logout'),  # 退出登录路由
    # path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    # path('finance_dashboard/', views.finance_dashboard, name='finance_dashboard'),  # 账务管理页面
    path('housing_dashboard/', views.housing_dashboard, name='housing_dashboard'),
    path('add_room/', views.add_room, name='add_room'),
    path('housing_dashboard/edit/<int:room_id>/', views.edit_room, name='edit_room'),
    path('catering_dashboard/', views.catering_dashboard, name='catering_dashboard'),
    path('customer_seat/', views.customer_seat, name='customer_seat'),  # 添加顾客入座路由
    path('catering_dashboard/edit/<int:table_id>/', views.edit_table, name='edit_table'),
    path('dish/', views.dish, name='dish'),  # 跳转到点餐页面
    path('add_to_order/', views.add_to_order, name='add_to_order'),  # 添加菜品到订单
    path('get_order_summary/', views.get_order_summary, name='get_order_summary'),
    path('bill/', views.bills_view, name='bills_view'),  # 跳转到点餐页面
    path('bill/clear_orders/<int:table_number>/', views.clear_orders, name='clear_orders'),
 # 财务管理
    path('finance/', views.finance_dashboard, name='finance_dashboard'),  # 财务管理首页
    # 编辑财务记录的AJAX请求
    path('edit_finance/', views.edit_finance, name='edit_finance'),
    # 删除财务记录的AJAX请求
    path('delete_finance/', views.delete_finance, name='delete_finance'),
path('add_finance/', views.add_finance, name='add_finance'),
    path('manager_dashboard/', views.manager_dashboard, name='manager_dashboard'),
    path('inventory/', views.inventory_dashboard, name='inventory_dashboard'),  # 库存管理页面
    path('add_table1/', views.add_table1, name='add_table1'),
    path('add_room1/', views.add_room1, name='add_room1'),
    path('update_table/', views.update_table, name='update_table'),
    path('update_room/', views.update_room, name='update_room'),
path('delete_table/', views.delete_table, name='delete_table'),
    path('delete_room/', views.delete_room, name='delete_room'),
path('delete_order_item/', views.delete_order_item, name='delete_order_item'),
path('archive_finances/', views.archive_finances, name='archive_finances'),
    path('cancel_seat/<int:table_number>/', views.cancel_seat, name='cancel_seat'),
    path('bill/get_paid_bills/', views.get_paid_bills, name='get_paid_bills'),  # 添加这个路由
]
