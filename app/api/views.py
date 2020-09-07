from rest_framework import viewsets

from api.models import User, UserProfile, Site, Station, Kiosk, Vehicle, Garage, Route, OperationLog, Manager, \
    V2X, DataHub, Navya, Notice, MicrosoftGraph, Fleet, Advertisement
from api.serializers import UserSerializer, SiteSerializer, StationSerializer, KioskSerializer, \
    VehicleSerializer, GarageSerializer, RouteSerializer, OperationLogSerializer, ManagerSerializer, \
    ManagerLoginSerializer, ManagerEmailSerializer, V2XSerializer, DataHubSerializer, \
    VehiclePartialUpdateSerializer, StationListSerializer, ChangePasswordSerializer,\
    SiteSummarySerializer, OperationLogSummarySerializer, \
    NoticeSerializer, MicrosoftGraphSerializer, ManagerMessageSerializer, \
    OperationLogPartialUpdateSerializer, OperationLogPartial2UpdateSerializer, \
    VehicleGetResponseSerializer, NavyaSerializer, KamoSerializer, EasymileSerializer, FleetSerializer, \
    EventSerializer, EventPassengerSerializer, EventMessageSerializer, \
    OperationLogByDatepdateSerializer, AdSerializer



# 비밀번호 변경 기능을 위한 추가
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from rest_framework.permissions import IsAuthenticated   
from django.contrib.auth import login, authenticate

# 비밀번호 유효성 검사를 위한 추가
from config.custom_password_validation import validate_password
from django.core.exceptions import ValidationError

from rest_framework.decorators import action
from rest_framework.response import Response

from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema
from rest_framework import mixins, status, generics
from drf_yasg import openapi
from geopy.distance import great_circle

from django.shortcuts import get_object_or_404
import requests
import json
import datetime

import time

# send email
from django.core.mail import send_mail


# logger
# logging
# create logger with 'spam_application'
import logging


