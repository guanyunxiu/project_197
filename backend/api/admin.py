from django.contrib import admin
from .models import User, Category, Book, BorrowRecord, Reservation, RenewRecord, FineRecord, OperationLog, SystemConfig

admin.site.register(User)
admin.site.register(Category)
admin.site.register(Book)
admin.site.register(BorrowRecord)
admin.site.register(Reservation)
admin.site.register(RenewRecord)
admin.site.register(FineRecord)
admin.site.register(OperationLog)
admin.site.register(SystemConfig)
