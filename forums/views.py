from django.db.models import F, Q
from django.core.paginator import Paginator
from rest_framework import status, permissions, viewsets, parsers
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from forums.models import Discussion, Comment
from forums import serializers


class DiscussionViewset(viewsets.ModelViewSet):

    """
    create: Create a Discussion thread.
    list: List all discussions in forum
    partial_update: Update discussion info as authenticated author.
    destroy: Delete discussion info as authenticated author.
    """
    queryset = Discussion.objects.all().order_by("-created_at")
    serializer_class = serializers.RetrieveDiscussionSerializer
    http_method_names = ["get", "post", "patch", "delete"]
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action in ["create", "partial_update"]:
            return serializers.CreateDiscussionSerializer
        return super().get_serializer_class()

    def create(self, request):
        serializer = serializers.CreateDiscussionSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.error_messages, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk):
        discussion = self.get_object()
        if discussion.user != request.user:
            return Response({
                "detail": "You cannot edit a post you did not create."
            }, status=status.HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save(user=request.user)
            return Response({
                "detail": "Discussion updated successfully!",
                **serializer.data
            }, status=status.HTTP_200_OK)
        return Response(serializer.error_messages, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk):
        discussion = self.get_object()
        if discussion.user != request.user:
            return Response({
                "detail": "You cannot delete a post you did not create."
            }, status=status.HTTP_403_FORBIDDEN)

        if Discussion.objects.filter(id=discussion.id).exists():
            discussion.delete()
            return Response({
                "detail": "Discussion delete successfully!"
            }, status=status.HTTP_200_OK)
        return Response({"detail": "Discussion with given ID not found"}, status=status.HTTP_400_NOT_FOUND)

    @swagger_auto_schema(
        methods=["post"],
        operation_description="Like or unlike this discussion",
        request_body=serializers.EmptySerializer,
        response_body=serializers.RetrieveDiscussionSerializer,
        permission_classes=[permissions.IsAuthenticated]
    )
    @action(methods=["post"], detail=True, url_path="like-unlike")
    def like_or_unlike(self, request, pk):
        discussion = self.get_object()
        if discussion.likes.filter(id=request.user.id).exists():
            discussion.likes.remove(request.user)
            serializer = self.get_serializer(instance=discussion, many=False)
            return Response({
                "detail": "You unliked this post.",
                **serializer.data
            }, status=status.HTTP_200_OK)

        discussion.likes.add(request.user)
        serializer = self.get_serializer(instance=discussion, many=False)
        return Response({
            "detail": "You liked this post!",
            **serializer.data
        }, status=status.HTTP_200_OK)

    @action(methods=["get"], detail=False, url_path="mine")
    def own_discussions(self, request):
        user_discussions = Discussion.objects.filter(user=request.user)
        user_discussions = self.paginate_queryset(user_discussions)
        serializer = self.get_serializer(user_discussions, many=True)
        return self.get_paginated_response(serializer.data)

    @swagger_auto_schema(
        methods=["post"],
        operation_description="Leave a comment on this Discussion.\
            If a comment already exists, this endpoint updates the user's reply.",
        response_body=serializers.RetrieveDiscussionSerializer,
        request_body=serializers.CreateCommentSerializer,
        permission_classes=[permissions.IsAuthenticated]
    )
    @action(methods=["post"], detail=True, url_path="add-comment")
    def add_comment(self, request, pk):
        discussion = self.get_object()

        try:
            discussion = Discussion.objects.get(id=discussion.id)
            _, created = Comment.objects.update_or_create(
                user=request.user,
                post=discussion,
                defaults={
                    "content": request.data.get("content")
                }
            )
            serializer = serializers.RetrieveDiscussionSerializer(discussion, many=False)

            if created:
                return Response({
                    "detail": "Comment added!",
                    **serializer.data
                }, status.HTTP_201_CREATED)
            return Response({
                "detail": "Comment updated!",
                **serializer.data
            }, status=status.HTTP_200_OK)
        except:
            return Response({
                "detail": "Discussion not found"
            }, status=status.HTTP_404_NOT_FOUND)

    @swagger_auto_schema(
        methods=["delete"],
        operation_description="Delete comment as an authenticated user",
        response_body=serializers.RetrieveDiscussionSerializer,
        request_body=serializers.IDSerializer,
        permission_classes=[permissions.IsAuthenticated]
    )
    @action(methods=["delete"], detail=True, url_path="delete-comment")
    def delete_comment(self, request, pk):

        discussion = self.get_object()
        comment_id = request.data.pop("comment_id", None)

        try:
            comment = discussion.comments.get(id=comment_id)

            if comment:
                if comment.user != request.user:
                    return Response({
                        "detail": "You cannot delete a comment you did not create."
                    }, status=status.HTTP_403_FORBIDDEN)
                
                comment.delete()
                serializer = self.get_serializer(instance=discussion, many=False)

                return Response({
                    "detail": "Comment has been deleted!",
                    **serializer.data
                })
        except:
            return Response({
                "detail": "Comment not found."
            }, status=status.HTTP_404_NOT_FOUND)

