from functools import wraps

import openpyxl
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt

from .forms import CustomAuthenticationForm, RegisterForm, AddRoomForm, RoomForm, TableForm, FinanceForm
from .models import User, Room, Customer, Dish, Order, Finance, Bill

from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages
from .forms import CustomAuthenticationForm
from .models import User
from django.contrib.auth import authenticate, login
import json  # 用于解析请求体中的 JSON 数据

from datetime import datetime

def user_login(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(data=request.POST)

        # 获取表单数据
        username = request.POST.get('username')  # 用户名
        password = request.POST.get('password')  # 密码
        selected_role = request.POST.get('role')  # 选择的身份角色

        # 1. 首先检查数据库中是否有选择的角色和用户名
        try:
            user = User.objects.get(username=username, role=selected_role)
        except User.DoesNotExist:
            # 如果没有找到这个用户名和角色的组合
            messages.error(request, '无此用户或角色不匹配。')
            return redirect('login')

        # 2. 找到用户后，进行密码验证
        user = authenticate(request, username=username, password=password)

        if user is not None:
            # 密码验证成功，登录并重定向到不同的页面
            login(request, user)

            # 根据用户角色重定向到不同的页面
            if user.role == 'finance':
                return redirect('finance_dashboard')  # 财务管理人员主页
            elif user.role == 'housing':
                return redirect('housing_dashboard')  # 住房管理人员主页
            elif user.role == 'catering':
                return redirect('catering_dashboard')  # 餐饮管理人员主页
            elif user.role == 'inventory':
                return redirect('inventory_dashboard')  # 库存管理人员主页
            elif user.role == 'manager':
                return redirect('manager_dashboard')  # 总经理主页
            else:
                messages.error(request, '角色无效，请联系管理员。')
                return redirect('login')
        else:
            # 密码错误
            messages.error(request, '用户名或密码错误。')
            return redirect('login')

    else:
        form = CustomAuthenticationForm()

    return render(request, 'login.html', {'form': form})


def role_required(*roles):
    """
    检查用户是否具有指定的角色（支持多个角色）。
    """

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                messages.error(request, "请先登录。")
                return redirect('login')  # 如果未登录，重定向到登录页面

            # 如果用户角色不在传入的角色列表中，重定向到登录页面
            if not any(role == request.user.role for role in roles):
                messages.error(request, f"您无权访问此页面，您需要具有以下身份之一：{', '.join(roles)}。")
                return redirect('login')  # 重定向到登录页面

            return view_func(request, *args, **kwargs)

        return _wrapped_view

    return decorator
def logout_view(request):
    logout(request)
    return redirect('login')  # 退出后跳转到登录页面
def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, '注册成功')
            return redirect('home')  # 注册成功后重定向
        else:
            # 打印表单错误
            # 提示中文错误信息
            for field, errors in form.errors.items():
                for error in errors:
                    if field == 'password2' and "too short" in error:
                        messages.error(request, "密码太短，至少需要8个字符。")
                    elif field == 'password2' and "too common" in error:
                        messages.error(request, "密码过于常见，请使用更复杂的密码。")
                    elif field == 'password2' and "entirely numeric" in error:
                        messages.error(request, "密码不能为纯数字，请包含字母或特殊字符。")
                    else:
                        messages.error(request, f"{field}: {error}")
    else:
        form = RegisterForm()

    return render(request, 'register.html', {'form': form})

from django.shortcuts import render


# def housing_dashboard(request):
#     rooms = Room.objects.all()  # 获取所有房间对象
#     return render(request, 'housing_dashboard.html', {'rooms': rooms})
@login_required
@role_required('manager','housing','admin')  # 只有角色为 housing 的用户才能访问
def housing_dashboard(request):
    if not request.user.is_authenticated:
        return redirect('login')  # 如果用户没有登录，重定向到登录页面
    is_manager = request.user.is_staff  # 假设根据 `is_staff` 判断总经理身份
    base_template = 'manage_base.html' if is_manager else 'house_base.html'
    filter_choice = request.GET.get('filter', 'all')

    if filter_choice == 'vacant':
        rooms = Room.objects.filter(status='vacant')
    elif filter_choice == 'occupied':
        rooms = Room.objects.filter(status='occupied')
    elif filter_choice == 'cleaning':
        rooms = Room.objects.filter(status='cleaning')
    elif filter_choice == 'maintenance':
        rooms = Room.objects.filter(status='maintenance')
    elif filter_choice == '99':
        rooms = Room.objects.filter(price=99)
    elif filter_choice == '199':
        rooms = Room.objects.filter(price=199)
    elif filter_choice == '399':
        rooms = Room.objects.filter(price=399)
    else:
        rooms = Room.objects.all()
    return render(
        request,
        'housing_dashboard.html',
        {'rooms': rooms,  'filter': filter_choice,'base_template': base_template}
    )
