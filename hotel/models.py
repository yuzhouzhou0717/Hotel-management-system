from decimal import Decimal

from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', '系统管理员'),
        ('finance', '账务管理人员'),
        ('housing', '住房管理人员'),
        ('catering', '餐饮管理人员'),
        ('inventory', '库存管理人员'),
        ('manager', '总经理'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='manager')

    def __str__(self):
        return self.username


class Room(models.Model):
    VACANT = 'vacant'
    OCCUPIED = 'occupied'
    STATUS_CHOICES = [
        (VACANT, '空房'),
        (OCCUPIED, '已入住'),
        ('cleaning', '清洁中'),
        ('maintenance', '待维修'),
    ]

    name = models.CharField(null=True,blank=True,max_length=100)
    id_card = models.CharField(null=True,blank=True,max_length=18)
    phone_number = models.CharField(null=True,blank=True,max_length=15)
    check_in_date = models.DateField(null=True, blank=True)
    check_out_date = models.DateField(null=True, blank=True)
    room_number = models.CharField(max_length=10)
    status = models.CharField(max_length=100, choices=STATUS_CHOICES, default=VACANT)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # 价格字段
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # 用户支付金额

    def __str__(self):
        return f"Room {self.room_number} ({self.name})"

class Table(models.Model):
    SEAT_TYPE_CHOICES = [
        ('hall', '大厅'), ('box', '包厢')
    ]
    VACANT = 'vacant'
    OCCUPIED = 'occupied'
    STATUS_CHOICES = [
        (VACANT, '空闲'),
        (OCCUPIED, '已占用'),
    ]
    seat_type = models.CharField(max_length=10, choices=SEAT_TYPE_CHOICES)  # 座位类型
    table_number = models.CharField(max_length=10, unique=True)  # 餐位编号
    table_status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=VACANT)
    customer_name = models.CharField(max_length=100, blank=True, null=True)  # 顾客姓名
    customer_phone = models.CharField(null=True,blank=True,max_length=15)
    check_in_time = models.DateTimeField(null=True, blank=True)  # 入座时间
    check_out_time = models.DateTimeField(null=True, blank=True)  # 新增字段
    def __str__(self):
        return f"Table {self.table_number}"
from django.db.models import Q

class Customer(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)  # 添加手机号字段
    check_in_time = models.DateField(null=True, blank=True)
    table = models.ForeignKey(Table, on_delete=models.SET_NULL, null=True)
    check_out_time = models.DateField(null=True, blank=True)


    def __str__(self):
        return f"{self.name} - {self.phone}"
class Dish(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name

class Order(models.Model):
    table = models.ForeignKey('Table', on_delete=models.CASCADE)  # 关联餐桌
    customer = models.ForeignKey('Customer', on_delete=models.CASCADE)  # 关联顾客
    dish = models.ForeignKey('Dish', on_delete=models.CASCADE)  # 关联菜品
    quantity = models.PositiveIntegerField(default=1)  # 菜品数量
    created_at = models.DateTimeField(auto_now_add=True)  # 记录创建时间

    def __str__(self):
        return f"Order for {self.customer.name} at Table {self.table.table_number}"
# 账单模型
# 账单模型
class Bill(models.Model):
    table = models.ForeignKey(Table, on_delete=models.CASCADE)  # 关联餐桌
    customer_name = models.CharField(max_length=100)  # 顾客姓名
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)  # 总金额
    is_paid = models.BooleanField(default=False)  # 是否结账
    order_created_at = models.DateTimeField(auto_now_add=True)  # 订单创建时间
    checkout_time = models.DateTimeField(null=True, blank=True)  # 结账时间，允许为空

    def __str__(self):
        return f"Bill for Table {self.table.table_number} - {'Paid' if self.is_paid else 'Unpaid'}"
class Finance(models.Model):
    FINANCE_CHOICES = [
        ('housing', '住房'),
        ('meal', '就餐'),
    ]

    finance_type = models.CharField(null=True, blank=True,max_length=10, choices=FINANCE_CHOICES)
    responsible_person = models.CharField(null=True, blank=True,max_length=100)  # 负责人
    details = models.TextField()  # 住房或就餐信息
    amount = models.DecimalField(max_digits=10, decimal_places=2)  # 价钱
    additional_service_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # 附加服务费用
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, editable=False, default=0)  # 总金额
    # 新增字段：记录时间
    record_time = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # 确保amount和additional_service_amount是Decimal类型
        self.amount = Decimal(self.amount)
        self.additional_service_amount = Decimal(self.additional_service_amount)

        # 计算总金额
        self.total_amount = self.amount + self.additional_service_amount
        super().save(*args, **kwargs)
    def __str__(self):
        return f"{self.finance_type} - {self.responsible_person} - {self.amount}"