class CustomFormatter(logging.Formatter):
    """Logging Formatter to add colors and count warning / errors"""
    # https://gist.github.com/kylie-a/86744517063e8ec2daf8c69363720ecd

    grey = "\x1b[38;21m"
    green = "\033[0;38;5;2m"
    yellow = "\x1b[33;21m"
    red = "\x1b[31;21m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"  # (%(filename)s:%(lineno)d)"

    FORMATS = {
        logging.DEBUG: grey + format + reset,
        logging.INFO: green + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: bold_red + format + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
ch.setFormatter(CustomFormatter())

logger.addHandler(ch)


@method_decorator(name='list', decorator=swagger_auto_schema(
    operation_id='모든 사용자 정보',
    operation_description='모든 사용자 정보를 리턴한다.',
    responses={
        '200': UserSerializer,
        '403': "Unauthorized access to accounts",
        '401': "Authentication credentials were not provided.",
    },
))
@method_decorator(name='retrieve', decorator=swagger_auto_schema(
    operation_id='지정된 사용자 정보',
    operation_description='지정된 사용자 정보를 리턴한다.',
    responses={
        '200': UserSerializer,
        '403': "Unauthorized access to accounts",
        '401': "Authentication credentials were not provided.",
    },
))
class UserViewSet(mixins.ListModelMixin,
                  mixins.RetrieveModelMixin,
                  viewsets.GenericViewSet):
    queryset = User.objects.all().order_by('id')
    # serializer_class = UserSerializer

    def get_serializer_class(self):
        if self.action == 'resetpassword':
            return ManagerEmailSerializer
        elif self.action == 'sendmessage':
            return ManagerMessageSerializer
        elif self.action == 'change_password':
            return ChangePasswordSerializer
        
            return UserSerializer

    @swagger_auto_schema(
        responses={
            '200': 'a random password',
            '404': "Not Found",
            '401': 'Authentication credentials were not provided.'
        },
        operation_id='지정된 관리자의 암호를 재설정한다.',
        operation_description='관리자의 이메일 주소로 재설정된 암호를 전달한다.'
    )
    @action(detail=False, methods=['post'])
    def resetpassword(self, request, pk=None):
        user = get_object_or_404(User, email=request.data['email'])
        password = User.objects.make_random_password()
        user.set_password(password)
        user.save()
        self._sendemail('임시 암호 전달', request.data['email'], password)
        return Response({'status': password})

    @swagger_auto_schema(
    responses={
        '200': '비밀번호 변경 성공',
        '404': "새로 입력한 비밀번호가 일치하지 않음",
        '401': '비밀번호 일치 실패'
    },
    e_mail_id = "사용자 id",
    origin_password = "현재 비밀번호",
    new_password = '변경하기 원하는 새로운 비밀번호',
    conform_new_password = '새로운 비밀번호 확인'
    )
    @action(detail=False, methods=['post'])
    # @login_required
    def change_password(self, request, pk=None):
            print(request, request.data)
            uid = request.data["e_mail_id"]
            current_password = request.data["old_password"]
            user = None
            user = authenticate(username=uid, password=current_password)
            print(user, uid, current_password)
            if user:
                new_password = request.data["new_password"]
                password_confirm = request.data["confirm_new_password"]
                if new_password == password_confirm:
                    try:
                        validate_password(new_password, user)
                        user.set_password(new_password)
                        user.save()
                        # 비밀번호 변경 후, 연결 유지를 위한 명령 문이라지만, 작동 여부는 확인 불가
                        # update_session_auth_hash(request, user)
                        return Response(["새로운 비밀번호로 변경됐습니다."], status=status.HTTP_200_OK)
                    except ValidationError as e:
                        return Response(e, status=status.HTTP_401_UNAUTHORIZED)
                else:
                    return Response(["두 개의 비밀번호가 일치하지 않습니다."], status=status.HTTP_404_NOT_FOUND)
            else:
                return Response(["비밀번호가 일치하지 않습니다."], status=status.HTTP_401_UNAUTHORIZED)

    @swagger_auto_schema(
        responses={
            '200': 'Ok',
            '202': 'Accept',
            '404': "Not Found",
            '401': 'Authentication credentials were not provided.'
        },
        operation_id='지정된 관리자에게 메시지를 전달한다.',
        operation_description='관리자의 이메일 주소로 메시지를 전송한다.',
    )
    @action(detail=False, methods=['post'])
    def sendmessage(self, request, pk=None):
        obj = get_object_or_404(User, email=request.data['email'])
        start_time = time.time()
        message_body = request.data['message']
        from_email = 'bcchoi@aspringcloud.com'
        to_email = []
        to_email.append(obj.email)
        ret = send_mail(
            '관제 긴급 메시지',
            message_body,
            from_email,
            to_email,
            fail_silently=False,
        )
        elapsed_time = time.time() - start_time
        context = {
            'elapsed_time': elapsed_time,
            'message_body': message_body,
            'from_email': from_email,
            'to_emai': to_email
        }

        if ret == 0 or ret == 1:
            return Response(context, status=status.HTTP_200_OK)
        else:
            return Response('Make sure all fields are entered and valid.')

        # status = self._sendemail('관제 긴급 메시지', obj.email, request.data['message'])
        # return Response({'status': status})

    # using microsfot grpah api, replaced to send_image
    def _sendemail(self, subject, email, message):
        graph = get_object_or_404(MicrosoftGraph, pk=2)
        data = {
            "message": {
                "subject": subject,
                "body": {
                    "contentType": "Text",
                    "content": ""
                },
                "toRecipients": [
                    {
                        "emailAddress": {
                            "address": ""
                        }
                    }
                ],
                "ccRecipients": [
                    {
                        "emailAddress": {
                            "address": "bcchoi@aspringcloud.com"
                        }
                    }
                ]
            }
        }
        data['message']['body']['content'] = message
        data['message']['toRecipients'][0]['emailAddress']['address'] = email
        # print(json.dumps(data, indent=4, sort_keys=True))

        url = 'https://graph.microsoft.com/v1.0/me/sendMail'
        r = requests.request(
            method='post',
            url=url,
            data=json.dumps(data),
            verify=None,
            headers={'Authorization': 'Bearer ' + graph.token, 'Content-type': 'application/json'},
        )
        if r is not None:
            print(r.status_code)
            if r.status_code != 200 and r.status_code != 202:
                res = r.reason
                logger.error('{} {}'.format(r.status_code, res))
            else:
                logger.info(r.status_code)

            return r.status_code
        return status.HTTP_404_NOT_FOUND

    # 의미 없음.
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = UserSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    # 의미 없음.
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


@method_decorator(name='list', decorator=swagger_auto_schema(
    operation_id='모든 사이트(운영/비운영) 정보',
    operation_description='모든 사이트(운영/비운영) 정보를 리턴한다.',
    responses={
        '200': SiteSerializer,
        '403': "Unauthorized access to accounts",
        '401': "Authentication credentials were not provided.",
    },
))
@method_decorator(name='retrieve', decorator=swagger_auto_schema(
    operation_id='지정된 사이트(운영/비운영) 정보',
    operation_description='지정된 사이트(운영/비운영) 정보를 리턴한다.',
    responses={
        '200': SiteSerializer,
        '403': "Unauthorized access to accounts",
        '401': "Authentication credentials were not provided.",
    },
))
@method_decorator(name='update', decorator=swagger_auto_schema(
    operation_id='지정된 사이트 정보 업데이트',
    operation_description='지정된 사이트 정보를 일괄 업데이트 한다.',
    responses={
        '200': "Ok",
        '403': "Unauthorized access to accounts",
        '401': "Authentication credentials were not provided.",
    },
))
@method_decorator(name='partial_update', decorator=swagger_auto_schema(
    operation_id='지정된 사이트 정보 업데이트',
    operation_description='지정된 사이트 정보를 부분 업데이트 한다.',
    responses={
        '200': "Ok",
        '403': "Unauthorized access to accounts",
        '401': "Authentication credentials were not provided.",
    },
))
class SiteViewSet(mixins.ListModelMixin,
                  mixins.RetrieveModelMixin,
                  mixins.UpdateModelMixin,
                  viewsets.GenericViewSet):
    queryset = Site.objects.all().order_by('mid')
    serializer_class = SiteSerializer

    @swagger_auto_schema(
        responses={
            '200': SiteSummarySerializer,
            '404': "Not Foun",
            '401': 'Authentication credentials were not provided.'
        },
        operation_id='총 차량, 정류장, 키오스크, 차고지, 경로, 데이터허브, 관리자 숫자',
        operation_description='총 차량, 정류장, 키오스크, 차고지, 경로, 데이터허브, 관리자 숫자를 리턴한다.',
    )
    @action(detail=False, methods=['get'])
    def summary(self, request, pk=None):
        newobj = dict()
        count = 0
        qs = Vehicle.objects.all()
        for q in qs:
            if 'SCN9' not in q.mid:
                count = count + 1
        newobj['vehicle_count'] = count

        count = 0
        qs = Station.objects.all()
        for q in qs:
            if q.operation:
                count = count + 1
        newobj['station_count'] = count

        count = 0
        qs = Kiosk.objects.all()
        for q in qs:
            if q.operation:
                count = count + 1
        newobj['kiosk_count'] = count

        count = 0
        qs = Garage.objects.all()
        for q in qs:
            if q.operation:
                count = count + 1
        newobj['garage_count'] = count

        count = 0
        qs = Route.objects.all()
        for q in qs:
            if q.operation:
                count = count + 1
        newobj['route_count'] = count

        count = 0
        qs = DataHub.objects.all()
        for q in qs:
            if q.operation:
                count = count + 1
        newobj['datahub_count'] = count

        newobj['manager_count'] = User.objects.count()
        serializer = SiteSummarySerializer(data=newobj)
        serializer.is_valid()
        return Response(serializer.data, status=status.HTTP_200_OK)

  
      

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        newobj = serializer.data
        
        # User에 대한 정보 추가
        queryset = User.objects.all().order_by('id')
        UserS = UserSerializer(queryset, many=True, context={'request': request})
        
        userinfo = []
        for userIndex in UserS.data:
            if userIndex['pk'] in newobj['user']:
                userinfo.append( {
                                        "pk":userIndex['pk'], \
                                        "email":userIndex['email'], \
                                        "username":userIndex['username']
                                    })
            else:
                continue
        
        newobj['user'] = userinfo
        count = 0
        # 각 사이트 별 차량 갯수 계산
        qs = Vehicle.objects.all().order_by('mid')

        serializer = VehicleSerializer(qs, many=True, context={'request': request})
        for vehicle_index in serializer.data:
            if vehicle_index['site'] is not None and int(vehicle_index['site']) == newobj['id']:
                count += 1
        newobj['vehicle_count'] = count

        # 각 사이트별 스테이션 갯수 계산
        count = 0
        qs = Station.objects.all().order_by('mid')
        serializer = StationSerializer(qs, many=True, context={'request': request})
        for station_index in serializer.data:
            if station_index['site'] is not None and int(station_index['site']) == newobj['id']:
                count += 1
        newobj['station_count'] = count

        # 각 사이트별 키오스크 갯수
        count = 0
        qs = Kiosk.objects.all().order_by('mid')
        serializer = KioskSerializer(qs, many=True, context={'request': request})
        for kiosk_index in serializer.data:
            if kiosk_index['operation'] and kiosk_index['site'] is not None and int(kiosk_index['site']) == newobj['id']:
                count += 1
        newobj['kiosk_count'] = count


        count = 0
        qs = Route.objects.all().order_by('mid')
        serializer = RouteSerializer(qs, many=True, context={'request': request})
        for route_index in serializer.data:
            if route_index['operation'] and route_index['site'] is not None and int(route_index['site']) == newobj['id']:
                count = count + 1 
        newobj['route_count'] = count

        count = 0
        qs = Garage.objects.all().order_by('mid')
        serializer = GarageSerializer(qs, many=True, context={'request': request})
        for garage_index in serializer.data:
            if  garage_index['site'] is not None and int(garage_index['site']) == newobj['id']:
                count = count + 1
        newobj['garege_count'] = count
        
        serializer = SiteSummarySerializer(data=newobj)
        serializer.is_valid()
        return Response(newobj, status=status.HTTP_200_OK)

    # todo
    def list(self, request ):
        instance = Site.objects.all()
        serializer = SiteSerializer(instance, many=True)
        newobj = serializer.data
        
        queryset = User.objects.all().order_by('id')
        # userinstance = User.objects.all()
        UserS = UserSerializer(queryset, many=True, context={'request': request})
        
        
        #각 Station과 User의 id 비교 후, 일치되는 데이터를 찾아 추가.
        for userindex in newobj:
            userinfo = []
            for pkIndex in UserS.data:
                if pkIndex['pk'] in userindex['user']:
                    userinfo.append( {
                                        "pk":pkIndex['pk'], \
                                        "email":pkIndex['email'], \
                                        "username":pkIndex['username']
                                    })
                else:
                    continue
                    
            userindex['user'] = userinfo

        return Response(newobj, status=status.HTTP_200_OK)


@method_decorator(name='list', decorator=swagger_auto_schema(
    operation_id='모든 정류장 정보',
    operation_description='모든 정류장 정보를 리턴한다.',
    responses={
        '200': StationListSerializer,
        '403': "Unauthorized access to accounts",
        '401': "Authentication credentials were not provided.",
    },
))
@method_decorator(name='retrieve', decorator=swagger_auto_schema(
    operation_id='지정된 정류장 정보',
    operation_description='지정된 정류장 정보를 리턴한다.',
    responses={
        '200': StationSerializer,
        '403': "Unauthorized access to accounts",
        '401': "Authentication credentials were not provided.",
    },
))
@method_decorator(name='partial_update', decorator=swagger_auto_schema(
    operation_id='지정된 정류장 정보 업데이트',
    operation_description='지정된 정류장 정보를 부분 업데이트 한다.',
    responses={
        '200': "Ok",
        '403': "Unauthorized access to accounts",
        '401': "Authentication credentials were not provided.",
    },
))
class StationViewSet(mixins.ListModelMixin,
                     mixins.RetrieveModelMixin,
                     mixins.UpdateModelMixin,
                     viewsets.GenericViewSet):
    queryset = Station.objects.all().order_by('mid')
    serializer_class = StationSerializer

    @swagger_auto_schema(
        responses={
            '200': '{미정}',
            '404': "Not Found",
            '401': 'Authentication credentials were not provided.'
        },
        operation_id='요약된 모든 정류장 정보',
        operation_description='요약된 모든 정류장 정보를 리턴한다. \
            <p style="color:Red;"><b>구현 예정</b></p>',
    )
    @action(detail=False, methods=['get'])
    def summary(self, request, pk=None):
        return Response({'status': request.data})

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = StationSerializer(queryset, many=True, context={'request': request})
        # print(json.dumps(serializer.data, indent=4, sort_keys=True))

        newobj = list()
        for data in serializer.data:
            site = data['site']
            # site의 모든 kiosk들.
            query = Kiosk.objects.filter(site=site)
            kiosk = KioskSerializer(query, many=True)
            # site의 모든 kiosk들의 위성좌표
            data['iskiosk'] = False
            for pose in kiosk.data:
                a = (pose['lat'], pose['lon'])
                b = (data['lat'], data['lon'])
                if great_circle(a, b).km < 0.02:
                    data['iskiosk'] = True
                    break
            newobj.append(data)
        serializer = StationListSerializer(data=newobj, many=True)
        serializer.is_valid()
        # newobj 대신 serializer.data 왜? id가 출력되지 않음.
        return Response(newobj, status=status.HTTP_200_OK)


@method_decorator(name='list', decorator=swagger_auto_schema(
    operation_id='모든 키오스크 정보',
    operation_description='모든 키오스크 정보를 리턴한다.',
    responses={
        '200': KioskSerializer,
        '403': "Unauthorized access to accounts",
        '401': "Authentication credentials were not provided.",
    },
))
@method_decorator(name='retrieve', decorator=swagger_auto_schema(
    operation_id='지정된 키오스크 정보',
    operation_description='지정된 키오스크 정보를 리턴한다.',
    responses={
        '200': KioskSerializer,
        '403': "Unauthorized access to accounts",
        '401': "Authentication credentials were not provided.",
    },
))
class KioskViewSet(mixins.ListModelMixin,
                   mixins.RetrieveModelMixin,
                   viewsets.GenericViewSet):
    queryset = Kiosk.objects.all().order_by('mid')
    serializer_class = KioskSerializer

    @swagger_auto_schema(
        responses={
            '200': '{미정}',
            '404': "Not Found",
            '401': 'Authentication credentials were not provided.'
        },
        operation_id='요약된 모든 키오스크 정보',
        operation_description='요약된 모든 키오스크 정보를 리턴한다. \
            <p style="color:Red;"><b>구현 예정</b></p>',
    )
    @action(detail=False, methods=['get'])
    def summary(self, request, pk=None):
        return Response({'status': request.data})


@method_decorator(name='list', decorator=swagger_auto_schema(
    operation_id='모든 차량 정보',
    operation_description='모든 차량 정보를 리턴한다.',
    responses={
        '200': VehicleGetResponseSerializer,
        '403': "Unauthorized access to accounts",
        '401': "Authentication credentials were not provided.",
    },
))
@method_decorator(name='retrieve', decorator=swagger_auto_schema(
    operation_id='지정된 차량 정보',
    operation_description='지정된 차량 정보를 리턴한다.',
    responses={
        '200': VehicleGetResponseSerializer,
        '403': "Unauthorized access to accounts",
        '401': "Authentication credentials were not provided.",
    },
))
@method_decorator(name='update', decorator=swagger_auto_schema(
    operation_id='지정된 차량 정보 업데이트',
    operation_description='지정된 차량 정보를 일괄 업데이트 한다.',
    responses={
        '200': "Ok",
        '403': "Unauthorized access to accounts",
        '401': "Authentication credentials were not provided.",
    },
))
@method_decorator(name='partial_update', decorator=swagger_auto_schema(
    operation_id='지정된 차량 정보 업데이트',
    operation_description='지정된 차량 정보를 부분 업데이트 한다.',
    responses={
        '200': "Ok",
        '403': "Unauthorized access to accounts",
        '401': "Authentication credentials were not provided.",
    },
))
class VehicleViewSet(mixins.ListModelMixin,
                     mixins.RetrieveModelMixin,
                     mixins.UpdateModelMixin,
                     viewsets.GenericViewSet):
    queryset = Vehicle.objects.all().order_by('mid')

    def get_serializer_class(self):
        if self.request.method in ['POST', 'PUT', 'PATCH']:
            return VehiclePartialUpdateSerializer
        else:
            return VehicleSerializer

    @swagger_auto_schema(
        responses={
            '200': '{미정}',
            '404': "Not Found",
            '401': 'Authentication credentials were not provided.'
        },
        operation_id='요약된 모든 차량 정보',
        operation_description='요약된 모든 차량 정보를 리턴한다. \
            <p style="color:Red;"><b>구현 예정</b></p>',
    )
    @action(detail=False, methods=['get'])
    def summary(self, request, pk=None):
        # deprecated
        return Response({'status': request.data})

    def list(self, request, *args, **kwargs):
        queryset = Vehicle.objects.all().order_by('mid')
        serializer = VehicleSerializer(queryset, many=True, context={'request': request})

        newobj = list()
        for data in serializer.data:
            # 나이스한 방법을 찾자
            if data['model']:
                pk = data['model']
                query = Fleet.objects.get(id=pk)
                s = FleetSerializer(query)
                data['model'] = s.data

            newobj.append(data)
        serializer = VehicleSerializer(data=newobj, many=True)
        serializer.is_valid()
        # newobj 대신 serializer.data 왜? id가 출력되지 않음.
        return Response(newobj, status=status.HTTP_200_OK)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        data = serializer.data
        if data['model']:
            pk = data['model']
            query = Fleet.objects.get(id=pk)
            s = FleetSerializer(query)
            data['model'] = s.data
        return Response(data)

    ''' 6/16
    def update(self, request, *args, **kwargs):
        data = self.request.data
        qv = get_object_or_404(Vehicle, pk=kwargs['pk'])
        sv = VehicleSerializer(qv)
        site = sv.data['site']
        qs = Station.objects.filter(site=site)
        ss = StationSerializer(qs, many=True)
        for s in ss.data:
            if 'lat' in request.data and 'lon' in request.data:
                a = (request.data['lat'], request.data['lon'])
                b = (s['lat'], s['lon'])
                #print('{} km'.format(great_circle(a,b).km))
                if great_circle(a, b).km < 0.02:
                    print("circle:{} station id:{} mid:{} name:{}".format(great_circle(a,b).km, s['id'],s['mid'],s['name']))
                    request.data['passed_station'] = s['id']
                    break
        return super(VehicleViewSet, self).update(request, *args, **kwargs)
    '''
    ''' 정의 안되어 있으면 update로 전달
    def partial_update(self, request, *args, **kwargs):
        return super(VehicleViewSet, self).partial_update(request, *args, **kwargs)
    '''


@method_decorator(name='list', decorator=swagger_auto_schema(
    operation_id='모든 차고지 정보',
    operation_description='모든 차고지 정보를 리턴한다.',
    responses={
        '200': GarageSerializer,
        '403': "Unauthorized access to accounts",
        '401': "Authentication credentials were not provided.",
    },
))
@method_decorator(name='retrieve', decorator=swagger_auto_schema(
    operation_id='지정된 차고지 정보',
    operation_description='지정된 차고지 정보를 리턴한다.',
    responses={
        '200': GarageSerializer,
        '403': "Unauthorized access to accounts",
        '401': "Authentication credentials were not provided.",
    },
))
class GarageViewSet(mixins.ListModelMixin,
                    mixins.RetrieveModelMixin,
                    viewsets.GenericViewSet):
    queryset = Garage.objects.all().order_by('mid')
    serializer_class = GarageSerializer

    @swagger_auto_schema(
        responses={
            '200': '{미정}',
            '404': "Not Found",
            '401': 'Authentication credentials were not provided.'
        },
        operation_id='요약된 모든 차고지 정보',
        operation_description='요약된 모든 차고지 정보를 리턴한다. \
            <p style="color:Red;"><b>구현 예정</b></p>',
    )
    @action(detail=False, methods=['get'])
    def summary(self, request, pk=None):
        return Response({'status': request.data})


@method_decorator(name='list', decorator=swagger_auto_schema(
    operation_id='모든 경로 정보',
    operation_description='모든 경로 정보를 리턴한다.',
    responses={
        '200': RouteSerializer,
        '403': "Unauthorized access to accounts",
        '401': "Authentication credentials were not provided.",
    },
))
@method_decorator(name='retrieve', decorator=swagger_auto_schema(
    operation_id='지정된 경로 정보',
    operation_description='지정된 경로 정보를 리턴한다.',
    responses={
        '200': RouteSerializer,
        '403': "Unauthorized access to accounts",
        '401': "Authentication credentials were not provided.",
    },
))
class RouteViewSet(mixins.ListModelMixin,
                   mixins.RetrieveModelMixin,
                   viewsets.GenericViewSet):
    queryset = Route.objects.all().order_by('mid')
    serializer_class = RouteSerializer

    @swagger_auto_schema(
        responses={
            '200': '{미정}',
            '404': "Not Found",
            '401': 'Authentication credentials were not provided.'
        },
        operation_id='요약된 모든 경로 정보',
        operation_description='요약된 모든 경로 정보를 리턴한다. \
            <p style="color:Red;"><b>구현 예정</b></p>',
    )
    @action(detail=False, methods=['get'])
    def summary(self, request, pk=None):
        return Response({'status': request.data})


@method_decorator(name='list', decorator=swagger_auto_schema(
    operation_id='모든 차량 운행기록 정보',
    operation_description='모든 차량 운행기록 정보를 리턴한다.',
    responses={
        '200': OperationLogSerializer,
        '403': "Unauthorized access to accounts",
        '401': "Authentication credentials were not provided.",
    },
))
@method_decorator(name='retrieve', decorator=swagger_auto_schema(
    operation_id='지정된 운행기록 정보',
    operation_description='지정된 운행기록 정보를 리턴한다.',
    responses={
        '200': OperationLogSerializer,
        '403': "Unauthorized access to accounts",
        '401': "Authentication credentials were not provided.",
    },
))
class OperationLogViewSet(mixins.ListModelMixin,
                          mixins.RetrieveModelMixin,
                          viewsets.GenericViewSet):
    queryset = OperationLog.objects.all().order_by('mid')

    def get_serializer_class(self):
        if self.action == 'start_vehicle' or self.action == 'stop_vehicle':
            return OperationLogPartialUpdateSerializer
        elif self.action == 'count_passenger':
            return OperationLogPartial2UpdateSerializer
        elif self.action == 'by_date':
            return OperationLogByDatepdateSerializer
        else:
            return OperationLogSerializer

    @swagger_auto_schema(
        responses={
            '200': OperationLogSummarySerializer,
            '404': "Not Found",
            '401': 'Authentication credentials were not provided.'
        },
        operation_id='누적된 운행 거리와 누적된 승객수',
        operation_description='누적된 운행 거리와 누적된 승객수를 리턴한다.'
    )
    @action(detail=False, methods=['get'])
    def summary(self, request, pk=None):
        qs1 = Vehicle.objects.all()
        newobj = list()
        for q1 in qs1:
            qs2 = OperationLog.objects.filter(vehicle=q1.pk)
            acc_pass = 0
            acc_dist = 0
            for q2 in qs2:
                if q2.passenger is not None:
                    acc_pass += q2.passenger
                if q2.distance is not None:
                    acc_dist += q2.distance
            newobj.append({'vehicle': q1.name, 'accum_passenger': acc_pass, 'accum_distance': acc_dist})
        serializer = OperationLogSummarySerializer(data=newobj, many=True)
        serializer.is_valid()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        responses={
            '200': "Predefined JSON format",
            '404': "Not Found",
            '401': 'Authentication credentials were not provided.'
        },
        operation_id='지정된 날짜의 운행 정보',
        operation_description='지정된 날짜의 운행 정보 리턴 예) %Y-%m-%d 2020-05-05'
    )
    @action(detail=False, methods=['post'], url_path='by-date', url_name='by-date')
    def by_date(self, request, pk=None):
        query = OperationLog.objects.filter(time_start__date=datetime.datetime.strptime(request.data['date'], "%Y-%m-%d"))
        serializer = OperationLogSerializer(query, many=True)
        newobj = []
        for data in serializer.data:
            contant = {}
            contant['log'] = data
            vehicle = Vehicle.objects.get(pk=data['vehicle'])
            vs = VehicleSerializer(vehicle)
            dv = {}
            dv['id'] = vs.data['id']
            dv['mid'] = vs.data['mid']
            dv['name'] = vs.data['name']
            contant['vehicle'] = dv
            ss = SiteSerializer(vehicle.site)
            contant['site'] = ss.data
            newobj.append(contant)
        # print(json.dumps(newobj, indent=4, sort_keys=True))
        return Response(newobj, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        responses={
            '200': OperationLogSerializer,
            '404': "Not Found",
            '401': 'Authentication credentials were not provided.'
        },
        operation_id='DEPRECATED',
        operation_description='운전자 앱에서 차량운행 시작시 호출 API'
    )
    # https://www.django-rest-framework.org/api-guide/routers/
    @action(detail=False, methods=['post'], url_path='start-vehicle', url_name='start_vehicle')
    def start_vehicle(self, request, pk=None):
        '''
        parameter:
            time_start:  UTC, string
            vehicle_id
        response:
            OperationLogSerializer
        '''
        pass

    @swagger_auto_schema(
        responses={
            '200': OperationLogSerializer,
            '404': "Not Found",
            '401': 'Authentication credentials were not provided.'
        },
        operation_id='DEPRECATED',
        operation_description='운전자 앱에서 차량운행 종료시 호출 API'
    )
    @action(detail=False, methods=['post'], url_path='stop-vehicle', url_name='stop_vehicle')
    def stop_vehicle(self, request, pk=None):
        '''
        parameter:
            time_end: UTC, string
            vehicle_id
        response:
            OperationLogSerializer
        '''
        pass

    @swagger_auto_schema(
        responses={
            '200': OperationLogSerializer,
            '404': "Not Found",
            '401': 'Authentication credentials were not provided.'
        },
        operation_id='DEPRECATED',
        operation_description='운전자 앱에서 탑승객 변경시 호출 API'
    )
    @action(detail=False, methods=['post'], url_path='count-passenger', url_name='count_passenger')
    def count_passenger(self, request, pk=None):
        '''
        parameter:
            passenger: 현재 탑승객수, string
            vehicle_id
        response:
            OperationLogSerializer
        '''
        pass