def calculate_stay_days(check_in_date, check_out_date):
    # 计算入住天数
    stay_days = (check_out_date - check_in_date).days
    return stay_days
@login_required
@role_required('manager','housing','admin')  # 只有角色为 housing 的用户才能访问
def add_room(request):
    is_manager = request.user.is_staff  # 假设根据 `is_staff` 判断总经理身份
    base_template = 'manage_base.html' if is_manager else 'house_base.html'
    # 获取未预定的房间列表
    available_rooms = Room.objects.filter(status=Room.VACANT)

    if request.method == "POST":
        form = AddRoomForm(request.POST)
        if form.is_valid():
            # 保存表单数据
            room_number = form.cleaned_data['room_number']
            room = Room.objects.get(room_number=room_number)
            room.status = Room.OCCUPIED
            room.name = form.cleaned_data['name']
            room.id_card = form.cleaned_data['id_card']
            room.phone_number = form.cleaned_data['phone_number']
            room.check_in_date = form.cleaned_data['check_in_date']
            room.check_out_date = form.cleaned_data['check_out_date']
            room.save()
            # 计算入住天数
            stay_days = calculate_stay_days(room.check_in_date, room.check_out_date)
            # # 将住房信息保存到财务表
            # finance = Finance(
            #     finance_type="住房",  # 财务类型：住房
            #     responsible_person="y1",  # 假设负责人是张三，实际可以从当前用户获取
            #     amount=room.price * stay_days,  # 计算总房费
            #     # details=f"入住房间: {room.room_number}, 顾客姓名: {room.name},+ "" +入住日期: {room.check_in_date},离店日期: {room.check_out_date}",
            #     details=(
            #         f"入住房间: {room.room_number}\n"
            #         f"顾客姓名: {room.name}\n"
            #         f"入住日期: {room.check_in_date}\n"
            #         f"离店日期: {room.check_out_date}"
            #     )
            # )
            # finance.save()

            messages.success(request, '房间信息已成功添加并保存到财务记录中！')
            return redirect('housing_dashboard')  # 保存成功后跳转到首页
    else:
        form = AddRoomForm()
    return render(
        request,
        'add_room.html',
    {'form': form, 'available_rooms': available_rooms,'base_template': base_template}
    )
@login_required
@role_required('manager','housing','admin')  # 只有角色为 housing 的用户才能访问
def edit_room(request, room_id):
    is_manager = request.user.is_staff  # 假设根据 `is_staff` 判断总经理身份
    base_template = 'manage_base.html' if is_manager else 'house_base.html'
    # 获取房间实例
    room = get_object_or_404(Room, room_number=room_id)

    if request.method == 'POST':
        if 'checkout' in request.POST:
            # 处理退房逻辑
            # 将住房信息保存到财务表
            # 计算入住天数
            stay_days = calculate_stay_days(room.check_in_date, room.check_out_date)
            finance = Finance(
                finance_type="住房",  # 财务类型：住房
                responsible_person="y1",  # 假设负责人是张三，实际可以从当前用户获取
                amount=room.price * stay_days,  # 计算总房费
                # details=f"入住房间: {room.room_number}, 顾客姓名: {room.name},+ "" +入住日期: {room.check_in_date},离店日期: {room.check_out_date}",
                details=(
                    f"入住房间: {room.room_number}\n"
                    f"顾客姓名: {room.name}\n"
                    f"入住日期: {room.check_in_date}\n"
                    f"离店日期: {room.check_out_date}"
                )
            )
            finance.save()
            room.status = Room.VACANT  # 设置房间为“空房”
            room.name = ''  # 清空顾客姓名
            room.id_card = ''  # 清空身份证号
            room.phone_number = ''  # 清空身份证号
            room.check_in_date = None  # 清空入住日期
            room.check_out_date = None  # 清空离店日期
            room.save()

            # 提示退房成功
            messages.success(request, "房间已成功退房。")
            return redirect('housing_dashboard')  # 或者跳转到其他页面
        else:
            # 传递实例到表单中
            form = RoomForm(request.POST, instance=room)
            if form.is_valid():
                form.save()
                # 将住房信息保存到财务表
                # 计算入住天数
                stay_days = calculate_stay_days(room.check_in_date, room.check_out_date)
                # finance = Finance(
                #     finance_type="住房",  # 财务类型：住房
                #     responsible_person="y1",  # 假设负责人是张三，实际可以从当前用户获取
                #     amount=room.price * stay_days,  # 计算总房费
                #     # details=f"入住房间: {room.room_number}, 顾客姓名: {room.name},+ "" +入住日期: {room.check_in_date},离店日期: {room.check_out_date}",
                #     details=(
                #         f"入住房间: {room.room_number}\n"
                #         f"顾客姓名: {room.name}\n"
                #         f"入住日期: {room.check_in_date}\n"
                #         f"离店日期: {room.check_out_date}"
                #     )
                # )
                # finance.save()
                return redirect('housing_dashboard')
    else:
        form = RoomForm(instance=room)  # 编辑现有房间时传递实例

    return render(request, 'edit_room.html', {'form': form, 'room': room,'base_template': base_template})
