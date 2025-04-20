from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from .models import UserPoints, UserActivity
from rest_framework.pagination import PageNumberPagination


class ActivityPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'limit'
    max_page_size = 100

    def get_paginated_response(self, data):
        return Response({
            'activities': data,
            'totalActivities': self.page.paginator.count,
            'currentPage': self.page.number,
            'totalPages': self.page.paginator.num_pages
        })


class BalanceView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({
            'points': request.user.points.points
        })


class ActivityListView(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = ActivityPagination

    def get(self, request):
        paginator = self.pagination_class()
        activities = request.user.activities.all()
        paginated_activities = paginator.paginate_queryset(activities, request)

        activity_data = [{
            'type': activity.activity_type,
            'points': activity.points,
            'created_at': activity.created_at
        } for activity in paginated_activities]

        return paginator.get_paginated_response(activity_data)


class LeaderboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        top_users = UserPoints.objects.select_related(
            'user').order_by('-points')[:3]
        leaderboard = [{
            'username': points.user.username,
            'points': points.points
        } for points in top_users]

        return Response({
            'leaderboard': leaderboard
        })