@method_decorator(name='retrieve', decorator=swagger_auto_schema(
    operation_id='지정된 차량 운행기록 정보',
    operation_description='지정된 차량 운행기록 정보를 리턴한다.',
    responses={
        '200': OperationLogSerializer,
        '403': "Unauthorized access to accounts",
        '401': "Authentication credentials were not provided.",
    },
))
class OperationLogVehicleViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):

    queryset = OperationLog.objects.all().order_by('mid')

    def retrieve(self, request, *args, **kwargs):
        qs = OperationLog.objects.filter(vehicle=kwargs['pk'])
        newobj = list()
        for q in qs:
            s = OperationLogSerializer(q)
            newobj.append(s.data)
        return Response(newobj, status=status.HTTP_200_OK)


'''
fields_param = openapi.Parameter(
    "page",
    openapi.IN_QUERY,
    description="의미 없는 데이터임=",
    type=openapi.TYPE_INTEGER,
)
@method_decorator(
    name="list", decorator=swagger_auto_schema(manual_parameters=[fields_param])
)
'''


email_param = openapi.Parameter(
    "data",
    openapi.IN_QUERY,
    description="",
    type=openapi.TYPE_OBJECT,
    required=True,
)

password_param = openapi.Parameter(
    "password",
    openapi.IN_QUERY,
    description="",
    type=openapi.TYPE_STRING,
    required=True,
)