@login_required
@role_required('manager','catering','admin')  # 只有角色为 housing 的用户才能访问
def catering_dashboard(request):
    is_manager = request.user.is_staff  # 假设根据 `is_staff` 判断总经理身份
    base_template = 'manage_base.html' if is_manager else 'table_base.html'
    # 获取查询参数
    filter_option = request.GET.get('filter_option', 'all')  # 默认显示所有餐桌
    search_table = request.GET.get('search_table', '').strip()  # 获取搜索餐桌号参数
    # 根据筛选条件过滤餐桌
    # 根据餐桌号进行搜索
    if search_table:
        tables = Table.objects.filter(table_number=search_table)
    elif filter_option == 'vacant':
        tables = Table.objects.filter(table_status='vacant')
    elif filter_option == 'occupied':
        tables = Table.objects.filter(table_status='occupied')
    elif filter_option == 'hall':
        tables = Table.objects.filter(seat_type='hall')
    elif filter_option == 'box':
        tables = Table.objects.filter(seat_type='box')
    else:
        tables = Table.objects.all()  # 显示所有餐桌


    return render(
        request,
        'catering_dashboard.html',
        {'tables': tables, 'base_template': base_template,  'search_table': search_table}
    )

from .models import Table
# 顾客就座视图
# 顾客就座视图
from django.utils import timezone
from datetime import datetime
@login_required
@role_required('manager','catering','admin')  # 只有角色为 housing 的用户才能访问
def customer_seat(request):
    is_manager = request.user.is_staff  # 假设根据 `is_staff` 判断总经理身份
    base_template = 'manage_base.html' if is_manager else 'table_base.html'
    seat_type = request.GET.get('seat_type', 'hall')  # 获取选择的座位类型，默认是大厅座
    tables = Table.objects.filter(seat_type=seat_type, table_status='vacant')  # 根据座位类型过滤
    if request.method == 'POST':
        # 获取表单数据
        customer_name = request.POST.get('customer_name')
        customer_phone = request.POST.get('customer_phone')  # 获取手机号
        check_in_time = request.POST.get('check_in_time')
        table_id = request.POST.get('table_number')

        print(f"顾客姓名: {customer_name}")  # 打印顾客姓名，检查是否正确接收到数据
        # 验证输入
        if not customer_name or not customer_phone or not check_in_time or not table_id:
            messages.error(request, '请填写所有必填字段')
            return render(request, 'customer_seat.html', {'tables':tables,'base_template': base_template})

        try:
            # 将 `check_in_time` 转换为日期时间对象
            check_in_time_naive = datetime.strptime(check_in_time, '%Y-%m-%dT%H:%M')  # 解析前端日期时间格式
            check_in_time_aware = timezone.make_aware(check_in_time_naive)  # 转换为时区感知时间
            # 更新餐桌状态
            table = Table.objects.get(id=table_id)
            table.table_status = 'occupied'  # 标记为已占用
            table.customer_phone = customer_phone
            table.check_in_time = check_in_time_aware
            table.customer_name = customer_name
            table.save()
            # 创建顾客记录
            customer = Customer.objects.create(
                name=customer_name,
                phone=customer_phone,
                check_in_time=check_in_time_aware,
                table=table
            )
            print(f"顾客姓名: {customer_name}")  # 确保顾客姓名已被正确创建并存储
            # 提示用户
            messages.success(request, f'顾客 {customer_name} 成功入座！')

            return redirect('catering_dashboard')  # 可根据实际需求跳转到适当的页面
        except Table.DoesNotExist:
            messages.error(request, '选择的座位不存在')
        except Exception as e:
            messages.error(request, f'入座操作失败: {str(e)}')
            # 返回 JSON 格式的座位数据
        table_data = [{'id': table.id, 'table_number': table.table_number} for table in tables]
        return JsonResponse({'tables': table_data})
        # 如果是 AJAX 请求，返回 JSON 格式的座位数据
        # 检查是否为 AJAX 请求
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # 返回 JSON 数据
        table_data = [{'id': table.id, 'table_number': table.table_number} for table in tables]
        return JsonResponse({'tables': table_data})
    return render(request, 'customer_seat.html', {'tables': tables,'base_template': base_template})
