from api_user.models import User

def get_all_admins():
    admin = User.objects.filter(is_superuser=True, admin=True, active=True)
    if not admin.exists():
        raise Exception('Not found any admins')
    return admin
