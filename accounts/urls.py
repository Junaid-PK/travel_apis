from django.urls import path
from .views import SignupView, LoginView, ChangePasswordView, ChangeEmailView
from .social_views import (
    FollowerListView, FollowingListView,
    FollowUserView, UnfollowUserView,
    UserSuggestionsView
)
from .point_views import BalanceView, ActivityListView, LeaderboardView

urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('change-email/', ChangeEmailView.as_view(), name='change-email'),
    # Social endpoints
    path('users/<int:user_id>/followers',
         FollowerListView.as_view(), name='user-followers'),
    path('users/<int:user_id>/following',
         FollowingListView.as_view(), name='user-following'),
    path('users/<int:user_id>/follow/',
         FollowUserView.as_view(), name='follow-user'),
    path('users/<int:user_id>/unfollow/',
         UnfollowUserView.as_view(), name='unfollow-user'),
    path('users/suggestions/', UserSuggestionsView.as_view(),
         name='user-suggestions'),
    # Points and activities endpoints
    path('balance/', BalanceView.as_view(), name='balance'),
    path('activities/', ActivityListView.as_view(), name='activities'),
    path('leaderboard/', LeaderboardView.as_view(), name='leaderboard'),
]