@login_required
@role_required('manager','catering','admin')  # 只有角色为 housing 的用户才能访问
def edit_table(request, table_id):
    is_manager = request.user.is_staff  # 假设根据 `is_staff` 判断总经理身份
    base_template = 'manage_base.html' if is_manager else 'table_base.html'
    table = get_object_or_404(Table, table_number=table_id)

    if request.method == 'POST':
        # 将表单与提交的数据绑定
        form = TableForm(request.POST, instance=table)

        # 不要让 table_number 通过表单提交，手动设置它
        form.instance.table_number = table.table_number  # 设置固定的桌号
        # 不要让 table_number 通过表单提交，手动设置它
        form.instance.seat_type = table.seat_type  # 设置固定的桌号

        if form.is_valid():
            form.save()  # 保存表单数据
            return redirect('catering_dashboard')  # 跳转到餐饮管理页面
        else:
            # 打印表单错误
            print(form.errors)
    else:
        form = TableForm(instance=table)
    return render(request, 'edit_table.html', {'form': form, 'table': table,'base_template': base_template})
def cancel_seat(request, table_number):

    if request.method == 'POST':
        try:
            # 获取对应的表
            table = Table.objects.get(table_number=table_number)
            table.table_status = Room.VACANT  # 设置房间为“空房”
            table.customer_name = None  # 清空顾客姓名
            table.check_in_time = None  # 清空入住日期
            table.customer_phone = None
            table.check_out_time = None  # 清空离店日期
            table.save()  # 保存更新后的数据
            return JsonResponse({'success': True})
        except Table.DoesNotExist:
            return JsonResponse({'success': False, 'message': '餐桌未找到'})
@login_required
@role_required('manager','catering','admin')  # 只有角色为 housing 的用户才能访问
def dish(request):
    is_manager = request.user.is_staff  # 假设根据 `is_staff` 判断总经理身份
    base_template = 'manage_base.html' if is_manager else 'table_base.html'
    # 获取所有已入座的餐桌
    tables = Table.objects.filter(table_status='occupied')  # 只显示已入座的餐桌

    # 获取所有菜品
    dishes = Dish.objects.all()

    return render(request, 'dish.html', {
        'tables': tables,
        'dishes': dishes,'base_template': base_template
    })
@login_required
@role_required('manager','catering','admin')  # 只有角色为 housing 的用户才能访问
def delete_order_item(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            order_id = data.get('order_id')
            table_id = data.get('table_id')

            # 检查是否提供了有效的order_id和table_id
            if not order_id or not table_id:
                return JsonResponse({'success': False, 'message': '缺少订单ID或餐桌ID'})

            # 获取并删除对应的订单项
            order_item = Order.objects.filter(id=order_id, table_id=table_id).first()

            if not order_item:
                return JsonResponse({'success': False, 'message': '未找到该订单项'})

            order_item.delete()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})

    return JsonResponse({'success': False, 'message': '无效请求方法'})
@login_required
@role_required('manager','catering','admin')  # 只有角色为 housing 的用户才能访问
def add_to_order(request):

    is_manager = request.user.is_staff  # 假设根据 `is_staff` 判断总经理身份
    base_template = 'manage_base.html' if is_manager else 'table_base.html'
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            table_id = data.get('table_id')
            dish_id = data.get('dish_id')
            quantity = data.get('quantity', 1)  # 默认为1份

            # 确保传递了餐桌ID和菜品ID
            if not table_id or not dish_id:
                return JsonResponse({'success': False, 'message': '缺少参数'})

            try:
                table = Table.objects.get(id=table_id)
                dish = Dish.objects.get(id=dish_id)

                # 获取餐桌对应的顾客

                # 获取餐桌对应的顾客，确保只返回一个顾客
                customers = Customer.objects.filter(table=table)


                customer = customers.first()  # 获取唯一的顾客


                # 创建订单
                for _ in range(quantity):
                    Order.objects.create(
                        table=table,
                        customer=customer,
                        dish=dish,
                        quantity=1  # 每次创建一份订单
                    )

                return JsonResponse({'success': True})

            except Table.DoesNotExist:
                return JsonResponse({'success': False, 'message': '餐桌不存在'})
            except Dish.DoesNotExist:
                return JsonResponse({'success': False, 'message': '菜品不存在'})
            except Customer.DoesNotExist:
                return JsonResponse({'success': False, 'message': '顾客不存在'})

        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': '无效的JSON数据'})

    return JsonResponse({'success': False, 'message': '无效请求'})

