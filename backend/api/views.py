from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.db.models import Count
from django.shortcuts import get_object_or_404

from .models import Category, Book, BorrowRecord
from .serializers import (
    UserSerializer, UserRegistrationSerializer, UserLoginSerializer,
    CategorySerializer, BookSerializer, BookListSerializer,
    BorrowRecordSerializer, BorrowBookSerializer, ReturnBookSerializer,
    ChangePasswordSerializer
)
from django.contrib.auth import get_user_model

User = get_user_model()


class IsAdminOrSelf(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.role == 'admin':
            return True
        return obj == request.user


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        user.role = 'reader'
        user.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            'user': UserSerializer(user).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    serializer = UserLoginSerializer(data=request.data)
    if serializer.is_valid():
        user = authenticate(
            username=serializer.validated_data['username'],
            password=serializer.validated_data['password']
        )
        if user:
            refresh = RefreshToken.for_user(user)
            return Response({
                'user': UserSerializer(user).data,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            })
        return Response({'detail': '用户名或密码错误'}, status=status.HTTP_401_UNAUTHORIZED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    try:
        refresh_token = request.data.get('refresh')
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()
        return Response({'detail': '退出成功'}, status=status.HTTP_200_OK)
    except Exception:
        return Response({'detail': '退出成功'}, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_current_user(request):
    return Response(UserSerializer(request.user).data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    serializer = ChangePasswordSerializer(data=request.data)
    if serializer.is_valid():
        if not request.user.check_password(serializer.validated_data['old_password']):
            return Response({'old_password': '旧密码错误'}, status=status.HTTP_400_BAD_REQUEST)
        request.user.set_password(serializer.validated_data['new_password'])
        request.user.save()
        return Response({'detail': '密码修改成功'}, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action in ['create']:
            return [AllowAny()]
        elif self.action in ['list', 'destroy']:
            return [IsAdminUser()]
        return [IsAuthenticated(), IsAdminOrSelf()]

    def get_queryset(self):
        queryset = User.objects.all()
        role = self.request.query_params.get('role')
        if role:
            queryset = queryset.filter(role=role)
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                username__icontains=search
            ) | queryset.filter(
                first_name__icontains=search
            ) | queryset.filter(
                email__icontains=search
            )
        return queryset

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        if request.user.role != 'admin' and instance != request.user:
            return Response({'detail': '无权限修改'}, status=status.HTTP_403_FORBIDDEN)
        data = request.data.copy()
        if request.user.role != 'admin':
            data.pop('role', None)
        serializer = self.get_serializer(instance, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.annotate(book_count=Count('books'))
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated()]
        return [IsAdminUser()]

    def get_queryset(self):
        queryset = Category.objects.annotate(book_count=Count('books'))
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(name__icontains=search)
        return queryset


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated()]
        return [IsAdminUser()]

    def get_serializer_class(self):
        if self.action == 'list':
            return BookListSerializer
        return BookSerializer

    def get_queryset(self):
        queryset = Book.objects.all()
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category_id=category)
        status = self.request.query_params.get('status')
        if status:
            queryset = queryset.filter(status=status)
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                title__icontains=search
            ) | queryset.filter(
                author__icontains=search
            ) | queryset.filter(
                isbn__icontains=search
            ) | queryset.filter(
                publisher__icontains=search
            )
        return queryset.order_by('-created_at')


class BorrowRecordViewSet(viewsets.ModelViewSet):
    queryset = BorrowRecord.objects.all()
    serializer_class = BorrowRecordSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = BorrowRecord.objects.all()
        if self.request.user.role == 'reader':
            queryset = queryset.filter(reader=self.request.user)
        reader_id = self.request.query_params.get('reader_id')
        if reader_id:
            queryset = queryset.filter(reader_id=reader_id)
        book_id = self.request.query_params.get('book_id')
        if book_id:
            queryset = queryset.filter(book_id=book_id)
        status = self.request.query_params.get('status')
        if status:
            queryset = queryset.filter(status=status)
        return queryset.order_by('-borrow_date')

    @action(detail=False, methods=['post'], permission_classes=[IsAdminUser])
    def borrow(self, request):
        serializer = BorrowBookSerializer(data=request.data)
        if serializer.is_valid():
            record = serializer.save()
            return Response(BorrowRecordSerializer(record).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], permission_classes=[IsAdminUser])
    def return_book(self, request):
        record_id = request.data.get('record_id')
        try:
            record = BorrowRecord.objects.get(id=record_id, status__in=['borrowed', 'overdue'])
        except BorrowRecord.DoesNotExist:
            return Response({'detail': '借阅记录不存在或已归还'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = ReturnBookSerializer(data=request.data)
        if serializer.is_valid():
            record = serializer.update(record, serializer.validated_data)
            return Response(BorrowRecordSerializer(record).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my_borrowing(self, request):
        records = BorrowRecord.objects.filter(
            reader=request.user,
            status__in=['borrowed', 'overdue']
        ).order_by('-borrow_date')
        page = self.paginate_queryset(records)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(records, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my_history(self, request):
        records = BorrowRecord.objects.filter(
            reader=request.user,
            status='returned'
        ).order_by('-return_date')
        page = self.paginate_queryset(records)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(records, many=True)
        return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def dashboard_stats(request):
    total_books = Book.objects.count()
    available_books = Book.objects.filter(available_quantity__gt=0).count()
    total_readers = User.objects.filter(role='reader').count()
    borrowed_count = BorrowRecord.objects.filter(status__in=['borrowed', 'overdue']).count()
    overdue_count = BorrowRecord.objects.filter(status='overdue').count()
    return Response({
        'total_books': total_books,
        'available_books': available_books,
        'total_readers': total_readers,
        'borrowed_count': borrowed_count,
        'overdue_count': overdue_count,
    })
