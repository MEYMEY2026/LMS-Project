from .models import Notification, SystemSettings

def notifications_processor(request):
    if request.user.is_authenticated:
        notifications = Notification.objects.filter(user=request.user).order_by('-created_at')[:10]
        unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
        return {
            'notifications': notifications,
            'unread_count': unread_count,
        }
    return {'notifications': [], 'unread_count': 0}

def app_settings_processor(request):
    settings_obj, _ = SystemSettings.objects.get_or_create(id=1)
    return {'system_settings': settings_obj}