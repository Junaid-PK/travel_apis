from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404
from accounts.models import Post, Comment, Like
from .serializers import (
    PostSerializer, PostCreateUpdateSerializer,
    CommentSerializer, CommentCreateUpdateSerializer
)
from rest_framework.parsers import MultiPartParser, FormParser


class PostPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'limit'
    max_page_size = 100

    def get_paginated_response(self, data):
        return Response({
            'posts': data,
            'totalPosts': self.page.paginator.count,
            'currentPage': self.page.number,
            'totalPages': self.page.paginator.num_pages
        })


class CommentPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'limit'
    max_page_size = 100

    def get_paginated_response(self, data):
        return Response({
            'comments': data,
            'totalComments': self.page.paginator.count,
            'currentPage': self.page.number,
            'totalPages': self.page.paginator.num_pages
        })


class PostListCreateView(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = PostPagination
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request):
        paginator = self.pagination_class()
        posts = Post.objects.all().order_by('-created_at')
        paginated_posts = paginator.paginate_queryset(posts, request)
        serializer = PostSerializer(
            paginated_posts, many=True, context={'request': request})
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        print("Request data:", request.data)
        # Handle both multipart form data and JSON data
        serializer = PostCreateUpdateSerializer(
            data=request.data, context={'request': request})
        if serializer.is_valid():
            print("Serializer validated data:", serializer.validated_data)
            # Let the serializer handle both file uploads and base64 image data
            post = serializer.save(author=request.user)

            # Add points for post creation
            user_points = request.user.points
            user_points.points += 100
            user_points.save()

            # Record post creation activity
            request.user.activities.create(
                activity_type='post_creation', points=100)

            response_serializer = PostSerializer(
                post, context={'request': request})
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        print("Serializer errors:", serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PostDetailView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        serializer = PostSerializer(post, context={'request': request})
        return Response(serializer.data)

    def put(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        if post.author != request.user:
            return Response({"error": {"message": "Not authorized", "code": "forbidden"}},
                            status=status.HTTP_403_FORBIDDEN)
        serializer = PostCreateUpdateSerializer(post, data=request.data)
        if serializer.is_valid():
            if 'image' in request.FILES:
                serializer.validated_data['image'] = request.FILES['image']
            post = serializer.save()
            response_serializer = PostSerializer(
                post, context={'request': request})
            return Response(response_serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        if post.author != request.user:
            return Response({"error": {"message": "Not authorized", "code": "forbidden"}},
                            status=status.HTTP_403_FORBIDDEN)
        post.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class PostLikeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        like, created = Like.objects.get_or_create(
            user=request.user, post=post)

        if not created:
            like.delete()
            is_liked = False
        else:
            is_liked = True

        return Response({
            'isLiked': is_liked,
            'likeCount': post.likes_count
        })


class PostShareView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        # Implement sharing logic here
        return Response({"message": "Post shared successfully"})


class CommentListCreateView(APIView):
    permission_classes = [IsAuthenticated]
    pagination_class = CommentPagination

    def get(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        paginator = self.pagination_class()
        comments = post.comments.filter(parent=None).order_by('-created_at')
        paginated_comments = paginator.paginate_queryset(comments, request)
        serializer = CommentSerializer(
            paginated_comments, many=True, context={'request': request})
        return paginator.get_paginated_response(serializer.data)

    def post(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        serializer = CommentCreateUpdateSerializer(data=request.data)
        if serializer.is_valid():
            comment = serializer.save(author=request.user, post=post)
            response_serializer = CommentSerializer(
                comment, context={'request': request})
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CommentDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, post_id, comment_id):
        comment = get_object_or_404(Comment, id=comment_id, post_id=post_id)
        if comment.author != request.user:
            return Response({"error": {"message": "Not authorized", "code": "forbidden"}},
                            status=status.HTTP_403_FORBIDDEN)
        serializer = CommentCreateUpdateSerializer(comment, data=request.data)
        if serializer.is_valid():
            comment = serializer.save()
            response_serializer = CommentSerializer(
                comment, context={'request': request})
            return Response(response_serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, post_id, comment_id):
        comment = get_object_or_404(Comment, id=comment_id, post_id=post_id)
        if comment.author != request.user:
            return Response({"error": {"message": "Not authorized", "code": "forbidden"}},
                            status=status.HTTP_403_FORBIDDEN)
        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CommentLikeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, post_id, comment_id):
        comment = get_object_or_404(Comment, id=comment_id, post_id=post_id)
        like, created = Like.objects.get_or_create(
            user=request.user, comment=comment)

        if not created:
            like.delete()
            is_liked = False
        else:
            is_liked = True

        return Response({
            'isLiked': is_liked,
            'likeCount': comment.likes_count
        })


class CommentReplyView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, post_id, comment_id):
        parent_comment = get_object_or_404(
            Comment, id=comment_id, post_id=post_id)
        serializer = CommentCreateUpdateSerializer(data=request.data)
        if serializer.is_valid():
            reply = serializer.save(
                author=request.user,
                post_id=post_id,
                parent=parent_comment
            )
            response_serializer = CommentSerializer(
                reply, context={'request': request})
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
