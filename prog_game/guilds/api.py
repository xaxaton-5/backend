from django.db.models import Count, Sum
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from guilds.models import Guild, GuildMembership
from guilds.serializers import (
    GuildDetailSerializer,
    GuildJoinSerializer,
    GuildMembershipSerializer,
    GuildSerializer,
)
from users.decorators import with_authorization


class GuildList(APIView):
    @with_authorization
    def get(self, request):
        membership = GuildMembership.objects.filter(user=request.user).select_related('guild').first()
        guilds = Guild.objects.annotate(member_count=Count('memberships')).order_by('name')
        serializer = GuildSerializer(guilds, many=True, context={'membership': membership})
        return Response(
            {
                'guilds': serializer.data,
                'current_guild_id': membership.guild_id if membership else None,
            }
        )


class GuildJoin(APIView):
    @with_authorization
    def post(self, request):
        serializer = GuildJoinSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)

        guild = serializer.context['guild']
        membership, created = GuildMembership.objects.update_or_create(
            user=request.user,
            defaults={'guild': guild},
        )

        response_status = status.HTTP_201_CREATED if created else status.HTTP_200_OK
        return Response(
            {
                'status': 'OK',
                'message': f'Вы вступили в гильдию "{guild.name}"',
                'membership': GuildMembershipSerializer(membership).data,
            },
            status=response_status,
        )


class GuildDetail(APIView):
    @with_authorization
    def get(self, request, slug: str):
        membership = GuildMembership.objects.filter(user=request.user).select_related('guild').first()

        try:
            guild = (
                Guild.objects.annotate(
                    member_count=Count('memberships'),
                    total_exp=Sum('users__profile__exp'),
                )
                .prefetch_related('users__profile')
                .get(slug=slug)
            )
        except Guild.DoesNotExist:
            return Response({'error': 'Guild not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = GuildDetailSerializer(guild, context={'membership': membership})
        return Response(serializer.data)


guild_list = GuildList.as_view()
guild_join = GuildJoin.as_view()
guild_detail = GuildDetail.as_view()