@login_required
@role_required('manager','catering','admin')  # 只有角色为 housing 的用户才能访问
def get_order_summary(request):
    is_manager = request.user.is_staff  # 假设根据 `is_staff` 判断总经理身份
    base_template = 'manage_base.html' if is_manager else 'table_base.html'
    table_id = request.GET.get('table_id')

    if not table_id:
        return JsonResponse({'success': False, 'message': '缺少餐桌ID'})

    try:
        orders = Order.objects.filter(table_id=table_id)  # 获取餐桌的所有订单
        order_items = {}

        # 统计每种菜品的数量
        for order in orders:
            if order.dish.name in order_items:
                order_items[order.dish.name]['quantity'] += 1
            else:
                order_items[order.dish.name] = {
                    'order_id': order.id,
                    'dish_name': order.dish.name,
                    'price': order.dish.price,
                    'quantity': 1
                }

        return JsonResponse({
            'success': True,
            'order_items': list(order_items.values())  # 将菜品信息转为列表
        })

    except Order.DoesNotExist:
        return JsonResponse({'success': False, 'message': '未找到点餐记录'})

from collections import defaultdict

# 获取所有餐桌的账单
@login_required
@role_required('manager','catering','admin')  #
def bills_view(request):
    is_manager = request.user.is_staff  # 假设根据 `is_staff` 判断总经理身份
    base_template = 'manage_base.html' if is_manager else 'table_base.html'
    tables = Table.objects.all()
    bills = []

    # 遍历所有餐桌
    for table in tables:
        # 获取该餐桌的所有订单
        order_items = Order.objects.filter(table=table)
        total_amount = 0
        order_details = defaultdict(lambda: {'quantity': 0, 'price': 0, 'dish_name': ''})

        # 遍历订单，计算总金额并整理账单详情
        for item in order_items:
            dish = item.dish  # 获取菜品对象
            order_details[dish.id]['quantity'] += item.quantity
            order_details[dish.id]['price'] = dish.price  # 记录菜品价格
            order_details[dish.id]['dish_name'] = dish.name  # 记录菜品名称
            total_amount += dish.price * item.quantity  # 累加价格

        # 只有在有点餐时才返回账单
        if total_amount > 0:
            bills.append({
                'table_id': table.id,
                'table_number': table.table_number,
                'customer_name': table.customer_name or "未命名",
                'total_amount': round(total_amount, 2),  # 保证金额显示两位小数
                'order_items': [
                    {
                        'dish_name': details['dish_name'],
                        'quantity': details['quantity'],
                        'price': round(details['price'], 2)
                    }
                    for details in order_details.values()
                ]
            })
    # 返回账单页面
    return render(request, 'bill.html', {'bills': bills,'base_template': base_template})
def get_paid_bills(request):
        # 获取已结账的账单记录
        paid_bills = Bill.objects.filter(is_paid=True)
        print(f"已结账账单数量: {paid_bills.count()}")  # 打印已结账的账单数量
        if paid_bills.exists():
            return JsonResponse({'success': True, 'paid_bills': list(paid_bills.values())})
        else:
            return JsonResponse({'success': False, 'message': '没有已结账的账单'})