@method_decorator(name='list', decorator=swagger_auto_schema(
    operation_id='모든 관리자 정보',
    operation_description='모든 관리자 정보를 리턴한다.',
    responses={
        status.HTTP_200_OK: ManagerSerializer,
        status.HTTP_403_FORBIDDEN: openapi.Response("Unauthorized access to accounts"),
        status.HTTP_401_UNAUTHORIZED: openapi.Response("Authentication credentials were not provided."),
    },
))
@method_decorator(name='create', decorator=swagger_auto_schema(
    operation_id='관리자를 등록한다.',
    operation_description='입력된 정보를 확인하여 등록여부를 결정한다. \
    <p style="color:Tomato;"><b>Example Value 클릭하여 필수 항목을 확인한다.</b></p>',

    responses={
        status.HTTP_200_OK: ManagerSerializer,
        status.HTTP_403_FORBIDDEN: openapi.Response("Unauthorized access to accounts"),
        status.HTTP_401_UNAUTHORIZED: openapi.Response("Authentication credentials were not provided."),
    },
))
@method_decorator(name='retrieve', decorator=swagger_auto_schema(
    operation_id='지정된 관리자 정보',
    operation_description='지정된 관리자 정보를 리턴한다.',
    responses={
        status.HTTP_200_OK: ManagerSerializer,
        status.HTTP_403_FORBIDDEN: openapi.Response("Unauthorized access to accounts"),
        status.HTTP_401_UNAUTHORIZED: openapi.Response("Authentication credentials were not provided."),
    },
))
class ManagerViewSet(mixins.CreateModelMixin,
                     mixins.ListModelMixin,
                     mixins.RetrieveModelMixin,
                     # mixins.UpdateModelMixin,
                     viewsets.GenericViewSet):
    """
    통합관제 관리자 계정에 관한 API

    통합관제 관리자 계정에 관한 API
    """
    queryset = Manager.objects.all().order_by('mid')
    # serializer_class = ManagerSerializer

    def get_serializer_class(self):
        if self.action == 'login':
            return ManagerLoginSerializer
        elif self.action == 'logout':
            return ManagerEmailSerializer
        elif self.action == 'sendmessage':
            return ManagerMessageSerializer
        elif self.action == 'resetpassword':
            return ManagerEmailSerializer
        else:
            return ManagerSerializer
   
    
    @swagger_auto_schema(
        responses={
            '200': '{미정}',
            '404': "Not Found",
            '401': 'Authentication credentials were not provided.'
        },
        operation_id='요약된 모든 관리자 정보',
        operation_description='요약된 모든 관리자 정보를 리턴한다. \
            <p style="color:Tomato;"><b>구현 예정</b></p>',

    )
    @action(detail=False, methods=['get'])
    def summary(self, request, pk=None):
        return Response({'status': request.data})

    @swagger_auto_schema(
        responses={
            '200': 'Ok',
            '404': "Not Found",
            '401': 'Authentication credentials were not provided.'
        },
        operation_id='관리자 로그',
        operation_description='관리자 로그인 API',
    )
    @action(detail=False, methods=['post'])
    def login(self, request, pk=None):
        return Response({'status': request.data})

    @swagger_auto_schema(
        responses={
            '200': 'Ok',
            '404': "Not Found",
            '401': 'Authentication credentials were not provided.'
        },
        operation_id='관리자 로그아웃',
        operation_description='관리자 로그아웃 API',
    )
    @action(detail=False, methods=['post'])
    def logout(self, request, pk=None):
        return Response({'status': request.data})

    @swagger_auto_schema(
        responses={
            '200': 'Ok',
            '404': "Not Found",
            '401': 'Authentication credentials were not provided.'
        },
        operation_id='지정된 관리자에게 메시지를 전달한다.',
        operation_description='설치된 관리자앱(안드로이드)으로 메시지를 전송한다. <br> \
        <p style="color:Tomato;"><b>구현 예정</b></p>',
    )
    @action(detail=False, methods=['post'])
    def sendmessage(self, request, pk=None):
        obj = get_object_or_404(Manager, email=request.data['email'])
        graph = get_object_or_404(MicrosoftGraph, pk=2)
        data = {
            "message": {
                "subject": "통합 관제(제목 정의해야함)",
                "body": {
                    "contentType": "Text",
                    "content": ""
                },
                "toRecipients": [
                    {
                        "emailAddress": {
                            "address": ""
                        }
                    }
                ],
                "ccRecipients": [
                    {
                        "emailAddress": {
                            "address": "bcchoi@aspringcloud.com"
                        }
                    }
                ]
            }
        }
        data['message']['body']['content'] = request.data['message']
        data['message']['toRecipients'][0]['emailAddress']['address'] = obj.email
        # print(json.dumps(data, indent=4, sort_keys=True))

        url = 'https://graph.microsoft.com/v1.0/me/sendMail'
        requests.request(
            method='post',
            url=url,
            data=json.dumps(data),
            verify=None,
            headers={'Authorization': 'Bearer ' + graph.token, 'Content-type': 'application/json'},
        )
        return Response({'status': request.data})

    @swagger_auto_schema(
        responses={
            '200': 'Ok',
            '404': "Not Found",
            '401': 'Authentication credentials were not provided.'
        },
        operation_id='지정된 관리자의 암호를 재설정한다.',
        operation_description='관리자의 이메일 주소로 재설정된 암호를 전달한다. \
        <p style="color:Tomato;"><b>구현 예정</b></p>',
    )
    @action(detail=False, methods=['post'])
    def resetpassword(self, request, pk=None):
        return Response({'status': request.data})


