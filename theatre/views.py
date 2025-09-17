from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAdminUser, IsAuthenticated

from theatre.permissions import IsAdminOrReadOnly
from theatre.models import (
    Actor,
    Genre,
    Play,
    TheatreHall,
    Performance,
    Ticket,
    Reservation,
)
from theatre.serializers import (
    ActorSerializer,
    ActorListSerializer,
    ActorDetailSerializer,
    GenreSerializer,
    GenreDetailSerializer,
    PlaySerializer,
    PlayListSerializer,
    PlayDetailSerializer,
    TheatreHallSerializer,
    TheatreHallListSerializer,
    TheatreHallDetailSerializer,
    PerformanceSerializer,
    PerformanceListSerializer,
    PerformanceDetailSerializer,
    TicketSerializer,
    TicketDetailSerializer,
    ReservationSerializer,
    ReservationDetailSerializer,
    ReservationCreateSerializer,
)


class ActorViewSet(ModelViewSet):
    queryset = Actor.objects.all()

    def get_queryset(self):
        if self.action in ["list", "retrieve"]:
            return self.queryset.prefetch_related("plays")
        return self.queryset

    def get_serializer_class(self):
        if self.action == "list":
            return ActorListSerializer
        if self.action == "retrieve":
            return ActorDetailSerializer
        return ActorSerializer


class GenreViewSet(ModelViewSet):
    queryset = Genre.objects.all()

    def get_queryset(self):
        if self.action == "retrieve":
            return self.queryset.prefetch_related("plays")
        return self.queryset

    def get_serializer_class(self):
        if self.action == "retrieve":
            return GenreDetailSerializer
        return GenreSerializer


class PlayViewSet(ModelViewSet):
    queryset = Play.objects.all()

    def get_queryset(self):
        if self.action in ["list", "retrieve"]:
            return self.queryset.prefetch_related("actors", "genres")
        return self.queryset

    def get_serializer_class(self):
        if self.action == "list":
            return PlayListSerializer
        if self.action == "retrieve":
            return PlayDetailSerializer
        return PlaySerializer


class TheatreHallViewSet(ModelViewSet):
    queryset = TheatreHall.objects.all()

    def get_queryset(self):
        if self.action in ["list", "retrieve"]:
            return self.queryset.prefetch_related("performances")
        return self.queryset

    def get_serializer_class(self):
        if self.action == "list":
            return TheatreHallListSerializer
        if self.action == "retrieve":
            return TheatreHallDetailSerializer
        return TheatreHallSerializer


class PerformanceViewSet(ModelViewSet):
    queryset = Performance.objects.all()

    def get_queryset(self):
        if self.action in ["list", "retrieve"]:
            return self.queryset.select_related("theatre_hall", "play")
        return self.queryset

    def get_serializer_class(self):
        if self.action == "list":
            return PerformanceListSerializer
        if self.action == "retrieve":
            return PerformanceDetailSerializer
        return PerformanceSerializer


class TicketViewSet(ModelViewSet):
    queryset = Ticket.objects.all()

    def get_queryset(self):
        if self.action in ["list", "retrieve"]:
            return self.queryset.select_related("performance", "reservation").filter(
                reservation__user=self.request.user.id
            )
        return self.queryset

    def get_serializer_class(self):
        if self.action == "retrieve":
            return TicketDetailSerializer
        return TicketSerializer

    def get_permissions(self):
        if self.action in ["list", "retrieve", "destroy"]:
            return [IsAuthenticated()]
        return [IsAdminOrReadOnly()]


class ReservationViewSet(ModelViewSet):
    queryset = Reservation.objects.all()

    def get_queryset(self):
        if self.action in ["list", "retrieve"]:
            return (
                self.queryset.filter(user=self.request.user.id)
                .select_related("user")
                .prefetch_related("tickets")
            )
        return self.queryset

    def get_serializer_class(self):
        if self.action == "create":
            return ReservationCreateSerializer
        if self.action == "retrieve":
            return ReservationDetailSerializer
        return ReservationSerializer

    def get_permissions(self):
        if self.action in ["create", "list", "retrieve", "destroy"]:
            return [IsAuthenticated()]
        return [IsAdminUser()]
