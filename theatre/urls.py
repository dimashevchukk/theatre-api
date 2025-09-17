from django.urls import path, include
from rest_framework import routers

from theatre.views import (
    ActorViewSet,
    GenreViewSet,
    PlayViewSet,
    TheatreHallViewSet,
    PerformanceViewSet,
    TicketViewSet,
    ReservationViewSet,
)

app_name = "theatre"

router = routers.DefaultRouter()
router.register("actors", ActorViewSet)
router.register("genres", GenreViewSet)
router.register("plays", PlayViewSet)
router.register("theatre-halls", TheatreHallViewSet)
router.register("performances", PerformanceViewSet)
router.register("tickets", TicketViewSet)
router.register("reservations", ReservationViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