@method_decorator(name='list', decorator=swagger_auto_schema(
    operation_id='모든 V2X 정보',
    operation_description='모든 V2X 정보를 리턴한다.',
    responses={
        '200': V2XSerializer,
        '403': "Unauthorized access to accounts",
        '401': "Authentication credentials were not provided.",
    },
))
@method_decorator(name='retrieve', decorator=swagger_auto_schema(
    operation_id='지정된 V2X 정보',
    operation_description='지정된 V2X 정보를 리턴한다.',
    responses={
        '200': V2XSerializer,
        '403': "Unauthorized access to accounts",
        '401': "Authentication credentials were not provided.",
    },
))
class V2XViewSet(mixins.ListModelMixin,
                 mixins.RetrieveModelMixin,
                 viewsets.GenericViewSet):
    queryset = V2X.objects.all().order_by('mid')
    serializer_class = V2XSerializer

    @swagger_auto_schema(
        responses={
            '200': '{미정}',
            '404': "Not Found",
            '401': 'Authentication credentials were not provided.'
        },
        operation_id='요약된 모든 V2X 정보',
        operation_description='요약된 모든 V2X 정보를 리턴한다. \
            <p style="color:Red;"><b>구현 예정</b></p>',
    )
    @action(detail=False, methods=['get'])
    def summary(self, request, pk=None):
        return Response({'status': request.data})