# 清空餐桌的订单
@login_required
@role_required('manager','catering','admin')
def clear_orders(request, table_number):
    is_manager = request.user.is_staff  # 假设根据 `is_staff` 判断总经理身份
    base_template = 'manage_base.html' if is_manager else 'table_base.html'
    if request.method == 'POST':
        try:
            print(f"Attempting to clear orders for table number: {table_number}")
            # 假设订单存储在 Order 模型中，并且每个订单都有一个 `table_number` 字段
            # 先查询餐桌，获取餐桌对象
            table = Table.objects.get(table_number=table_number)

            # 通过餐桌对象查询该餐桌的所有订单
            orders = Order.objects.filter(table=table)  # 假设 Table 模型有 'number' 字段
            if not orders.exists():
                return JsonResponse({'success': False, 'message': '没有找到该餐桌的订单'})
                # 计算总金额
            total_amount = sum([order.dish.price * order.quantity for order in orders])
            # 更新餐桌的离店时间
            table.check_out_time = timezone.now()  # 结账时的当前时间
            if orders.exists():
                # 格式化时间
                check_in_time_str = table.check_in_time.strftime(
                    "%Y年%m月%d日 %H:%M:%S") if table.check_in_time else "无入座时间"
                check_out_time_str = table.check_out_time.strftime(
                    "%Y年%m月%d日 %H:%M:%S") if table.check_out_time else "无离店时间"

                # 获取餐桌第一次点餐的时间（订单创建时间）
                first_order_time = orders.order_by('created_at').first().created_at
                # 结账时间（直接使用 timezone.now()）
                checkout_time = timezone.now()
                # 创建账单记录
                bill = Bill.objects.create(
                    table=table,
                    customer_name=table.customer_name,  # 顾客名
                    total_amount=round(total_amount, 2),  # 总金额
                    order_created_at=table.check_in_time,  # 第一次点餐时间
                    checkout_time= checkout_time,  # 结账时间
                    is_paid=True  # 设置账单为已结账
                )
                # 创建财务记录
                finance = Finance(
                    finance_type="就餐",  # 财务类型为就餐
                    responsible_person="y2",  # 当前管理员的名字
                    amount=round(total_amount, 2),  # 总金额
                    details=(
                                f"入座餐位: {table.table_number}\n"
                                f"顾客姓名: {table.customer_name}\n"
                                f"入座时间: {check_in_time_str}\n"
                                f"离店时间: {check_out_time_str}\n"
                            )
                )
                finance.save()
                orders.delete()  # 删除该餐桌的所有订单
                # 处理退房逻辑
                table.table_status = Room.VACANT  # 设置房间为“空房”
                table.customer_name = None  # 清空顾客姓名
                table.check_in_time = None  # 清空入住日期
                table.customer_phone = None
                table.check_out_time = None  # 清空离店日期
                table.save()
                return JsonResponse({'success': True})
            else:
                return JsonResponse({'success': False, 'message': '没有找到该餐桌的订单'})
        except Exception as e:
            print(f"Error occurred: {str(e)}")
            return JsonResponse({'success': False, 'message': str(e)})

    return JsonResponse({'success': False, 'message': '无效请求'})
@login_required
@role_required('manager','finance','admin')
def bill_list(request):
    is_manager = request.user.is_staff  # 假设根据 `is_staff` 判断总经理身份
    base_template = 'manage_base.html' if is_manager else 'finance_base.html'
    bills = Order.objects.all()  # 获取所有账单
    return render(request, 'bill_list.html', {'bills': bills,'base_template': base_template})
@login_required
@role_required('manager','finance','admin')
def finance_dashboard(request):
    is_manager = request.user.is_staff  # 假设根据 `is_staff` 判断总经理身份
    base_template = 'manage_base.html' if is_manager else 'finance_base.html'
    filter_type = request.GET.get('filter', 'all')  # 获取 filter 参数
    start_date = request.GET.get('start_date')  # 获取起始日期
    end_date = request.GET.get('end_date')  # 获取终止日期

    # 获取所有财务记录
    finances = Finance.objects.all()
    # 将 finance_type 从英文转换为中文
    for finance in finances:
        if finance.finance_type == 'housing':
            finance.finance_type = '住房'
        elif finance.finance_type == 'meal':
            finance.finance_type = '就餐'
    if filter_type == '住房':
        finances = Finance.objects.filter(finance_type='住房')
        # 根据日期筛选（在财务类型筛选后的结果中）
        if start_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
            finances = finances.filter(record_time__gte=start_date)
        if end_date:
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
            finances = finances.filter(record_time__lte=end_date)
    elif filter_type == '就餐':
        finances = Finance.objects.filter(finance_type='就餐')
        # 根据日期筛选（在财务类型筛选后的结果中）
        if start_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
            finances = finances.filter(record_time__gte=start_date)
        if end_date:
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
            finances = finances.filter(record_time__lte=end_date)
    else:
        finances = Finance.objects.all()  # 显示所有财务记录
        # 根据日期筛选（在财务类型筛选后的结果中）
        if start_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
            finances = finances.filter(record_time__gte=start_date)
        if end_date:
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
            finances = finances.filter(record_time__lte=end_date)

    return render(request, 'finance_dashboard.html', {'finances': finances, 'filter': filter_type,'base_template': base_template, 'start_date': start_date.strftime('%Y-%m-%d') if start_date else '',
        'end_date': end_date.strftime('%Y-%m-%d') if end_date else ''})
