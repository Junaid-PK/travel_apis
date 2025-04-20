from django.contrib.auth.models import User
from django.db.models import Count, Q
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import UserFollow
from .serializers import (
    FollowerSerializer,
    FollowingSerializer,
    UserSerializer,
    UserSuggestionSerializer
)


class FollowerListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
            followers = UserFollow.objects.filter(following=user)
            serializer = FollowerSerializer(followers, many=True)
            return Response({
                'followers': serializer.data,
                'totalFollowers': followers.count()
            })
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)


class FollowingListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
            following = UserFollow.objects.filter(follower=user)
            serializer = FollowingSerializer(following, many=True)
            return Response({
                'following': serializer.data,
                'totalFollowing': following.count()
            })
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)


class FollowUserView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, user_id):
        try:
            user_to_follow = User.objects.get(id=user_id)
            if request.user == user_to_follow:
                return Response(
                    {'error': 'You cannot follow yourself'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            follow, created = UserFollow.objects.get_or_create(
                follower=request.user,
                following=user_to_follow
            )

            if not created:
                return Response(
                    {'error': 'You are already following this user'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            return Response({
                'success': True,
                'message': 'Successfully followed user',
                'followedUser': UserSerializer(user_to_follow).data
            })
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )


class UnfollowUserView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, user_id):
        try:
            user_to_unfollow = User.objects.get(id=user_id)
            follow = UserFollow.objects.filter(
                follower=request.user,
                following=user_to_unfollow
            ).first()

            if not follow:
                return Response(
                    {'error': 'You are not following this user'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            follow.delete()
            return Response({
                'success': True,
                'message': 'Successfully unfollowed user',
                'unfollowedUser': UserSerializer(user_to_unfollow).data
            })
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )


class UserSuggestionsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Exclude the current user and users they already follow
        following_ids = request.user.following.values_list(
            'following_id', flat=True)
        suggestions = User.objects.exclude(
            Q(id=request.user.id) | Q(id__in=following_ids)
        ).annotate(
            mutual_count=Count(
                'following',
                filter=Q(following__following_id__in=following_ids)
            )
        ).order_by('-mutual_count')[:5]

        serializer = UserSuggestionSerializer(
            suggestions,
            many=True,
            context={'request': request}
        )
        return Response({'suggestions': serializer.data})
