from rest_framework import serializers
from api.models import User, UserProfile, Site, Station, Kiosk, Vehicle, Garage, Route, OperationLog, Manager, \
    V2X, DataHub, Notice, MicrosoftGraph, Navya, Kamo, Easymile, Fleet, Advertisement


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ('team', 'phone', 'level', 'photo')

# 비밀번호 변경을 위한 추가
# https://www.it-swarm.dev/ko/python/django-rest-framework%EC%97%90%EC%84%9C-%EC%82%AC%EC%9A%A9%EC%9E%90-%EB%B9%84%EB%B0%80%EB%B2%88%ED%98%B8%EB%A5%BC-%EC%97%85%EB%8D%B0%EC%9D%B4%ED%8A%B8%ED%95%98%EB%8A%94-%EB%B0%A9%EB%B2%95%EC%9D%80-%EB%AC%B4%EC%97%87%EC%9E%85%EB%8B%88%EA%B9%8C/827091059/
class ChangePasswordSerializer(serializers.Serializer):

    """
    Serializer for password change endpoint.
    """
    e_mail_id = serializers.EmailField()
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    confirm_new_password = serializers.CharField(required=True)


class UserSerializer(serializers.HyperlinkedModelSerializer):
    profile = UserProfileSerializer(required=True)
    username = serializers.SerializerMethodField('get_full_name')

    class Meta:
        model = User
        '''
        https://github.com/django/django/blob/master/django/contrib/auth/models.py
        에서 확인해보면 first_name, last_name, username과 get_full_name과 같은 함수가
        정의 되어 있음.
        '''
        fields = ('pk', 'url', 'email', 'username', 'password', 'profile')
        extra_kwargs = {'password': {'write_only': True}}

    def get_full_name(self, obj):
        full_name = '%s %s' % (obj.last_name, obj.first_name)
        return full_name.strip()

    def create(self, validated_data):
        profile_data = validated_data.pop('profile')
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        UserProfile.objects.create(user=user, **profile_data)
        return user

    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile')
        profile = instance.profile

        instance.email = validated_data.get('email', instance.email)
        instance.save()

        profile.team = profile_data.get('team', profile.team)
        profile.phone = profile_data.get('phone', profile.phone)
        profile.level = profile_data.get('level', profile.level)
        profile.photo = profile_data.get('photo', profile.photo)
        profile.save()

        return instance


class SiteSummarySerializer(serializers.Serializer):
    vehicle_count = serializers.IntegerField(label='총 차량 개수')
    station_count = serializers.IntegerField(label='총 정류장 개수')
    kiosk_count = serializers.IntegerField(label='총 키오스크 개수')
    garage_count = serializers.IntegerField(label='총 차고지 개수')
    route_count = serializers.IntegerField(label='총 경로 개수')
    datahub_count = serializers.IntegerField(label='총 데이터허브 개수')
    manager_count = serializers.IntegerField(label='총 관리자 스')


class SiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Site
        fields = '__all__'

class SitePartialUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Site
        fields = ('current_weather', 'weather_forecast', 'air_quality')

class StationListSerializer(serializers.ModelSerializer):
    iskiosk = serializers.BooleanField(default=False, label='kiosk 존재 유무')

    class Meta:
        model = Station
        fields = ('id', 'mid', 'name', 'operation', 'lat', 'lon', 'site', 'iskiosk')


class StationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Station
        fields = '__all__'


class KioskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Kiosk
        fields = '__all__'


class VehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = '__all__'


class NavyaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Navya
        fields = '__all__'


class KamoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Kamo
        fields = '__all__'


class EasymileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Easymile
        fields = '__all__'


class FleetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fleet
        fields = '__all__'


class VehicleGetResponseSerializer(serializers.ModelSerializer):
    model = FleetSerializer()

    class Meta:
        model = Vehicle
        fields = '__all__'


class GarageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Garage
        fields = '__all__'


class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = '__all__'


class OperationLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = OperationLog
        fields = '__all__'


class OperationLogSummarySerializer(serializers.Serializer):
    vehicle = serializers.CharField(max_length=200, label='차량 이름')
    accum_passenger = serializers.IntegerField(label='누적 승객수')
    accum_distance = serializers.IntegerField(label='누적 운행거리')
    accum_dvr_volume = serializers.IntegerField(label='누적 데이터 용량')


class ManagerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Manager
        fields = '__all__'


class ManagerLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(max_length=200, label='관리자 암호')


class ManagerEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()


class ManagerMessageSerializer(serializers.Serializer):
    email = serializers.EmailField()
    message = serializers.CharField(max_length=512, label='메시지')


class V2XSerializer(serializers.ModelSerializer):
    class Meta:
        model = V2X
        fields = '__all__'


class DataHubSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataHub
        fields = '__all__'


class VehiclePartialUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = ('drive', 'gnss', 'speed', 'hitratio', 'battery', 'passenger', 'heading',
                  'door', 'lat', 'lon', 'isparked', 'operation_mode', 'state', 'drive_mode',
                  'webcam1', 'webcam2', 'webcam3', 'distance', 'rpm', 'brakeactuator', 'parkingbrake',
                  'passed_station', 'eta','latest_power_on', 'latest_power_off')


class OperationLogPartialUpdateSerializer(serializers.Serializer):
    utc_time = serializers.CharField(max_length=200, label='차량시작/종료 time(UTC)')
    vehicle_id = serializers.CharField(max_length=200, label='차량 ID')


class OperationLogPartial2UpdateSerializer(serializers.Serializer):
    passenger = serializers.CharField(max_length=200, label='현재 차량 탑승객수')
    vehicle_id = serializers.CharField(max_length=200, label='차량 ID')


class NoticeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notice
        fields = '__all__'


class MicrosoftGraphSerializer(serializers.ModelSerializer):
    class Meta:
        model = MicrosoftGraph
        fields = '__all__'


class EventSerializer(serializers.Serializer):
    vehicle_id = serializers.IntegerField(max_value=None, min_value=None, label='차량 ID(PK)')
    value = serializers.BooleanField(default=False, label='True/False')


class EventPassengerSerializer(serializers.Serializer):
    vehicle_id = serializers.IntegerField(max_value=None, min_value=None, label='차량 ID(PK)')
    current_passenger = serializers.IntegerField(max_value=None, min_value=0, label='현재 승객수')
    accumulated_passenger = serializers.IntegerField(max_value=None, min_value=0, label='현재 누적된 승객수')


class EventMessageSerializer(serializers.Serializer):
    vehicle_id = serializers.IntegerField(max_value=None, min_value=None, label='차량 ID(PK)')
    message = serializers.CharField(max_length=200, label='메시지')


class OperationLogByDatepdateSerializer(serializers.Serializer):
    date = serializers.DateField(format="%Y/%m/%d", input_formats=["%Y-%m-%d"])


class AdSerializer(serializers.ModelSerializer):
    class Meta:
        model = Advertisement
        fields = '__all__'