# 编辑财务记录
# 编辑财务记录
def archive_finances(request):
    # 创建一个工作簿对象
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "财务记录"

    # 设置表头
    headers = ["财务类型", "负责人", "详情", "消费金额（元）", "附加服务金额（元）", "总金额（元）", "更改时间"]
    ws.append(headers)

    # 获取所有财务记录
    finances = Finance.objects.all()

    # 填充财务记录数据
    for finance in finances:
        row = [
            finance.finance_type,  # 财务类型
            finance.responsible_person,  # 负责人
            finance.details,  # 详情
            finance.amount,  # 消费金额
            finance.additional_service_amount,  # 附加服务金额
            finance.total_amount,  # 总金额
            finance.record_time.strftime("%Y年%m月%d日 %H:%M:%S")  # 更改时间
        ]
        ws.append(row)

    # 设置文件响应
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=finance_records.xlsx'

    # 将工作簿写入响应
    wb.save(response)

    return response
@login_required
@role_required('manager','finance','admin')
def edit_finance(request):
    is_manager = request.user.is_staff  # 假设根据 `is_staff` 判断总经理身份
    base_template = 'manage_base.html' if is_manager else 'finance_base.html'
    if request.method == 'POST':
        finance_id = request.POST.get('id')
        extra = request.POST.get('extra')
        amount = request.POST.get('amount')
        details = request.POST.get('details')

        try:
            finance = Finance.objects.get(id=finance_id)
            # finance.finance_type = finance_type
            # finance.responsible_person = responsible_person
            # record_time = finance.record_time  # 获取记录时间
            # finance.record_time = record_time
            # 设置 record_time 为当前时间
            finance.record_time = timezone.now()
            finance.amount = amount
            finance.details = details
            finance.additional_service_amount = extra  # 更新附加服务费用
            # 计算并更新总金额
            finance.total_amount = float(amount) + float(extra)
            finance.save()

            return JsonResponse({'success': True, 'message': '财务记录更新成功'})

        except Finance.DoesNotExist:
            return JsonResponse({'success': False, 'message': '财务记录不存在'})
    else:
        return JsonResponse({'success': False, 'message': '无效请求'})
# 删除财务记录
# 删除财务记录
@login_required
@role_required('manager','finance','admin')
def delete_finance(request):
    is_manager = request.user.is_staff  # 假设根据 `is_staff` 判断总经理身份
    base_template = 'manage_base.html' if is_manager else 'finance_base.html'
    if request.method == 'POST':
        finance_id = request.POST.get('id')

        try:
            finance = Finance.objects.get(id=finance_id)
            finance.delete()

            return JsonResponse({'success': True, 'message': '财务记录已删除'})
        except Finance.DoesNotExist:
            return JsonResponse({'success': False, 'message': '财务记录不存在'})
    else:
        return JsonResponse({'success': False, 'message': '无效请求'})
@login_required
@role_required('manager','finance','admin')
def add_finance(request):
    is_manager = request.user.is_staff  # 假设根据 `is_staff` 判断总经理身份
    base_template = 'manage_base.html' if is_manager else 'finance_base.html'
    if request.method == 'POST':
        form = FinanceForm(request.POST)
        if form.is_valid():
            # 获取表单的财务类型
            finance_type = form.cleaned_data['finance_type']

            # 转换英文财务类型为中文
            if finance_type == 'housing':
                form.instance.finance_type = '住房'
            elif finance_type == 'meal':
                form.instance.finance_type = '就餐'

            form.save()  # 保存财务记录
            messages.success(request, "财务记录已成功添加！")
            return redirect('finance_dashboard')  # 跳转到相关页面，您可以调整为想要的页面
    else:
        form = FinanceForm()  # GET请求时展示空表单
    return render(request, 'add_finance.html', {'form': form,'base_template': base_template})

# 总经理页面视图
@login_required
@role_required('manager','admin')
def manager_dashboard(request):
    print(f"User authenticated: {request.user.is_authenticated}")
    print(f"User is staff: {request.user.is_staff}")
    if not request.user.is_authenticated:
        return redirect('login')  # 如果用户没有登录，重定向到登录页面
    # 检查用户是否是总经理身份，可以根据用户的权限或者角色来判断
    if request.user.is_staff:  # 假设总经理是管理员角色
        return render(request, 'manager_dashboard.html')
    else:
        return redirect('login')  # 如果不是总经理，重定向到登录页面
