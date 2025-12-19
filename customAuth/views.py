from rest_framework import viewsets
from datetime import datetime, timedelta
from django.conf import settings
import jwt


from django.contrib.auth.models import User
from rest_framework import generics, serializers, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
# from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated

from django.utils import timezone
from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
# from rest_framework_simplejwt.tokens import RefreshToken
from django.db import transaction
from .models import SutUserMst, SutLoginAttmptLog, SutAppUserLog, SutUserLocMap
from .serializers import LoginSerializer

# import hashlib
# import base64
from Crypto.Cipher import AES
import base64

from rest_framework.permissions import BasePermission



KEY = b'Scpl12345DM12345'  # must be bytes
IV = b'RandomInitVector'   # must be bytes

class IsAuthenticatedCustom(BasePermission):
    """
    Custom permission class that uses our middleware authentication
    """
    def has_permission(self, request, view):
        print(f"IsAuthenticatedCustom: request.custom_user = {request.custom_user}, is_authenticated = {request.custom_user is not None}")
        # Check if we have a custom_user set by our middleware
        return hasattr(request, 'custom_user') and request.custom_user is not None




def encrypt_password(plain_text):
    # PKCS5 padding
    pad = 16 - len(plain_text) % 16
    plain_text += chr(pad) * pad

    cipher = AES.new(KEY, AES.MODE_CBC, IV)
    encrypted = cipher.encrypt(plain_text.encode('utf-8'))
    return base64.b64encode(encrypted).decode('utf-8')


def check_password(input_password, db_password):
    """
    Hash input password and compare with DB password.
    """
    # Example: SHA256 + Base64
    hashed = hashlib.sha256(input_password.encode('utf-8')).digest()
    hashed_b64 = base64.b64encode(hashed).decode()
    return hashed_b64 == db_password


def generate_sequential_no(model, field_name):
    """Generate 20-char sequential ID like YYYYMMDD000000000001"""
    today_str = timezone.now().strftime("%Y%m%d")
    last_obj = model.objects.filter(**{f"{field_name}__startswith": today_str}).order_by(f"-{field_name}").first()
    if last_obj:
        last_num = int(getattr(last_obj, field_name)[8:]) + 1
    else:
        last_num = 1
    return f"{today_str}{last_num:012d}"


class CustomLoginView(APIView):
    permission_classes = [AllowAny]

    # @transaction.atomic
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                "statusCode": "400",
                "statusMessage": "Invalid payload",
                "errorInfoList": serializer.errors
            }, status=400)

        user_id = serializer.validated_data["userId"]
        password = serializer.validated_data["password"]
        ip_addr = serializer.validated_data["ipAddress"]

        # 1️⃣ Create login attempt
        login_attmpt_no = generate_sequential_no(SutLoginAttmptLog, "login_attmpt_no")
        attempt = SutLoginAttmptLog.objects.create(
            login_attmpt_no=login_attmpt_no,
            user_id=user_id,
            pwd=password,
            ip_addr=ip_addr,
            sucess_flg="N",
            mod_dt=timezone.now()
        )

        # 2️⃣ Check user existence
        try:
            user = SutUserMst.objects.get(user_id=user_id)
        except SutUserMst.DoesNotExist:
            attempt.fail_rson = "User not found"
            attempt.save()
            return Response({"statusCode": "401", "statusMessage": "Invalid credentials"}, status=401)

        # 2.1 Password comparison (plain)
        if user.user_pwd != encrypt_password(password):
            attempt.fail_rson = "Wrong password"
            attempt.save()
            return Response({"statusCode": "401", "statusMessage": "Invalid credentials"}, status=401)
        # if not check_password(password, user.user_pwd):
        #     attempt.fail_rson = "Wrong password"
        #     attempt.save()
        #     return Response({"statusCode": "401", "statusMessage": "Invalid credentials"}, status=401)

        # 2.2 Check expiry date
        # today = timezone.now().date()
        # if user.exp_dt and user.exp_dt < today:
        #     attempt.fail_rson = "User expired"
        #     attempt.save()
        #     return Response({"statusCode": "403", "statusMessage": "User expired"}, status=403)

        # 2.3 Check active flags
        if user.login_flg != "0" or user.act_flg != "A":
            attempt.fail_rson = "User inactive"
            attempt.save()
            return Response({"statusCode": "403", "statusMessage": "User inactive"}, status=403)

        # 3️⃣ Success → update attempt
        attempt.sucess_flg = "Y"
        attempt.save()

        # 4️⃣ Determine login_lvl_ref_cd from sut_user_loc_map
        locs = SutUserLocMap.objects.filter(user_id=user_id, act_flg="A")
        if locs.count() == 1:
            login_lvl_ref_cd = locs.first().lvl_ref_cd
        else:
            login_lvl_ref_cd = None  # multiple or none

        # 4️⃣ Create app_user_log
        app_log_no = generate_sequential_no(SutAppUserLog, "app_log_no")
        now = timezone.now()
        SutAppUserLog.objects.create(
            app_log_no=app_log_no,
            user_dt=now,
            ip_addr=ip_addr,
            user_id=user_id,
            # sys_dt=today,
            mod_id="M0002",
            logout_flg="N",
            login_dt=now,
            login_lvl_ref_cd = login_lvl_ref_cd,
            data_lvl_ref_cd=None,
            log_typ="A",
            mob_no=user.mob_no
        )
        

        # 5️⃣ Generate JWT
        payload = {
            "user_id": user.user_id,
            "id": user.user_id,  # <-- Add this line!
            "exp": datetime.utcnow() + timedelta(hours=2),  # Token expires in 2 hours
            "iat": datetime.utcnow(),
        }
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")

        return Response({
            "statusCode": "200",
            "statusMessage": "Success",
            "errorInfoList": [],
            "scplAdContext": {
                "userId": user.user_id,
                "userNm": user.user_nm,
                "mobNo": user.mob_no,
                "ipAddress": ip_addr,
                "appLogNo": app_log_no,
                "access": token if isinstance(token, str) else token.decode('utf-8'),  # PyJWT v2 returns str, v1 returns bytes
            }
        }, status=200)
    
