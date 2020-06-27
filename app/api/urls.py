from django.urls import path, include
from rest_framework import routers
from api.views import UserViewSet, SiteViewSet, StationViewSet, KioskViewSet, VehicleViewSet, \
    GarageViewSet, RouteViewSet, OperationLogViewSet, ManagerViewSet, V2XViewSet, DataHubViewSet, \
    NoticeViewSet, MicrosoftGraphViewSet, OperationLogVehicleViewSet, EventViewSet, AdViewSet, AdKioskViewSet

router = routers.DefaultRouter()

# table CRUD api
router.register(r'users', UserViewSet)
router.register(r'sites', SiteViewSet)
router.register(r'stations', StationViewSet)
router.register(r'kiosks', KioskViewSet)
router.register(r'vehicles', VehicleViewSet)
router.register(r'garages', GarageViewSet)
router.register(r'routes', RouteViewSet)
router.register(r'oplogs', OperationLogViewSet)
router.register(r'oplogs/vehicle', OperationLogVehicleViewSet)
# router.register(r'managers', ManagerViewSet)
router.register(r'v2x', V2XViewSet)
router.register(r'datahub', DataHubViewSet)
router.register(r'notice', NoticeViewSet)
router.register(r'graph', MicrosoftGraphViewSet)
router.register(r'event', EventViewSet)
router.register(r'ad', AdViewSet)
router.register(r'ad/kiosk', AdKioskViewSet)

# function api
# site summery
# vehicle summery
# password request
# call manager
#
urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('rest_auth.urls')),
]
