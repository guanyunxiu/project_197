from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from api.views import (
    UserViewSet, CategoryViewSet, BookViewSet, BorrowRecordViewSet,
    ReservationViewSet, RenewRecordViewSet, FineRecordViewSet,
    OperationLogViewSet, SystemConfigViewSet,
    register, login, logout, get_current_user, change_password,
    dashboard_stats, borrow_stats, reader_stats
)

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'categories', CategoryViewSet)
router.register(r'books', BookViewSet)
router.register(r'borrow-records', BorrowRecordViewSet)
router.register(r'reservations', ReservationViewSet)
router.register(r'renew-records', RenewRecordViewSet)
router.register(r'fine-records', FineRecordViewSet)
router.register(r'operation-logs', OperationLogViewSet)
router.register(r'system-configs', SystemConfigViewSet)

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
    path('api/stats/borrow/', borrow_stats),
    path('api/stats/reader/', reader_stats),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
