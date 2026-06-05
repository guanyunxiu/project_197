from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Category, Book, BorrowRecord
from datetime import timedelta

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role', 'phone', 'address', 'date_joined']
        read_only_fields = ['id', 'date_joined']


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


class CategorySerializer(serializers.ModelSerializer):
    book_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'book_count', 'created_at']
        read_only_fields = ['id', 'created_at']


class BookSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Book
        fields = ['id', 'isbn', 'title', 'author', 'publisher', 'publish_date', 'category', 'category_name',
                  'description', 'location', 'total_quantity', 'available_quantity', 'status', 'cover_image',
                  'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class BookListSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = Book
        fields = ['id', 'isbn', 'title', 'author', 'publisher', 'category_name', 'available_quantity', 'status', 'cover_image']


class BorrowRecordSerializer(serializers.ModelSerializer):
    reader_name = serializers.CharField(source='reader.username', read_only=True)
    book_title = serializers.CharField(source='book.title', read_only=True)
    book_isbn = serializers.CharField(source='book.isbn', read_only=True)

    class Meta:
        model = BorrowRecord
        fields = ['id', 'reader', 'reader_name', 'book', 'book_title', 'book_isbn', 'borrow_date', 'due_date',
                  'return_date', 'status', 'fine_amount', 'fine_paid', 'remarks', 'created_at']
        read_only_fields = ['id', 'borrow_date', 'created_at']


class BorrowBookSerializer(serializers.Serializer):
    book_id = serializers.IntegerField()
    reader_id = serializers.IntegerField()
    borrow_days = serializers.IntegerField(default=30, min_value=1, max_value=90)

    def create(self, validated_data):
        from .models import BorrowRecord
        from django.utils import timezone

        book = Book.objects.get(id=validated_data['book_id'])
        reader = User.objects.get(id=validated_data['reader_id'])

        if book.available_quantity <= 0:
            raise serializers.ValidationError({'book_id': '该书已无库存'})

        active_borrows = BorrowRecord.objects.filter(
            reader=reader,
            book=book,
            status__in=['borrowed', 'overdue']
        ).exists()
        if active_borrows:
            raise serializers.ValidationError({'book_id': '您已借阅该书，尚未归还'})

        borrow_date = timezone.now()
        due_date = borrow_date + timedelta(days=validated_data['borrow_days'])

        borrow_record = BorrowRecord.objects.create(
            reader=reader,
            book=book,
            borrow_date=borrow_date,
            due_date=due_date,
            status='borrowed'
        )

        book.available_quantity -= 1
        if book.available_quantity == 0:
            book.status = 'borrowed'
        book.save()

        return borrow_record


class ReturnBookSerializer(serializers.Serializer):
    record_id = serializers.IntegerField()

    def update(self, instance, validated_data):
        from django.utils import timezone

        instance.return_date = timezone.now()
        instance.status = 'returned'

        if instance.return_date > instance.due_date:
            days_overdue = (instance.return_date - instance.due_date).days
            instance.fine_amount = days_overdue * 0.5

        instance.save()

        book = instance.book
        book.available_quantity += 1
        if book.available_quantity > 0:
            book.status = 'available'
        book.save()

        return instance


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True, min_length=6)
    new_password = serializers.CharField(write_only=True, min_length=6)
    confirm_password = serializers.CharField(write_only=True, min_length=6)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError({'confirm_password': '两次输入的新密码不一致'})
        return attrs