@login_required
@role_required('manager','inventory','admin')
def inventory_dashboard(request):
    is_manager = request.user.is_staff  # 假设根据 `is_staff` 判断总经理身份
    base_template = 'manage_base.html' if is_manager else 'inventory_base.html'
    tables = Table.objects.all()  # 假设有一个 Table 模型
    rooms = Room.objects.all()  # 假设有一个 Room 模型
    return render(request, 'inventory_dashboard.html',{'tables': tables, 'rooms': rooms,'base_template': base_template})  # 库存管理人员的主页模板
from django.views.decorators.csrf import csrf_exempt

# 添加餐桌
@login_required
@role_required('manager','inventory','admin')
def add_table1(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        table_number = data.get('table_number')
        # seats = data.get('seats')

        # 检查数据是否有效
        if table_number:
            try:
                new_table = Table.objects.create(table_number=table_number)
                return JsonResponse({'success': True, 'message': '餐桌添加成功'})
            except Exception as e:
                return JsonResponse({'success': False, 'message': '保存餐桌失败'})
        return JsonResponse({'success': False, 'message': '无效的数据'})


# 添加房间
@login_required
@role_required('manager','inventory','admin')
def add_room1(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        room_number = data.get('room_number')
        room_type = data.get('type')
        price = data.get('price')

        # 检查数据是否有效
        if room_number and price:
            try:
                new_room = Room.objects.create(room_number=room_number, price=price)
                return JsonResponse({'success': True, 'message': '房间添加成功'})
            except Exception as e:
                return JsonResponse({'success': False, 'message': '保存房间失败'})
        return JsonResponse({'success': False, 'message': '无效的数据'})
@login_required
@role_required('manager','inventory','admin')
def update_table(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)  # 解析请求体中的 JSON 数据
            table_number = data.get('table_number')
            seats = data.get('seats')
            # 确保房间号正确
            print(f"收到的房间号: {table_number}")
            # print(f"收到的房间类型: {room_type}")
            print(f"收到的房间价格: {seats}")
            table = Table.objects.get(table_number=table_number)
            table.table_number = table_number
            table.save()
            return JsonResponse({'success': True})
        except Table.DoesNotExist:
            return JsonResponse({'success': False})
        except Exception as e:
            return JsonResponse({'success': False})
    return JsonResponse({'success': False, 'message': '无效请求'})

# @csrf_exempt  # 仅在开发阶段使用，生产环境应启用 CSRF 保护
@login_required
@role_required('manager','inventory','admin')
def update_room(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)  # 解析请求体中的 JSON 数据
            room_number = data.get('room_number')
            # room_type = data.get('type')
            price = data.get('price')
            # 调试：打印接收到的房间号
            # 确保房间号正确
            print(f"收到的房间号: {room_number}")
            # print(f"收到的房间类型: {room_type}")
            print(f"收到的房间价格: {price}")
            # 查询房间
            room = Room.objects.get(room_number=room_number)

            # 更新房间信息
            # room.type = room_type
            room.price = price
            room.save()

            return JsonResponse({'success': True})
        except Room.DoesNotExist:
            return JsonResponse({'success': False, 'message': '房间不存在'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    return JsonResponse({'success': False, 'message': '无效请求'})
@login_required
@role_required('manager','inventory','admin')
def delete_table(request):
    if request.method == "POST":

        try:
            data = json.loads(request.body)  # 解析请求体中的 JSON 数据
            table_number = data.get('table_number')
            print(f"删除时收到的房间号: {table_number}")
            table = Table.objects.get(table_number=table_number)
            table.delete()  # 删除餐桌
            return JsonResponse({'success': True})
        except Table.DoesNotExist:
            return JsonResponse({'success': False, 'message': '餐桌未找到'})
@login_required
@role_required('manager','inventory','admin')
def delete_room(request):
    if request.method == "POST":
        # room_number = request.POST.get('room_number')
        # 调试：打印接收到的 room_number

        try:
            data = json.loads(request.body)  # 解析请求体中的 JSON 数据
            room_number = data.get('room_number')
            print(f"删除时收到的房间号: {room_number}")
            room = Room.objects.get(room_number=room_number)
            room.delete()  # 删除房间
            return JsonResponse({'success': True})
        except Room.DoesNotExist:
            return JsonResponse({'success': False, 'message': '房间未找到'})