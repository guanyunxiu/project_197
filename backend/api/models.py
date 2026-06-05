from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', '管理员'),
        ('reader', '读者'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='reader')
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)

    def __str__(self):
        return self.username


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
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '图书'
        verbose_name_plural = '图书'

    def __str__(self):
        return self.title


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
    remarks = models.TextField(blank=True, null=True, verbose_name='备注')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '借阅记录'
        verbose_name_plural = '借阅记录'

    def __str__(self):
        return f'{self.reader.username} - {self.book.title}'
