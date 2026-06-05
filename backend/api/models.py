from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


class User(AbstractUser):
    ROLE_CHOICES = (
        ('super_admin', '超级管理员'),
        ('admin', '普通管理员'),
        ('reader', '读者'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='reader')
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = '用户'
        verbose_name_plural = '用户'

    def __str__(self):
        return self.username

    def is_super_admin(self):
        return self.role == 'super_admin'

    def is_admin_role(self):
        return self.role in ['super_admin', 'admin']


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name='分类名称')
    description = models.TextField(blank=True, null=True, verbose_name='分类描述')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '图书分类'
        verbose_name_plural = '图书分类'

    def __str__(self):
        return self.name


class Book(models.Model):
    STATUS_CHOICES = (
        ('available', '可借阅'),
        ('borrowed', '已借出'),
        ('reserved', '已预约'),
        ('lost', '已遗失'),
    )
    isbn = models.CharField(max_length=20, unique=True, verbose_name='ISBN')
    title = models.CharField(max_length=200, verbose_name='书名')
    author = models.CharField(max_length=100, verbose_name='作者')
    publisher = models.CharField(max_length=100, verbose_name='出版社')
    publish_date = models.DateField(verbose_name='出版日期')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='books', verbose_name='分类')
    description = models.TextField(verbose_name='内容简介')
    location = models.CharField(max_length=100, verbose_name='馆藏位置')
    total_quantity = models.IntegerField(default=1, verbose_name='总数量')
    available_quantity = models.IntegerField(default=1, verbose_name='可借数量')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available', verbose_name='状态')
    cover_image = models.ImageField(upload_to='book_covers/', blank=True, null=True, verbose_name='封面图片')
    borrow_count = models.IntegerField(default=0, verbose_name='借阅次数')
    reservation_count = models.IntegerField(default=0, verbose_name='预约次数')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '图书'
        verbose_name_plural = '图书'
        ordering = ['-borrow_count', '-created_at']

    def __str__(self):
        return self.title

    def update_status(self):
        if self.available_quantity > 0:
            self.status = 'available'
        elif self.reservation_count > 0:
            self.status = 'reserved'
        else:
            self.status = 'borrowed'
        self.save()


class BorrowRecord(models.Model):
    STATUS_CHOICES = (
        ('borrowed', '借阅中'),
        ('returned', '已归还'),
        ('overdue', '已逾期'),
        ('lost', '已遗失'),
    )
    reader = models.ForeignKey(User, on_delete=models.CASCADE, related_name='borrow_records', verbose_name='读者')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='borrow_records', verbose_name='图书')
    borrow_date = models.DateTimeField(default=timezone.now, verbose_name='借阅日期')
    due_date = models.DateTimeField(verbose_name='应还日期')
    return_date = models.DateTimeField(blank=True, null=True, verbose_name='归还日期')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='borrowed', verbose_name='状态')
    fine_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='罚款金额')
    fine_paid = models.BooleanField(default=False, verbose_name='罚款已缴')
    fine_paid_at = models.DateTimeField(blank=True, null=True, verbose_name='罚款缴纳时间')
    renew_count = models.IntegerField(default=0, verbose_name='续借次数')
    max_renew_count = models.IntegerField(default=2, verbose_name='最大续借次数')
    remarks = models.TextField(blank=True, null=True, verbose_name='备注')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '借阅记录'
        verbose_name_plural = '借阅记录'
        ordering = ['-borrow_date']

    def __str__(self):
        return f'{self.reader.username} - {self.book.title}'

    def calculate_fine(self):
        if self.return_date and self.return_date > self.due_date:
            days_overdue = (self.return_date - self.due_date).days
        elif not self.return_date and timezone.now() > self.due_date:
            days_overdue = (timezone.now() - self.due_date).days
        else:
            days_overdue = 0
        return days_overdue * 0.5

    def get_overdue_days(self):
        if self.status in ['borrowed', 'overdue']:
            now = timezone.now()
            if now > self.due_date:
                return (now - self.due_date).days
        return 0


class Reservation(models.Model):
    STATUS_CHOICES = (
        ('pending', '等待中'),
        ('available', '可借阅'),
        ('completed', '已完成'),
        ('expired', '已过期'),
        ('cancelled', '已取消'),
    )
    reader = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reservations', verbose_name='读者')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='reservations', verbose_name='图书')
    queue_position = models.IntegerField(default=1, verbose_name='排队位置')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='状态')
    reservation_date = models.DateTimeField(default=timezone.now, verbose_name='预约日期')
    available_notify_date = models.DateTimeField(blank=True, null=True, verbose_name='可借通知日期')
    expire_date = models.DateTimeField(verbose_name='过期日期')
    borrow_record = models.OneToOneField(
        BorrowRecord,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='reservation',
        verbose_name='关联借阅记录'
    )
    remarks = models.TextField(blank=True, null=True, verbose_name='备注')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '预约记录'
        verbose_name_plural = '预约记录'
        ordering = ['-reservation_date']

    def __str__(self):
        return f'{self.reader.username} - {self.book.title}'


