from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Category, Book, BorrowRecord, Reservation, RenewRecord, FineRecord, OperationLog, SystemConfig
from datetime import timedelta
from django.utils import timezone
from django.db.models import F
from django.conf import settings

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    role_display = serializers.CharField(source='get_role_display', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role', 'role_display', 'phone', 'address', 'date_joined', 'is_active', 'created_at']
        read_only_fields = ['id', 'date_joined', 'created_at']


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)
    confirm_password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'confirm_password', 'first_name', 'last_name', 'phone', 'address']

    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError({'password': '两次输入的密码不一致'})
        return attrs

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        user = User.objects.create_user(**validated_data)
        return user


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True, min_length=6)
    new_password = serializers.CharField(write_only=True, min_length=6)
    confirm_password = serializers.CharField(write_only=True, min_length=6)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError({'confirm_password': '两次输入的新密码不一致'})
        return attrs


class CategorySerializer(serializers.ModelSerializer):
    book_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'book_count', 'created_at']
        read_only_fields = ['id', 'created_at']


class BookSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    borrow_count_display = serializers.IntegerField(source='borrow_count', read_only=True)

    class Meta:
        model = Book
        fields = ['id', 'isbn', 'title', 'author', 'publisher', 'publish_date', 'category', 'category_name',
                  'description', 'location', 'total_quantity', 'available_quantity', 'status', 'status_display',
                  'cover_image', 'borrow_count', 'borrow_count_display', 'reservation_count', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at', 'borrow_count', 'reservation_count']


class BookListSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    can_reserve = serializers.SerializerMethodField()
    can_borrow = serializers.SerializerMethodField()

    class Meta:
        model = Book
        fields = ['id', 'isbn', 'title', 'author', 'publisher', 'category_name', 'available_quantity', 'status',
                  'status_display', 'cover_image', 'borrow_count', 'can_reserve', 'can_borrow']

    def get_can_reserve(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated or request.user.role != 'reader':
            return False
        max_reservation = int(settings.LIBRARY_CONFIG.get('MAX_RESERVATION_COUNT', 3))
        user_reservations = Reservation.objects.filter(
            reader=request.user,
            status__in=['pending', 'available']
        ).count()
        if user_reservations >= max_reservation:
            return False
        existing = Reservation.objects.filter(
            reader=request.user,
            book=obj,
            status__in=['pending', 'available']
        ).exists()
        return not existing

    def get_can_borrow(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated or request.user.role != 'reader':
            return False
        if obj.available_quantity <= 0:
            return False
        max_borrow = int(settings.LIBRARY_CONFIG.get('MAX_BORROW_COUNT', 5))
        user_borrows = BorrowRecord.objects.filter(
            reader=request.user,
            status__in=['borrowed', 'overdue']
        ).count()
        if user_borrows >= max_borrow:
            return False
        existing = BorrowRecord.objects.filter(
            reader=request.user,
            book=obj,
            status__in=['borrowed', 'overdue']
        ).exists()
        return not existing


class BorrowRecordSerializer(serializers.ModelSerializer):
    reader_name = serializers.CharField(source='reader.username', read_only=True)
    reader_display = serializers.SerializerMethodField()
    book_title = serializers.CharField(source='book.title', read_only=True)
    book_isbn = serializers.CharField(source='book.isbn', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    overdue_days = serializers.SerializerMethodField()
    can_renew = serializers.SerializerMethodField()
    has_pending_renew = serializers.SerializerMethodField()

    class Meta:
        model = BorrowRecord
        fields = ['id', 'reader', 'reader_name', 'reader_display', 'book', 'book_title', 'book_isbn',
                  'borrow_date', 'due_date', 'return_date', 'status', 'status_display', 'fine_amount',
                  'fine_paid', 'fine_paid_at', 'renew_count', 'max_renew_count', 'overdue_days',
                  'can_renew', 'has_pending_renew', 'remarks', 'created_at', 'updated_at']
        read_only_fields = ['id', 'borrow_date', 'created_at', 'updated_at']

    def get_reader_display(self, obj):
        return f'{obj.reader.first_name}{obj.reader.last_name} ({obj.reader.username})'

    def get_overdue_days(self, obj):
        return obj.get_overdue_days()

    def get_can_renew(self, obj):
        if obj.status not in ['borrowed', 'overdue']:
            return False
        if obj.renew_count >= obj.max_renew_count:
            return False
        if obj.fine_paid is False and obj.fine_amount > 0:
            return False
        request = self.context.get('request')
        if request and request.user.role == 'reader' and request.user != obj.reader:
            return False
        return True

    def get_has_pending_renew(self, obj):
        return RenewRecord.objects.filter(
            borrow_record=obj,
            status='pending'
        ).exists()


class BorrowBookSerializer(serializers.Serializer):
    book_id = serializers.IntegerField()
    reader_id = serializers.IntegerField()
    borrow_days = serializers.IntegerField(default=30, min_value=1, max_value=90)

    def validate(self, attrs):
        book = Book.objects.filter(id=attrs['book_id']).first()
        if not book:
            raise serializers.ValidationError({'book_id': '图书不存在'})
        if book.available_quantity <= 0:
            raise serializers.ValidationError({'book_id': '该书已无库存'})

        reader = User.objects.filter(id=attrs['reader_id']).first()
        if not reader or reader.role != 'reader':
            raise serializers.ValidationError({'reader_id': '读者不存在或不是读者角色'})

        active_borrows = BorrowRecord.objects.filter(
            reader=reader,
            book=book,
            status__in=['borrowed', 'overdue']
        ).exists()
        if active_borrows:
            raise serializers.ValidationError({'book_id': '该读者已借阅该书，尚未归还'})

        max_borrow = int(settings.LIBRARY_CONFIG.get('MAX_BORROW_COUNT', 5))
        user_borrows = BorrowRecord.objects.filter(
            reader=reader,
            status__in=['borrowed', 'overdue']
        ).count()
        if user_borrows >= max_borrow:
            raise serializers.ValidationError({'reader_id': f'该读者已达到最大借阅数量({max_borrow}本)'})

        return attrs

    def create(self, validated_data):
        book = Book.objects.get(id=validated_data['book_id'])
        reader = User.objects.get(id=validated_data['reader_id'])

        borrow_date = timezone.now()
        due_date = borrow_date + timedelta(days=validated_data['borrow_days'])

        borrow_record = BorrowRecord.objects.create(
            reader=reader,
            book=book,
            borrow_date=borrow_date,
            due_date=due_date,
            status='borrowed',
            max_renew_count=int(settings.LIBRARY_CONFIG.get('MAX_RENEW_COUNT', 2))
        )

        book.available_quantity = F('available_quantity') - 1
        book.borrow_count = F('borrow_count') + 1
        book.save()
        book.refresh_from_db()
        book.update_status()

        reservations = Reservation.objects.filter(
            book=book,
            status='available',
            reader=reader
        )
        for reservation in reservations:
            reservation.status = 'completed'
            reservation.borrow_record = borrow_record
            reservation.save()
            book.reservation_count = F('reservation_count') - 1
            book.save()

        return borrow_record


class ReturnBookSerializer(serializers.Serializer):
    record_id = serializers.IntegerField()

    def update(self, instance, validated_data):
        instance.return_date = timezone.now()
        instance.status = 'returned'

        if instance.return_date > instance.due_date:
            days_overdue = (instance.return_date - instance.due_date).days
            fine_per_day = float(settings.LIBRARY_CONFIG.get('FINE_PER_DAY', 0.5))
            instance.fine_amount = days_overdue * fine_per_day

            if instance.fine_amount > 0:
                FineRecord.objects.create(
                    reader=instance.reader,
                    borrow_record=instance,
                    book=instance.book,
                    fine_type='overdue',
                    amount=instance.fine_amount,
                    days_overdue=days_overdue,
                    status='unpaid'
                )

        instance.save()

        book = instance.book
        book.available_quantity = F('available_quantity') + 1
        book.save()
        book.refresh_from_db()
        book.update_status()

        return instance


class ReservationSerializer(serializers.ModelSerializer):
    reader_name = serializers.CharField(source='reader.username', read_only=True)
    reader_display = serializers.SerializerMethodField()
    book_title = serializers.CharField(source='book.title', read_only=True)
    book_isbn = serializers.CharField(source='book.isbn', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Reservation
        fields = ['id', 'reader', 'reader_name', 'reader_display', 'book', 'book_title', 'book_isbn',
                  'queue_position', 'status', 'status_display', 'reservation_date', 'available_notify_date',
                  'expire_date', 'remarks', 'created_at', 'updated_at']
        read_only_fields = ['id', 'queue_position', 'status', 'reservation_date', 'created_at', 'updated_at']

    def get_reader_display(self, obj):
        return f'{obj.reader.first_name}{obj.reader.last_name} ({obj.reader.username})'


class CreateReservationSerializer(serializers.Serializer):
    book_id = serializers.IntegerField()

    def validate(self, attrs):
        request = self.context.get('request')
        reader = request.user

        book = Book.objects.filter(id=attrs['book_id']).first()
        if not book:
            raise serializers.ValidationError({'book_id': '图书不存在'})

        existing = Reservation.objects.filter(
            reader=reader,
            book=book,
            status__in=['pending', 'available']
        ).exists()
        if existing:
            raise serializers.ValidationError({'book_id': '您已预约该书'})

        max_reservation = int(settings.LIBRARY_CONFIG.get('MAX_RESERVATION_COUNT', 3))
        user_reservations = Reservation.objects.filter(
            reader=reader,
            status__in=['pending', 'available']
        ).count()
        if user_reservations >= max_reservation:
            raise serializers.ValidationError({'book_id': f'您已达到最大预约数量({max_reservation}本)'})

        return attrs

    def create(self, validated_data):
        request = self.context.get('request')
        reader = request.user
        book = Book.objects.get(id=validated_data['book_id'])

        queue_position = Reservation.objects.filter(
            book=book,
            status__in=['pending', 'available']
        ).count() + 1

        expire_days = int(settings.LIBRARY_CONFIG.get('RESERVATION_EXPIRE_DAYS', 3))
        expire_date = timezone.now() + timedelta(days=expire_days)

        reservation = Reservation.objects.create(
            reader=reader,
            book=book,
            queue_position=queue_position,
            status='pending',
            expire_date=expire_date
        )

        book.reservation_count = F('reservation_count') + 1
        book.save()
        book.refresh_from_db()
        book.update_status()

        return reservation


class RenewRecordSerializer(serializers.ModelSerializer):
    reader_name = serializers.CharField(source='reader.username', read_only=True)
    reader_display = serializers.SerializerMethodField()
    book_title = serializers.CharField(source='book.title', read_only=True)
    book_isbn = serializers.CharField(source='book.isbn', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    reviewer_name = serializers.CharField(source='reviewer.username', read_only=True, allow_null=True)

    class Meta:
        model = RenewRecord
        fields = ['id', 'borrow_record', 'reader', 'reader_name', 'reader_display', 'book', 'book_title',
                  'book_isbn', 'request_date', 'renew_days', 'original_due_date', 'new_due_date', 'status',
                  'status_display', 'reviewer', 'reviewer_name', 'review_date', 'review_remark',
                  'created_at', 'updated_at']
        read_only_fields = ['id', 'request_date', 'original_due_date', 'status', 'created_at', 'updated_at']

    def get_reader_display(self, obj):
        return f'{obj.reader.first_name}{obj.reader.last_name} ({obj.reader.username})'


class CreateRenewSerializer(serializers.Serializer):
    borrow_record_id = serializers.IntegerField()
    renew_days = serializers.IntegerField(default=30, min_value=1, max_value=90)

    def validate(self, attrs):
        request = self.context.get('request')
        borrow_record = BorrowRecord.objects.filter(id=attrs['borrow_record_id']).first()

        if not borrow_record:
            raise serializers.ValidationError({'borrow_record_id': '借阅记录不存在'})

        if request.user.role == 'reader' and borrow_record.reader != request.user:
            raise serializers.ValidationError({'borrow_record_id': '无权限续借他人的图书'})

        if borrow_record.status not in ['borrowed', 'overdue']:
            raise serializers.ValidationError({'borrow_record_id': '该借阅记录状态不允许续借'})

        if borrow_record.renew_count >= borrow_record.max_renew_count:
            raise serializers.ValidationError({'borrow_record_id': '已达到最大续借次数'})

        if borrow_record.fine_paid is False and borrow_record.fine_amount > 0:
            raise serializers.ValidationError({'borrow_record_id': '请先缴纳逾期罚款后再续借'})

        pending = RenewRecord.objects.filter(
            borrow_record=borrow_record,
            status='pending'
        ).exists()
        if pending:
            raise serializers.ValidationError({'borrow_record_id': '该借阅记录已有待审核的续借申请'})

        return attrs

    def create(self, validated_data):
        request = self.context.get('request')
        borrow_record = BorrowRecord.objects.get(id=validated_data['borrow_record_id'])

        renew_record = RenewRecord.objects.create(
            borrow_record=borrow_record,
            reader=borrow_record.reader,
            book=borrow_record.book,
            renew_days=validated_data['renew_days'],
            original_due_date=borrow_record.due_date,
            status='pending'
        )

        return renew_record


class ReviewRenewSerializer(serializers.Serializer):
    renew_id = serializers.IntegerField()
    approved = serializers.BooleanField()
    review_remark = serializers.CharField(required=False, allow_blank=True)

    def validate(self, attrs):
        renew = RenewRecord.objects.filter(id=attrs['renew_id']).first()
        if not renew:
            raise serializers.ValidationError({'renew_id': '续借记录不存在'})
        if renew.status != 'pending':
            raise serializers.ValidationError({'renew_id': '该续借申请已审核'})
        return attrs

    def update(self, instance, validated_data):
        request = self.context.get('request')
        instance.status = 'approved' if validated_data['approved'] else 'rejected'
        instance.reviewer = request.user
        instance.review_date = timezone.now()
        instance.review_remark = validated_data.get('review_remark', '')

        if validated_data['approved']:
            borrow_record = instance.borrow_record
            new_due_date = borrow_record.due_date + timedelta(days=instance.renew_days)
            borrow_record.due_date = new_due_date
            borrow_record.renew_count += 1
            borrow_record.status = 'borrowed'
            borrow_record.save()

            instance.new_due_date = new_due_date

        instance.save()
        return instance


class FineRecordSerializer(serializers.ModelSerializer):
    reader_name = serializers.CharField(source='reader.username', read_only=True)
    reader_display = serializers.SerializerMethodField()
    book_title = serializers.CharField(source='book.title', read_only=True)
    book_isbn = serializers.CharField(source='book.isbn', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    payment_method_display = serializers.CharField(source='get_payment_method_display', read_only=True, allow_null=True)
    paid_by_name = serializers.CharField(source='paid_by.username', read_only=True, allow_null=True)

    class Meta:
        model = FineRecord
        fields = ['id', 'reader', 'reader_name', 'reader_display', 'borrow_record', 'book', 'book_title',
                  'book_isbn', 'fine_type', 'amount', 'days_overdue', 'status', 'status_display',
                  'payment_method', 'payment_method_display', 'paid_date', 'paid_by', 'paid_by_name',
                  'waiver_reason', 'remarks', 'created_at', 'updated_at']
        read_only_fields = ['id', 'fine_type', 'amount', 'days_overdue', 'created_at', 'updated_at']

    def get_reader_display(self, obj):
        return f'{obj.reader.first_name}{obj.reader.last_name} ({obj.reader.username})'


class PayFineSerializer(serializers.Serializer):
    fine_id = serializers.IntegerField()
    payment_method = serializers.ChoiceField(choices=['cash', 'alipay', 'wechat', 'card', 'transfer'])
    remarks = serializers.CharField(required=False, allow_blank=True)

    def validate(self, attrs):
        fine = FineRecord.objects.filter(id=attrs['fine_id']).first()
        if not fine:
            raise serializers.ValidationError({'fine_id': '罚款记录不存在'})
        if fine.status != 'unpaid':
            raise serializers.ValidationError({'fine_id': '该罚款已处理'})
        return attrs

    def update(self, instance, validated_data):
        request = self.context.get('request')
        instance.status = 'paid'
        instance.payment_method = validated_data['payment_method']
        instance.paid_date = timezone.now()
        instance.paid_by = request.user
        instance.remarks = validated_data.get('remarks', '')
        instance.save()

        borrow_record = instance.borrow_record
        borrow_record.fine_paid = True
        borrow_record.fine_paid_at = timezone.now()
        borrow_record.save()

        return instance


class OperationLogSerializer(serializers.ModelSerializer):
    operator_name = serializers.CharField(source='operator.username', read_only=True, allow_null=True)
    operation_type_display = serializers.CharField(source='get_operation_type_display', read_only=True)

    class Meta:
        model = OperationLog
        fields = ['id', 'operator', 'operator_name', 'operation_type', 'operation_type_display',
                  'target_model', 'target_id', 'target_name', 'description', 'ip_address', 'created_at']
        read_only_fields = ['id', 'created_at']


class SystemConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemConfig
        fields = ['id', 'key', 'value', 'description', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
