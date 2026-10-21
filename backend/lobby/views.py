import random

from django.db import transaction
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from games.models import Game, Player
from .models import WaitingEntry


def is_busy(user):
    return Player.objects.filter(user=user, game__status__in=["waiting", "active"]).exists()


def form_game():
    with transaction.atomic():
        free = [e for e in WaitingEntry.objects.all() if not is_busy(e.user)]
        if len(free) < 3:
            return None

        chosen = random.sample(free, 3)
        game = Game.objects.create()
        for entry, color in zip(chosen, ["red", "green", "blue"]):
            Player.objects.create(game=game, user=entry.user, color=color, score=0)
            entry.delete()
        return game


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def join(request):
    if is_busy(request.user):
        return Response({"errors": {"detail": ["Already in a game."]}}, status=409)
    if WaitingEntry.objects.filter(user=request.user).exists():
        return Response({"errors": {"detail": ["Already waiting."]}}, status=409)

    WaitingEntry.objects.create(user=request.user)
    game = form_game()
    return Response({"joined": True, "game_id": game.id if game else None}, status=201)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def leave(request):
    WaitingEntry.objects.filter(user=request.user).delete()
    return Response(status=204)