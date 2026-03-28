from rest_framework import serializers

from guilds.models import Guild, GuildMembership


class GuildSerializer(serializers.ModelSerializer):
    member_count = serializers.IntegerField(read_only=True)
    is_joined = serializers.SerializerMethodField()

    class Meta:
        model = Guild
        fields = [
            'id',
            'name',
            'slug',
            'emoji',
            'tagline',
            'description',
            'focus',
            'topics',
            'member_count',
            'is_joined',
        ]

    def get_is_joined(self, obj):
        membership = self.context.get('membership')
        return bool(membership and membership.guild_id == obj.id)


class GuildMembershipSerializer(serializers.ModelSerializer):
    guild_id = serializers.IntegerField(source='guild.id', read_only=True)
    guild_name = serializers.CharField(source='guild.name', read_only=True)

    class Meta:
        model = GuildMembership
        fields = ['guild_id', 'guild_name', 'joined_at']


class GuildJoinSerializer(serializers.Serializer):
    guild_id = serializers.IntegerField(required=True)

    def validate_guild_id(self, value):
        try:
            guild = Guild.objects.get(id=value)
        except Guild.DoesNotExist as exc:
            raise serializers.ValidationError('Guild not found') from exc
        self.context['guild'] = guild
        return value
