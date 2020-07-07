from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from datetime import datetime


class User(AbstractUser):
    ''' 이미 AbstractUser에서 정의 되어있음.
    https://github.com/django/django/blob/master/django/contrib/auth/models.py
    '''
    email = models.EmailField(_('email address'), unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return "{}".format(self.email)


class UserProfile(models.Model):
    USER_TYPE_CHOICES = (
        (1, 'operator'),
        (2, 'manager'),
        (3, 'supervisor'),
    )
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    team = models.CharField(max_length=50, blank=True, null=True)
    phone = models.CharField(max_length=25, default='000-0000-0000')
    level = models.PositiveSmallIntegerField(choices=USER_TYPE_CHOICES, default=1, verbose_name='level')
    photo = models.ImageField(upload_to='uploads', blank=True)

    def __str__(self):
        return self.user.email


class Manager(models.Model):
    username = models.CharField(max_length=50, blank=True, null=True, verbose_name=_('관리자 이름'))
    email = models.EmailField(verbose_name=_('관리자 이메일'), unique=True)
    USER_TYPE_CHOICES = (
        (1, 'operator'),
        (2, 'manager'),
        (3, 'supervisor'),
    )
    team = models.CharField(max_length=25, blank=True, null=True, verbose_name=_('관리자 소속'))
    phone = models.CharField(max_length=25, default='000-0000-0000', verbose_name=_('관리자 핸드폰'))
    level = models.PositiveSmallIntegerField(choices=USER_TYPE_CHOICES, default=1, verbose_name=_('접근권한'),
                                             help_text='1:Operator, 2:Manager, 3:Supervisor')
    photo = models.ImageField(upload_to='uploads', blank=True, verbose_name=_('관리자 사진'))

    def __str__(self):
        return self.email


class Weather(models.Model):
    '''
    weather, temp, timestamp
    '''
    pass


class Forecast(models.Model):
    '''
    weather, temp, hour
    '''
    pass


class AireQuality(models.Model):
    '''
    dust, microdust, ozone, nm
    '''
    pass


class Site(models.Model):
    mid = models.CharField(default='S000', max_length=25, verbose_name=_('운영장소 관리 ID'))
    name = models.CharField(max_length=50, blank=True, null=True, verbose_name=_('운영장소 이름'))
    summary = models.TextField(blank=True, null=True, verbose_name=_('운영장소 요약'))
    summary2 = models.TextField(blank=True, null=True, verbose_name=_('운영장소 요약2'))
    user = models.ManyToManyField(User, blank=True, verbose_name=_('관리자'))
    operation = models.BooleanField(default=False, verbose_name=_('운영중'))
    address = models.TextField(blank=True, null=True, verbose_name=_('운영장소주소'))
    image = models.ImageField(upload_to='uploads', blank=True, verbose_name=_('emergency contact'))
    current_weather = models.CharField(max_length=100, blank=True, null=True, verbose_name=_('현재날씨'))
    weather_forecast = models.CharField(max_length=300, blank=True, null=True, verbose_name=_('날씨예보'))
    air_quality = models.CharField(max_length=250, blank=True, null=True, verbose_name=_('대기상태'))

    def __str__(self):
        if not self.name:
            return self.mid
        else:
            return self.name


class Station(models.Model):
    mid = models.CharField(default='S000', max_length=25, verbose_name=_('정류소 관리 ID'))
    name = models.CharField(max_length=50, blank=True, null=True, verbose_name=_('정류소 이름'))
    user = models.ManyToManyField(User, blank=True, verbose_name=_('관리자'))
    operation = models.BooleanField(default=False, verbose_name=_('운영중'))
    lat = models.DecimalField(max_digits=22, decimal_places=16, blank=True, null=True, verbose_name=_('정류소 위도'))
    lon = models.DecimalField(max_digits=22, decimal_places=16, blank=True, null=True, verbose_name=_('정류소 경도'))
    site = models.ForeignKey(Site, blank=True, null=True, on_delete=models.CASCADE, verbose_name=_('운영장소'))
    eta = ArrayField(models.CharField(max_length=250), blank=True, null=True, default=list, verbose_name=_('Estimated time of arrival'))

    def __str__(self):
        if not self.name:
            return self.mid
        else:
            return self.name


class Advertisement(models.Model):
    image = models.ImageField(upload_to='uploads', blank=True, verbose_name=_('키오스크 광고이미지'))
    duration = models.TimeField(default='01:00:00', blank=True, verbose_name='광고 노출 시간')
    description = models.TextField(default='설명', blank=True, null=True, verbose_name=_('광고 설명'))

    def __str__(self):
        if not self.description:
            return '설명'
        return self.description


class Kiosk(models.Model):
    mid = models.CharField(default='K000', max_length=25, verbose_name=_('키오스크 관리 ID'))
    name = models.CharField(max_length=50, blank=True, null=True, verbose_name=_('키오스크 이름'))
    sn = models.CharField(max_length=50, blank=True, null=True, verbose_name=_('시리얼 번호'))
    user = models.ManyToManyField(User, blank=True, verbose_name=_('관리자'))
    operation = models.BooleanField(default=False, verbose_name=_('운영중'))
    lat = models.DecimalField(max_digits=22, decimal_places=16, blank=True, null=True, verbose_name=_('키오스크 위도'))
    lon = models.DecimalField(max_digits=22, decimal_places=16, blank=True, null=True, verbose_name=_('키오스크 경도'))
    site = models.ForeignKey(Site, blank=True, null=True, on_delete=models.CASCADE, verbose_name=_('운영장소'))
    password = models.DecimalField(max_digits=6, decimal_places=0, default=123456, blank=False, null=False, verbose_name=_('키오스크 암호'))
    ad = models.ManyToManyField(Advertisement, blank=True, verbose_name=_('키오스크 광고'))

    def __str__(self):
        if not self.name:
            return self.mid
        else:
            return self.name


class Garage(models.Model):
    mid = models.CharField(default='G000', max_length=25, verbose_name=_('차고지 관리 ID'))
    name = models.CharField(max_length=50, blank=True, null=True, verbose_name=_('차고지 이름'))
    lat = models.DecimalField(max_digits=22, decimal_places=16, blank=True, null=True, verbose_name=_('차고지 위도'))
    lon = models.DecimalField(max_digits=22, decimal_places=16, blank=True, null=True, verbose_name=_('차고지 경도'))
    door = models.BooleanField(default=False, verbose_name=_('차고지 문열림'))
    temperature = models.FloatField(blank=True, null=True, verbose_name=_('차고지 온도'))
    humidity = models.FloatField(blank=True, null=True, verbose_name=_('차고지 습도'))
    charger = models.BooleanField(default=False, verbose_name=_('차고지 충전유무'))
    site = models.ForeignKey(Site, blank=True, null=True, on_delete=models.CASCADE, verbose_name=_('운영장소'))
    user = models.ManyToManyField(User, blank=True, verbose_name=_('관리자'))
    operation = models.BooleanField(default=False, verbose_name=_('운영중'))

    def __str__(self):
        if not self.name:
            return self.mid
        else:
            return self.name


class Route(models.Model):
    mid = models.CharField(default='R000', max_length=25, verbose_name=_('경로 관리 ID'))
    name = models.CharField(max_length=50, blank=True, null=True, verbose_name=_('경로 이름'))
    start = ArrayField(models.DecimalField(max_digits=22, decimal_places=16), blank=True, null=True, default=list, verbose_name=_('경로시작위치'))
    end = ArrayField(models.DecimalField(max_digits=22, decimal_places=16), blank=True, null=True, default=list, verbose_name=_('경로끝위치'))
    site = models.ForeignKey(Site, blank=True, null=True, on_delete=models.CASCADE, verbose_name=_('운영장소'))
    operation = models.BooleanField(default=False, verbose_name=_('운영중'))

    def __str__(self):
        if not self.name:
            return self.mid
        else:
            return self.name


class Navya(models.Model):
    vin = models.CharField(max_length=25, blank=True, verbose_name=_('VIN'))
    firmware = models.CharField(max_length=25, blank=True, verbose_name=_('Firmware version'))

    def __str__(self):
        return self.vin


class Kamo(models.Model):
    vin = models.CharField(max_length=25, blank=True, verbose_name=_('VIN'))
    firmware = models.CharField(max_length=25, blank=True, verbose_name=_('Firmware version'))

    def __str__(self):
        return self.vin


class Easymile(models.Model):
    vin = models.CharField(max_length=25, blank=True, verbose_name=_('VIN'))
    firmware = models.CharField(max_length=25, blank=True, verbose_name=_('Firmware version'))

    def __str__(self):
        return self.vin


class Fleet(models.Model):
    types = ['Navya', 'Kamo', 'Easymile']
    MODEL_TYPE = (
        (0, types[0]),
        (1, types[1]),
        (2, types[2]),
    )
    vin = models.CharField(max_length=25, blank=True, verbose_name=_('VIN'))
    firmware = models.CharField(max_length=25, blank=True, verbose_name=_('Firmware version'))
    modeltype = models.PositiveSmallIntegerField(choices=MODEL_TYPE, default=0, verbose_name=_('Model type'))

    def __str__(self):
        return self.types[self.modeltype] + ' ' + self.vin


def get_oddfile_path(instance, filename):
    return '/'.join(['odd', str(instance.id), filename])


class Vehicle(models.Model):
    OPERATION_MODE_CHOICES = (
        (1, 'always'),
        (2, 'event'),
        (3, 'test'),
    )
    STATE_CHOICES = (
        (1, 'closed'),
        (2, 'pending'),
        (3, 'open'),
        (4, 'operating'),
    )
    DRIVE_MODE_CHOICES = (
        (1, 'dynamic'),
        (2, 'static'),
        (3, 'test'),
        (4, 'static&dynamic'),
    )
    mid = models.CharField(default='V000', max_length=25, verbose_name=_('차량 관리 ID'))
    name = models.CharField(max_length=50, blank=True, null=True, verbose_name=_('차량 이름'))
    licence = models.CharField(max_length=50, blank=True, null=True, verbose_name=_('차량 라이선스'))
    drive = models.BooleanField(default=False, blank=True, null=True, verbose_name=_('차량 운행중'))
    gnss = models.BooleanField(default=False, blank=True, null=True, verbose_name=_('GNSS 작동중'))
    speed = models.IntegerField(blank=True, null=True, verbose_name=_('차량 속도'))
    hitratio = models.IntegerField(blank=True, null=True, verbose_name=_('GNSS 감도'))
    battery = models.IntegerField(blank=True, null=True, verbose_name=_('Battery 상태'))
    passenger = models.IntegerField(blank=True, null=True, verbose_name=_('현재탑승객수'))
    heading = models.IntegerField(blank=True, null=True, verbose_name=_('차량 방향'))
    lights = ArrayField(models.BooleanField(default=False), blank=True, null=True, default=list, verbose_name=_('차량 Light유무'))
    door = models.BooleanField(default=False, blank=True, null=True, verbose_name=_('문열림'))
    user = models.ManyToManyField(User, blank=True, verbose_name=_('관리자'))
    site = models.ForeignKey(Site, blank=True, null=True, on_delete=models.CASCADE, verbose_name=_('장소'))
    model = models.ForeignKey(Fleet, blank=True, null=True, on_delete=models.CASCADE, verbose_name=_('차량 모델'))
    lat = models.DecimalField(max_digits=22, decimal_places=16, blank=True, null=True, verbose_name=_('차량 위도'))
    lon = models.DecimalField(max_digits=22, decimal_places=16, blank=True, null=True, verbose_name=_('차량 경도'))
    operation_mode = models.PositiveSmallIntegerField(choices=OPERATION_MODE_CHOICES, default=1, blank=True, null=True, verbose_name=_('운행모드'))
    state = models.PositiveSmallIntegerField(choices=STATE_CHOICES, default=1, blank=True, null=True, verbose_name=_('상태'))
    drive_mode = models.PositiveSmallIntegerField(choices=DRIVE_MODE_CHOICES, default=1, blank=True, null=True, verbose_name=_('주행모드'))
    webcam1 = models.URLField(blank=True, null=True, verbose_name=_('카메라#1 URL'))
    webcam2 = models.URLField(blank=True, null=True, verbose_name=_('카메라#2 URL'))
    webcam3 = models.URLField(blank=True, null=True, verbose_name=_('카메라#3 URL'))
    webcam4 = models.URLField(blank=True, null=True, verbose_name=_('카메라#4 URL'))
    distance = models.FloatField(blank=True, null=True, verbose_name=_('운행중 누적거리(km)'))
    brakeactuator = models.FloatField(blank=True, null=True, verbose_name=_('브레이크 모터'))
    parkingbrake = models.FloatField(blank=True, null=True, verbose_name=_('주차 브레이크'))
    rpm = models.FloatField(blank=True, null=True, verbose_name=_('차량 RPM'))
    odd = models.FileField(upload_to=get_oddfile_path, blank=True, null=True, verbose_name='ODD 파일')
    wheelbase_speed = models.FloatField(blank=True, null=True, verbose_name=_('휠기반 차량 속도'))
    isparked = models.BooleanField(default=False, blank=True, null=True, verbose_name=_('주차여부'))
    passed_station = models.ForeignKey(Station, blank=True, null=True, on_delete=models.CASCADE, verbose_name=_('막지나온역'))
    eta = ArrayField(models.CharField(max_length=250), blank=True, null=True, default=list, verbose_name=_('Estimated time of arrival'))
    # v2x
    # remove light

    def __str__(self):
        if not self.name:
            return self.mid
        else:
            return self.name


class OperationIssue(models.Model):
    text = models.TextField(blank=True, null=True, verbose_name=_('주요이슈'))

    def __str__(self):
        return self.text


class OperationQuestion(models.Model):
    text = models.TextField(blank=True, null=True, verbose_name=_('주요질문'))

    def __str__(self):
        return self.text


class OperationLog(models.Model):
    WEATHER_TYPE_CHOICES = (
        (1, 'sunny'),
        (2, 'cloudy'),
        (3, 'rainy'),
        (4, 'snowing'),
        (5, 'windy'),
        (6, 'foggy'),
    )
    EVENT_TYPE_CHOICES = (
        (1, 'inspection'),
        (2, 'testing'),
        (3, 'demo'),
        (4, 'exhibition'),
    )
    created_on = models.DateTimeField(auto_now=True, blank=True, verbose_name=_('생성시간'))
    time_start = models.DateTimeField(blank=True, null=True, verbose_name=_('시작시간'))
    time_end = models.DateTimeField(blank=True, null=True, verbose_name=_('종료시간'))
    vehicle = models.ForeignKey(Vehicle, blank=True, null=True, on_delete=models.CASCADE, verbose_name=_('차량 관리 ID'))
    issue = models.ManyToManyField(OperationIssue, blank=True, verbose_name=_('주요이슈'))
    question = models.ManyToManyField(OperationQuestion, blank=True, verbose_name=_('주요질문'))
    distance = models.FloatField(blank=True, null=True, verbose_name=_('하루누적주행거리(km)'))
    passenger = models.IntegerField(blank=True, null=True, verbose_name=_('하루누적탑승객수(명)'))
    user = models.ManyToManyField(User, blank=True, verbose_name=_('오퍼레이터'))
    event = models.PositiveSmallIntegerField(choices=EVENT_TYPE_CHOICES, default=1, blank=True, null=True, verbose_name=_('이벤트'))
    task = models.TextField(blank=True, null=True, verbose_name=_('Task'))
    weather = models.PositiveSmallIntegerField(choices=WEATHER_TYPE_CHOICES, default=1, blank=True, null=True, verbose_name=_('하루평균날씨'))
    temperature = models.FloatField(blank=True, null=True, verbose_name=_('하루평균실외온도'))


class V2X(models.Model):
    mid = models.CharField(default='VX000', max_length=25, verbose_name=_('V2X 관리 ID'))
    name = models.CharField(max_length=50, blank=True, null=True, verbose_name=_('V2X 이름'))
    user = models.ManyToManyField(User, blank=True, verbose_name=_('관리자'))
    operation = models.BooleanField(default=False, verbose_name=_('작동중'))
    lat = models.DecimalField(max_digits=22, decimal_places=16, blank=True, null=True, verbose_name=_('V2X 위도'))
    lon = models.DecimalField(max_digits=22, decimal_places=16, blank=True, null=True, verbose_name=_('V2X 경도'))
    site = models.ForeignKey(Site, blank=True, null=True, on_delete=models.CASCADE, verbose_name=_('운영장소'))

    def __str__(self):
        if not self.name:
            return self.mid
        else:
            return self.name


class DataHub(models.Model):
    mid = models.CharField(default='DC000', max_length=25, verbose_name=_('데이터허브 관리 ID'))
    name = models.CharField(max_length=50, blank=True, null=True, verbose_name=_('데이터허브 이름'))
    user = models.ManyToManyField(User, blank=True, verbose_name=_('관리자'))
    operation = models.BooleanField(default=False, verbose_name=_('작동중'))
    lat = models.DecimalField(max_digits=22, decimal_places=16, blank=True, null=True, verbose_name=_('데이터허브 위도'))
    lon = models.DecimalField(max_digits=22, decimal_places=16, blank=True, null=True, verbose_name=_('데이터허브 경도'))
    summary = models.TextField(blank=True, null=True, verbose_name=_('데이터허브 요약'))
    address = models.TextField(blank=True, null=True, verbose_name=_('데이터허브 주소'))
    site = models.ForeignKey(Site, blank=True, null=True, on_delete=models.CASCADE, verbose_name=_('운영장소'))

    def __str__(self):
        if not self.name:
            return self.mid
        else:
            return self.name


class Notice(models.Model):
    TYPE_CHOICES = (
        (1, 'Common'),
        (2, 'integrated control'),
        (3, 'integrated dashboard')
    )
    created_on = models.DateTimeField(auto_now_add=True, null=True)
    updated_on = models.DateTimeField(auto_now=True)
    title = models.CharField(default='title', max_length=50, blank=True, null=True, verbose_name=_('제목'))
    category = models.PositiveSmallIntegerField(choices=TYPE_CHOICES, default=1, blank=True, null=True, verbose_name=_('구분'))
    contents = models.TextField(blank=True, null=True, verbose_name=_('내용'))
    pin = models.BooleanField(default=False, verbose_name=_('고정유무'))

    def __str__(self):
        return self.title


class MicrosoftGraph(models.Model):

    created_on = models.DateTimeField(auto_now_add=True, null=True)
    updated_on = models.DateTimeField(auto_now=True)
    token = models.TextField(blank=True, null=True, verbose_name=_('token'))
