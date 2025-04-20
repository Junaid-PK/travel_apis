from django.urls import path
from . import views

urlpatterns = [
    path('posts/', views.PostListCreateView.as_view(), name='post-list-create'),
    path('posts/<int:post_id>/', views.PostDetailView.as_view(), name='post-detail'),
    path('posts/<int:post_id>/like/',
         views.PostLikeView.as_view(), name='post-like'),
    path('posts/<int:post_id>/share/',
         views.PostShareView.as_view(), name='post-share'),
    path('posts/<int:post_id>/comments/',
         views.CommentListCreateView.as_view(), name='comment-list-create'),
    path('posts/<int:post_id>/comments/<int:comment_id>/',
         views.CommentDetailView.as_view(), name='comment-detail'),
    path('posts/<int:post_id>/comments/<int:comment_id>/like/',
         views.CommentLikeView.as_view(), name='comment-like'),
    path('posts/<int:post_id>/comments/<int:comment_id>/replies/',
         views.CommentReplyView.as_view(), name='comment-reply'),
]
