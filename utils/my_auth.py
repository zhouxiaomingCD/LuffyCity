from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from Course.models import Account
from utils.redis_pool import POOL
import redis


class Authentication(BaseAuthentication):

    def authenticate(self, request):
        token = request.META.get("HTTP_TOKEN", "")
        conn = redis.Redis(connection_pool=POOL)
        user_id = conn.get(token)
        if not user_id:
            raise AuthenticationFailed("认证失败")
        else:
            user_obj = Account.objects.filter(id=user_id).first()
        return user_obj, user_obj.username
