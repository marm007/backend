import json
from datetime import timedelta

import requests
from api.models import User
from api.serializers.user import UserSerializer
from axes.signals import user_locked_out
from django.conf import settings
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout as d_logout
from django.core.mail import EmailMultiAlternatives
from django.dispatch import receiver
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.crypto import get_random_string
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.conf import settings


@receiver(user_locked_out)
def raise_permission_denied(*args, **kwargs):
    raise PermissionDenied("Too many failed login attempts")


@api_view(['POST'])
@permission_classes([AllowAny])
def auth(request):
    try:
        user = request.data
        user = authenticate(request=request, email=user.get(
            'email'), password=user.get('password'))

        if user is not None:
            login(request, user)

            refresh = RefreshToken.for_user(user)

            serializer = UserSerializer(user)

            json_data = {'refresh': str(refresh), 'access': str(
                refresh.access_token), 'user': serializer.data, }

            return Response(json_data, status=status.HTTP_200_OK)
        else:
            res = {'detail': 'Bad login or password'}
            return Response(res, status=status.HTTP_400_BAD_REQUEST)
    except Exception as err:
        print(err)
        res = {'detail': 'Something went wrong!'}
        return Response(res, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated, ])
def logout(request):
    d_logout(request._request)
    return Response(status=status.HTTP_200_OK)


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


@api_view(['POST'])
@permission_classes([AllowAny])
def recaptcha_validate(request):
    body = json.loads(request.body)
    token = body['recaptcha']
    res = {}
    url = "https://www.google.com/recaptcha/api/siteverify"
    params = {
        'secret': settings.RECAPTCHA_SECRET_KEY,
        'response': token,
        #'remoteip': get_client_ip(request) #
    }
    if token is None:
        res = {
            'message': 'Token is empty or invalid',
        }
        return Response(res, status=status.HTTP_201_CREATED)
    verify_rs = requests.get(url, params=params, verify=True)
    verify_rs = verify_rs.json()
    res["status"] = verify_rs.get("success", False)
    res['message'] = verify_rs.get('error-codes', None) or "Unspecified error."
    return Response(res)


@api_view(['POST'])
@permission_classes([AllowAny])
def activate_account_link_clicked(request, *args, **kwargs):
    token = request.data.get('activation_token')
    res = {
        'message': 'Account activated',
    }
    user = User.objects.filter(meta__activation_token=token).first()

    if bool(user):
        user.is_active = True
        user.save()
        user.meta.activation_token = ''
        user.meta.activation_token_expires = timezone.now()
        user.meta.save()
        return Response(res, status=status.HTTP_200_OK)
    else:
        res = {
            'message': 'Invalid activation token',

        }
        return Response(res, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def forgot_password(request):
    email = request.data.get('email')
    if email is not None:
        if bool(User.objects.filter(email=email).first()):
            token = get_random_string(length=32)
            verify_link = token

            subject = 'Reset your password'
            from_email = settings.EMAIL_HOST_USER
            to = email
            html_content = '<a href="{}/reset/{}/">Click to reset your password</a>'.format(
                settings.FRONT_URL, verify_link)

            msg = EmailMultiAlternatives(subject, '', from_email, [to])
            msg.attach_alternative(html_content, "text/html")
            msg.send()

            user = get_object_or_404(User, email=email)
            user.meta.reset_password_token = token
            user.meta.reset_password_expires = timezone.now() + timedelta(hours=5)
            user.meta.save()
            res = {
                'message': 'Token sent to an email',
            }
            return Response(res, status=status.HTTP_200_OK)
        else:
            res = {
                'message': 'User with such an email dose nto exists.',
            }
            return Response(res, status=status.HTTP_404_NOT_FOUND)

    else:
        res = {
            'message': 'Non email provided',
        }
        return Response(res, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def reset_password(request, *args, **kwargs):
    token = kwargs.get('token')
    res = {
        'message': 'Password reset successfully',
    }
    user = User.objects.filter(meta__reset_password_token=token,
                               meta__reset_password_expires__gte=timezone.now()).first()

    if bool(user):
        password = request.data.get('password')
        if password is not None:
            user.set_password(request.data.get('password'))
            user.save()
            user.meta.reset_password_token = ''
            user.meta.reset_password_expires = timezone.now()
            user.meta.save()
            return Response(res, status=status.HTTP_200_OK)
        return Response({'error': {'Password cannot be none'}}, status=status.HTTP_400_BAD_REQUEST)

    else:
        res = {
            'message': 'Invalid reset token',

        }
        return Response(res, status=status.HTTP_400_BAD_REQUEST)
