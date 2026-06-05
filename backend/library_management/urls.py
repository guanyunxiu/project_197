from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from api.views import (
    UserViewSet, CategoryViewSet, BookViewSet, BorrowRecordViewSet,
    register, login, logout, get_current_user, change_password, dashboard_stats
)

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'categories', CategoryViewSet)
router.register(r'books', BookViewSet)
router.register(r'borrow-records', BorrowRecordViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/auth/register/', register),
    path('api/auth/login/', login),
    path('api/auth/logout/', logout),
    path('api/auth/me/', get_current_user),
    path('api/auth/change-password/', change_password),
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/dashboard/stats/', dashboard_stats),
]
