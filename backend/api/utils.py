from .models import OperationLog, SystemConfig
from django.utils import timezone


def log_operation(request, operation_type, target_model=None, target_id=None, target_name=None, description=''):
    try:
        ip_address = get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')

        OperationLog.objects.create(
            operator=request.user if request.user.is_authenticated else None,
            operation_type=operation_type,
            target_model=target_model,
            target_id=target_id,
            target_name=target_name,
            description=description,
            ip_address=ip_address,
            user_agent=user_agent
        )
    except Exception as e:
        pass


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR', '')
    return ip


def get_system_config(key, default_value=None):
    try:
        config = SystemConfig.objects.get(key=key)
        return config.value
    except SystemConfig.DoesNotExist:
        return default_value


def set_system_config(key, value, description=''):
    SystemConfig.objects.update_or_create(
        key=key,
        defaults={'value': value, 'description': description}
    )


def init_system_config():
    defaults = {
        'default_borrow_days': ('30', '默认借阅天数'),
        'max_renew_count': ('2', '最大续借次数'),
        'renew_days': ('30', '续借天数'),
        'fine_per_day': ('0.5', '每日罚款金额（元）'),
        'reservation_expire_days': ('3', '预约保留天数'),
        'max_borrow_count': ('5', '最大同时借阅数量'),
        'max_reservation_count': ('3', '最大同时预约数量'),
    }
    for key, (value, description) in defaults.items():
        set_system_config(key, value, description)
