from rest_framework import serializers
from forums.models import Discussion, Comment, CATEGORY_TYPE


class CreateDiscussionSerializer(serializers.ModelSerializer):
    likes = serializers.SerializerMethodField()

    class Meta:
        model = Discussion
        exclude = ("slug", "user")

    def get_likes(self, obj):
        return obj.get_likes_count()


class RetrieveDiscussionSerializer(serializers.ModelSerializer):

    likes = serializers.SerializerMethodField()
    comments = serializers.SerializerMethodField()

    class Meta:
        model = Discussion
        fields = "__all__"

    def get_likes(self, obj):
        return obj.get_likes_count()

    def get_comments(self, obj):
        return RetrieveCommentSerializer(obj.comments.all(), many=True).data


class CreateCommentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Comment
        fields = ("content", "created_at")


class RetrieveCommentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Comment
        fields = "__all__"


class EmptySerializer(serializers.Serializer):
    pass


class IDSerializer(serializers.Serializer):
    comment_id = serializers.IntegerField()
