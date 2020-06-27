from django.contrib import admin

# Register your models here.
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.safestring import mark_safe
from django.utils.html import format_html, format_html_join
from api.models import User, UserProfile, Site, Station, Kiosk, Vehicle, Garage, \
    Route, OperationLog, OperationIssue, OperationQuestion, Navya, Kamo, Easymile, \
    V2X, DataHub, Notice, MicrosoftGraph, Fleet, Advertisement


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2'),
        }),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser')}),
    )
    list_display = ('email', 'username', 'is_staff', 'is_superuser')
    search_fields = ('email', 'username')
    ordering = ('email',)
    inlines = (UserProfileInline, )


class ManagerAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'team', 'phone', 'level')


class SiteAdmin(admin.ModelAdmin):
    list_display = ('mid', 'name', 'get_user', 'summary')

    def get_user(self, obj):
        return format_html_join(mark_safe('<br/>'), '<li>{}</li>', ((p.email,) for p in obj.user.all()))
    get_user.short_description = '관리자'


class StationAdmin(admin.ModelAdmin):
    list_display = ('mid', 'name', 'site__name', 'user__email')

    def site__name(self, obj):
        if not obj.site:
            return '미지정'
        return str(obj.site.name)
    site__name.short_description = '운영장소 이름'

    def user__email(self, obj):
        return format_html_join(mark_safe('<br/>'), '<li>{}</li>', ((p.email,) for p in obj.user.all()))
    user__email.short_description = '관리자'


class KioskAdmin(admin.ModelAdmin):
    list_display = ('mid', 'name', 'site__name', 'user__email', 'operation')

    def site__name(self, obj):
        if not obj.site:
            return '미지정'
        return str(obj.site.name)
    site__name.short_description = '운영장소 이름'

    def user__email(self, obj):
        return format_html_join(mark_safe('<br/>'), '<li>{}</li>', ((p.email,) for p in obj.user.all()))
    user__email.short_description = '관리자'


class VehicleAdmin(admin.ModelAdmin):
    list_display = ('mid', 'name', 'site__name', 'user__email', 'gnss', 'speed', 'battery', 'passenger', 'heading', 'door')

    def site__name(self, obj):
        if not obj.site:
            return '미지정'
        return str(obj.site.name)
    site__name.short_description = '운영장소 이름'

    def user__email(self, obj):
        return format_html_join(mark_safe('<br/>'), '<li>{}</li>', ((p.email,) for p in obj.user.all()))
    user__email.short_description = '관리자'


class GarageAdmin(admin.ModelAdmin):
    list_display = ('mid', 'name', 'site__name', 'user__email')

    def site__name(self, obj):
        if not obj.site:
            return '미지정'
        return str(obj.site.name)
    site__name.short_description = '운영장소 이름'

    def user__email(self, obj):
        return format_html_join(mark_safe('<br/>'), '<li>{}</li>', ((p.email,) for p in obj.user.all()))
    user__email.short_description = '관리자'


class RouteAdmin(admin.ModelAdmin):
    list_display = ('mid', 'name', 'site__name')

    def site__name(self, obj):
        if not obj.site:
            return '미지정'
        return str(obj.site.name)
    site__name.short_description = '운영장소 이름'


class OperationLogAdmin(admin.ModelAdmin):
    list_display = ('vehicle', 'time_start_str', 'time_end_str', 'distance', 'passenger', 'issue__text', 'question__text', 'task', 'weather')

    def time_start_str(self, obj):
        if not obj.time_start:
            return ""
        return obj.time_start.strftime('%Y년 %m월-%d일 %H:%M')
    time_start_str.short_description = '시작시간'

    def time_end_str(self, obj):
        if not obj.time_end:
            return ""
        return obj.time_end.strftime('%Y년 %m월-%d일 %H:%M')
    time_end_str.short_description = '종료시간'

    def issue__text(self, obj):
        return format_html_join(mark_safe('<br/>'), '<li>{}</li>', ((p.text,) for p in obj.issue.all()))
    issue__text.short_description = '주요이슈'

    def question__text(self, obj):
        return format_html_join(mark_safe('<br/>'), '<li>{}</li>', ((p.text,) for p in obj.question.all()))
    question__text.short_description = '주요질문'


class V2XAdmin(admin.ModelAdmin):
    list_display = ('mid', 'name', 'site__name')

    def site__name(self, obj):
        if not obj.site:
            return '미지정'
        return str(obj.site.name)
    site__name.short_description = '운영장소 이름'


class DataHubAdmin(admin.ModelAdmin):
    list_display = ('mid', 'name', 'get_user', 'summary')

    def get_user(self, obj):
        return format_html_join(mark_safe('<br/>'), '<li>{}</li>', ((p.email,) for p in obj.user.all()))
    get_user.short_description = '관리자'


@admin.register(Navya)
class NavyaAdmin(admin.ModelAdmin):
    pass


@admin.register(Kamo)
class KamoAdmin(admin.ModelAdmin):
    pass


@admin.register(Easymile)
class EasymileAdmin(admin.ModelAdmin):
    pass


@admin.register(MicrosoftGraph)
class MicrosoftGraphAdmin(admin.ModelAdmin):
    pass


class NoticeAdmin(admin.ModelAdmin):
    list_display = ('created_on', 'updated_on', 'title', 'category', 'contents', 'pin')


@admin.register(Fleet)
class FleetAdmin(admin.ModelAdmin):
    pass


@admin.register(Advertisement)
class AdAdmin(admin.ModelAdmin):
    pass


admin.site.register(Site, SiteAdmin)
admin.site.register(Station, StationAdmin)
admin.site.register(Kiosk, KioskAdmin)
admin.site.register(Vehicle, VehicleAdmin)
admin.site.register(Garage, GarageAdmin)
admin.site.register(Route, RouteAdmin)
admin.site.register(OperationLog, OperationLogAdmin)
# admin.site.register(Manager, ManagerAdmin)
admin.site.register(OperationIssue)
admin.site.register(OperationQuestion)
admin.site.register(V2X, V2XAdmin)
admin.site.register(DataHub, DataHubAdmin)
admin.site.register(Notice, NoticeAdmin)