@method_decorator(name='list', decorator=swagger_auto_schema(
    operation_id='모든 Data DataHub 정보',
    operation_description='모든 DataHub 정보를 리턴한다.',
    responses={
        '200': DataHubSerializer,
        '403': "Unauthorized access to accounts",
        '401': "Authentication credentials were not provided.",
    },
))
@method_decorator(name='retrieve', decorator=swagger_auto_schema(
    operation_id='지정된 DataHub 정보',
    operation_description='지정된 DataHub 정보를 리턴한다.',
    responses={
        '200': DataHubSerializer,
        '403': "Unauthorized access to accounts",
        '401': "Authentication credentials were not provided.",
    },
))
class DataHubViewSet(mixins.ListModelMixin,
                     mixins.RetrieveModelMixin,
                     viewsets.GenericViewSet):
    queryset = DataHub.objects.all().order_by('mid')
    serializer_class = DataHubSerializer

    @swagger_auto_schema(
        responses={
            '200': '{미정}',
            '404': "Not Found",
            '401': 'Authentication credentials were not provided.'
        },
        operation_id='요약된 모든 DataHub 정보',
        operation_description='요약된 모든 DataHub 정보를 리턴한다. \
            <p style="color:Red;"><b>구현 예정</b></p>',
    )
    @action(detail=False, methods=['get'])
    def summary(self, request, pk=None):
        return Response({'status': request.data})