class RenewRecord(models.Model):
    STATUS_CHOICES = (
        ('pending', '待审核'),
        ('approved', '已通过'),
        ('rejected', '已拒绝'),
    )
    borrow_record = models.ForeignKey(BorrowRecord, on_delete=models.CASCADE, related_name='renew_records', verbose_name='借阅记录')
    reader = models.ForeignKey(User, on_delete=models.CASCADE, related_name='renew_records', verbose_name='读者')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='renew_records', verbose_name='图书')
    request_date = models.DateTimeField(default=timezone.now, verbose_name='申请日期')
    renew_days = models.IntegerField(default=30, verbose_name='续借天数')
    original_due_date = models.DateTimeField(verbose_name='原应还日期')
    new_due_date = models.DateTimeField(blank=True, null=True, verbose_name='新应还日期')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='状态')
    reviewer = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='reviewed_renews',
        verbose_name='审核人'
    )
    review_date = models.DateTimeField(blank=True, null=True, verbose_name='审核日期')
    review_remark = models.TextField(blank=True, null=True, verbose_name='审核备注')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '续借记录'
        verbose_name_plural = '续借记录'
        ordering = ['-request_date']

    def __str__(self):
        return f'{self.reader.username} - {self.book.title} 续借申请'


class FineRecord(models.Model):
    STATUS_CHOICES = (
        ('unpaid', '未缴纳'),
        ('paid', '已缴纳'),
        ('waived', '已减免'),
    )
    PAYMENT_METHOD_CHOICES = (
        ('cash', '现金'),
        ('alipay', '支付宝'),
        ('wechat', '微信支付'),
        ('card', '刷卡'),
        ('transfer', '转账'),
    )
    reader = models.ForeignKey(User, on_delete=models.CASCADE, related_name='fine_records', verbose_name='读者')
    borrow_record = models.ForeignKey(BorrowRecord, on_delete=models.CASCADE, related_name='fine_records', verbose_name='借阅记录')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='fine_records', verbose_name='图书')
    fine_type = models.CharField(max_length=50, default='overdue', verbose_name='罚款类型')
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='罚款金额')
    days_overdue = models.IntegerField(default=0, verbose_name='逾期天数')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='unpaid', verbose_name='状态')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, blank=True, null=True, verbose_name='支付方式')
    paid_date = models.DateTimeField(blank=True, null=True, verbose_name='缴纳日期')
    paid_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='processed_fines',
        verbose_name='处理人'
    )
    waiver_reason = models.TextField(blank=True, null=True, verbose_name='减免原因')
    remarks = models.TextField(blank=True, null=True, verbose_name='备注')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '罚金记录'
        verbose_name_plural = '罚金记录'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.reader.username} - ¥{self.amount}'


class OperationLog(models.Model):
    OPERATION_TYPE_CHOICES = (
        ('create', '创建'),
        ('update', '更新'),
        ('delete', '删除'),
        ('borrow', '借书'),
        ('return', '还书'),
        ('renew', '续借'),
        ('reserve', '预约'),
        ('fine', '罚款'),
        ('login', '登录'),
        ('logout', '退出'),
        ('import', '导入'),
        ('export', '导出'),
        ('other', '其他'),
    )
    operator = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name='operation_logs', verbose_name='操作人')
    operation_type = models.CharField(max_length=50, choices=OPERATION_TYPE_CHOICES, verbose_name='操作类型')
    target_model = models.CharField(max_length=100, blank=True, null=True, verbose_name='目标模型')
    target_id = models.IntegerField(blank=True, null=True, verbose_name='目标ID')
    target_name = models.CharField(max_length=200, blank=True, null=True, verbose_name='目标名称')
    description = models.TextField(verbose_name='操作描述')
    ip_address = models.CharField(max_length=50, blank=True, null=True, verbose_name='IP地址')
    user_agent = models.TextField(blank=True, null=True, verbose_name='用户代理')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='操作时间')

    class Meta:
        verbose_name = '操作日志'
        verbose_name_plural = '操作日志'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.operator} - {self.operation_type} - {self.created_at}'


class SystemConfig(models.Model):
    key = models.CharField(max_length=100, unique=True, verbose_name='配置键')
    value = models.TextField(verbose_name='配置值')
    description = models.TextField(blank=True, null=True, verbose_name='配置描述')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '系统配置'
        verbose_name_plural = '系统配置'

    def __str__(self):
        return f'{self.key}: {self.value}'
