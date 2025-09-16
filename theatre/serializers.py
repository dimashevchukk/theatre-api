from django.utils import timezone
from rest_framework import serializers

from theatre.models import Actor, Genre, Play, TheatreHall, Performance, Ticket, Reservation


class ActorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Actor
        fields = ["id", "first_name", "last_name"]


class ActorListSerializer(ActorSerializer):
    class Meta(ActorSerializer.Meta):
        fields = ["id", "full_name", "plays"]


class ActorDetailSerializer(ActorSerializer):
    plays = serializers.StringRelatedField(many=True, read_only=True)

    class Meta(ActorSerializer.Meta):
        fields = ActorSerializer.Meta.fields + ["plays"]


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ["id", "name"]


class GenreDetailSerializer(GenreSerializer):
    plays = serializers.StringRelatedField(many=True, read_only=True)

    class Meta(GenreSerializer.Meta):
        fields = GenreSerializer.Meta.fields + ["plays"]


class PlaySerializer(serializers.ModelSerializer):
    class Meta:
        model = Play
        fields = ["id", "title", "description", "actors", "genres"]


class PlayListSerializer(PlaySerializer):
    class Meta(PlaySerializer.Meta):
        fields = ["id", "title", "actors", "genres"]


class PlayDetailSerializer(PlaySerializer):
    actors = ActorListSerializer(many=True, read_only=True)
    genres = GenreSerializer(many=True, read_only=True)


class TheatreHallSerializer(serializers.ModelSerializer):
    class Meta:
        model = TheatreHall
        fields = ["id", "name", "rows", "seats_in_row"]


class TheatreHallListSerializer(TheatreHallSerializer):
    class Meta(TheatreHallSerializer.Meta):
        fields = ["id", "name", "capacity", "performances"]


class TheatreHallDetailSerializer(TheatreHallSerializer):
    performances = serializers.StringRelatedField(many=True, read_only=True)

    class Meta(TheatreHallSerializer.Meta):
        fields = TheatreHallSerializer.Meta.fields + [
            "capacity", "performances"
        ]


class PerformanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Performance
        fields = ["id", "play", "theatre_hall", "show_time"]

    def validate_show_time(self, show_time):
        if show_time < timezone.now():
            raise serializers.ValidationError(
                "Show time cannot be in the past."
            )
        return show_time


class PerformanceListSerializer(PerformanceSerializer):
    theatre_hall = serializers.SlugRelatedField(
        slug_field="name", read_only=True
    )


class PerformanceDetailSerializer(PerformanceSerializer):
    play = PlaySerializer(read_only=True)
    theatre_hall = TheatreHallSerializer(read_only=True)


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ["id", "row", "seat", "performance", "reservation"]


class TicketDetailSerializer(TicketSerializer):
    performance = PerformanceDetailSerializer(read_only=True)
    reservation = serializers.SlugRelatedField(
        slug_field="created_at", read_only=True
    )


class ReservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservation
        fields = ["id", "created_at", "user", "tickets"]


class ReservationDetailSerializer(ReservationSerializer):
    tickets = TicketDetailSerializer(many=True, read_only=True)


class ReservationCreateSerializer(ReservationSerializer):
    seats = serializers.ListField(
        child=serializers.DictField(
            child=serializers.IntegerField()
        ),
        write_only=True
    )
    performance = serializers.PrimaryKeyRelatedField(
        queryset=Performance.objects.all(), write_only=True
    )

    class Meta(ReservationSerializer.Meta):
        fields = ["id", "created_at", "seats", "performance"]

    def create(self, validated_data):
        user = self.context["request"].user
        seats = validated_data.pop("seats")
        performance = validated_data.pop("performance")
        reservation = Reservation.objects.create(
            user=user, **validated_data
        )

        tickets = []
        for seat in seats:
            row = seat["row"]
            seat_num = seat["seat"]

            tickets.append(
                Ticket(
                    reservation=reservation,
                    performance=performance,
                    row=row,
                    seat=seat_num
                )
            )

        Ticket.objects.bulk_create(tickets)
        return reservation
