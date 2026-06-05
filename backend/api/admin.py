from django.contrib import admin
from .models import User, Category, Book, BorrowRecord

admin.site.register(User)
admin.site.register(Category)
admin.site.register(Book)
admin.site.register(BorrowRecord)