@method_decorator(name='list', decorator=swagger_auto_schema(
    operation_id='모든 공지사항 정보',
    operation_description='모든 공지사항 정보를 리턴한다.',
    responses={
        '200': NoticeSerializer,
        '403': "Unauthorized access to accounts",
        '401': "Authentication credentials were not provided.",
    },
))
@method_decorator(name='retrieve', decorator=swagger_auto_schema(
    operation_id='지정된 공지사항 정보',
    operation_description='지정된 공지사항 정보를 리턴한다.',
    responses={
        '200': NoticeSerializer,
        '403': "Unauthorized access to accounts",
        '401': "Authentication credentials were not provided.",
    },
))
class NoticeViewSet(mixins.ListModelMixin,
                    mixins.RetrieveModelMixin,
                    viewsets.GenericViewSet):
    queryset = Notice.objects.all().order_by('id')
    serializer_class = NoticeSerializer


@method_decorator(name='partial_update', decorator=swagger_auto_schema(
    operation_id='Update MGT(Microsfot Graph Token)',
    operation_description='UPdate Microsoft Graph token',
    responses={
        '200': "Ok",
        '403': "Unauthorized access to accounts",
        '401': "Authentication credentials were not provided.",
    },
))
class MicrosoftGraphViewSet(mixins.UpdateModelMixin,
                            viewsets.GenericViewSet):
    queryset = MicrosoftGraph.objects.all().order_by('mid')
    serializer_class = MicrosoftGraphSerializer


class EventViewSet(viewsets.GenericViewSet):
    queryset = Site.objects.all().order_by('mid')

    def get_serializer_class(self):
        if self.action == 'passenger':
            return EventPassengerSerializer
        elif self.action == 'message':
            return EventMessageSerializer
        else:
            return EventSerializer

    @swagger_auto_schema(
        responses={
            '200': 'Ok',
            '404': "Not Found",
            '401': 'Authentication credentials were not provided.'
        },
        operation_id='안전요원 앱 차량 문열림/문닫힘 이벤트',
        operation_description='안전요원 앱에서 차량 문열림/문닫힘 이벤트 발생 통합관제로 전달 \
            <p style="color:Blue;"><b>열림 이면 True</b></p> <p style="color:Red;"><b>닫힘 이면 False</b></p>',
    )
    @action(detail=False, methods=['post'])
    def door(self, request, pk=None):
        vehicle = get_object_or_404(Vehicle, pk=request.data['vehicle_id'])
        serializer = VehicleSerializer(vehicle, many=False)
        data = {}
        content = {}
        content['vehicle_id'] = request.data['vehicle_id']
        content['vehicle_mid'] = serializer.data['mid']
        content['value'] = request.data['value']
        data["door"] = content
        # deprecated
        return Response('Ok', status=status.HTTP_200_OK)

    @swagger_auto_schema(
        responses={
            '200': 'Ok',
            '404': "Not Found",
            '401': 'Authentication credentials were not provided.'
        },
        operation_id='안전요원 앱 차량 자동/수동모드 이벤트',
        operation_description='안전요원 앱에서 차량 자동/수동모드 이벤트 발생 통합관제로 전달 \
            <p style="color:Blue;"><b>자동 이면 True</b></p> <p style="color:Red;"><b>수동 이면 False</b></p>',
    )
    @action(detail=False, methods=['post'])
    def drive(self, request, pk=None):
        vehicle = get_object_or_404(Vehicle, pk=request.data['vehicle_id'])
        serializer = VehicleSerializer(vehicle, many=False)
        data = {}
        content = {}
        content['vehicle_id'] = request.data['vehicle_id']
        content['vehicle_mid'] = serializer.data['mid']
        content['value'] = request.data['value']
        data["drive"] = content
        # deprecated
        return Response('Ok', status=status.HTTP_200_OK)

    @swagger_auto_schema(
        responses={
            '200': 'Ok',
            '404': "Not Found",
            '401': 'Authentication credentials were not provided.'
        },
        operation_id='안전요원 앱 차량 주차상태 이벤트',
        operation_description='안전요원 앱에서 차량 주차상태 이벤트 발생 통합관제로 전달 \
            <p style="color:Blue;"><b>주자중 이면 True</b></p> <p style="color:Red;"><b>주행중 이면 False</b></p>',
    )
    @action(detail=False, methods=['post'])
    def parking(self, request, pk=None):
        vehicle = get_object_or_404(Vehicle, pk=request.data['vehicle_id'])
        serializer = VehicleSerializer(vehicle, many=False)
        data = {}
        content = {}
        content['vehicle_id'] = request.data['vehicle_id']
        content['vehicle_mid'] = serializer.data['mid']
        content['value'] = request.data['value']
        data["parking"] = content
        return Response('Ok', status=status.HTTP_200_OK)

    @swagger_auto_schema(
        responses={
            '200': 'Ok',
            '404': "Not Found",
            '401': 'Authentication credentials were not provided.'
        },
        operation_id='안전요원 앱 차량 전원ON/OFF 이벤트',
        operation_description='안전요원 앱에서 차량 전원 On/Off 이벤트 발생 통합관제로 전달. \
            <p style="color:Blue;"><b>On 이면 True</b></p> <p style="color:Red;"><b>Off 이면 False</b></p>',
    )
    @action(detail=False, methods=['post'])
    def power(self, request, pk=None):
        vehicle = get_object_or_404(Vehicle, pk=request.data['vehicle_id'])
        serializer = VehicleSerializer(vehicle, many=False)
        data = {}
        content = {}
        content['vehicle_id'] = request.data['vehicle_id']
        content['vehicle_mid'] = serializer.data['mid']
        content['value'] = request.data['value']
        data["power"] = content
        # deprecated
        return Response('Ok', status=status.HTTP_200_OK)

    @swagger_auto_schema(
        responses={
            '200': 'Ok',
            '404': "Not Found",
            '401': 'Authentication credentials were not provided.'
        },
        operation_id='안전요원 앱 승객수 이벤트',
        operation_description='안전요원 앱에서 승객수(현재,누적수) 이벤트 발생 통합관제로 전달'
    )
    @action(detail=False, methods=['post'])
    def passenger(self, request, pk=None):
        vehicle = get_object_or_404(Vehicle, pk=request.data['vehicle_id'])
        serializer = VehicleSerializer(vehicle, many=False)
        data = {}
        content = {}
        content['vehicle_id'] = request.data['vehicle_id']
        content['vehicle_mid'] = serializer.data['mid']
        content['current_passenger'] = request.data['current_passenger']
        content['accumulated_passenger'] = request.data['accumulated_passenger']
        data["passenger"] = content
        # deprecated
        return Response('Ok', status=status.HTTP_200_OK)

    @swagger_auto_schema(
        responses={
            '200': 'Ok',
            '404': "Not Found",
            '401': 'Authentication credentials were not provided.'
        },
        operation_id='안전요원 앱 메시지 전송',
        operation_description='안전요원 앱에서 메시지 이벤트 발생 통합관제로 전달'
    )
    @action(detail=False, methods=['post'])
    def message(self, request, pk=None):
        vehicle = get_object_or_404(Vehicle, pk=request.data['vehicle_id'])
        serializer = VehicleSerializer(vehicle, many=False)
        data = {}
        content = {}
        content['vehicle_id'] = request.data['vehicle_id']
        content['vehicle_mid'] = serializer.data['mid']
        content['value'] = request.data['message']
        data["message"] = content
        # deprecated
        return Response('Ok', status=status.HTTP_200_OK)


@method_decorator(name='list', decorator=swagger_auto_schema(
    operation_id='모든 키오스크 광고 정보',
    operation_description='모든 키오스크 광고 정보를 리턴한다.',
    responses={
        '200': AdSerializer,
        '403': "Unauthorized access to accounts",
        '401': "Authentication credentials were not provided.",
    },
))
@method_decorator(name='retrieve', decorator=swagger_auto_schema(
    operation_id='지정된 키오스크 광고 정보',
    operation_description='지정된 키오스크 광공 정보를 리턴한다.',
    responses={
        '200': AdSerializer,
        '403': "Unauthorized access to accounts",
        '401': "Authentication credentials were not provided.",
    },
))
class AdViewSet(mixins.ListModelMixin,
                mixins.RetrieveModelMixin,
                viewsets.GenericViewSet):

    queryset = Advertisement.objects.all()
    serializer_class = AdSerializer

    @swagger_auto_schema(
        responses={
            '200': '{미정}',
            '404': "Not Found",
            '401': 'Authentication credentials were not provided.'
        },
        operation_id='요약된 모든 키오스크 광고 정보',
        operation_description='요약된 모든 키오스크 광고 정보를 리턴한다. \
            <p style="color:Red;"><b>구현 예정</b></p>',
    )
    @action(detail=False, methods=['get'])
    def summary(self, request, pk=None):
        return Response({'status': request.data})


@method_decorator(name='retrieve', decorator=swagger_auto_schema(
    operation_id='지정된 키오스크의 광고 정보',
    operation_description='지정된 키오스크의 광고 정보를 리턴한다.',
    responses={
        '200': AdSerializer,
        '403': "Unauthorized access to accounts",
        '401': "Authentication credentials were not provided.",
    },
))
class AdKioskViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = Advertisement.objects.all().order_by('mid')
    serializer_class = AdSerializer
