from rest_framework import serializers
from accounts.models import Post, Comment, Like
from django.contrib.auth.models import User


class UserBriefSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']


class CommentSerializer(serializers.ModelSerializer):
    author = UserBriefSerializer(read_only=True)
    likes = serializers.IntegerField(source='likes_count', read_only=True)
    isLikedByUser = serializers.SerializerMethodField()
    replies = serializers.SerializerMethodField()
    timestamp = serializers.DateTimeField(source='created_at', read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'author', 'content', 'likes',
                  'isLikedByUser', 'timestamp', 'replies']

    def get_isLikedByUser(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Like.objects.filter(user=request.user, comment=obj).exists()
        return False

    def get_replies(self, obj):
        replies = obj.replies.all()
        return CommentSerializer(replies, many=True, context=self.context).data


class PostSerializer(serializers.ModelSerializer):
    author = UserBriefSerializer(read_only=True)
    likes = serializers.IntegerField(source='likes_count', read_only=True)
    comments = serializers.IntegerField(
        source='comments_count', read_only=True)
    isLikedByUser = serializers.SerializerMethodField()
    timestamp = serializers.DateTimeField(source='created_at', read_only=True)
    image = serializers.ImageField(max_length=None, use_url=True)

    class Meta:
        model = Post
        fields = ['id', 'author', 'content', 'image', 'location', 'likes',
                  'comments', 'isLikedByUser', 'timestamp']

    def get_isLikedByUser(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Like.objects.filter(user=request.user, post=obj).exists()
        return False


class PostCreateUpdateSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(
        max_length=None, use_url=True, required=False)
    image_data = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = Post
        fields = ['content', 'image', 'image_data', 'location']

    def create(self, validated_data):
        image_data = validated_data.pop('image_data', None)

        if image_data:
            try:
                # Handle base64 image data
                if ';base64,' in image_data:
                    format, base64_str = image_data.split(';base64,')
                    # Extract image format from the data URI
                    image_format = format.split('/')[-1]

                    import base64
                    from django.core.files.base import ContentFile
                    import time

                    try:
                        image_data = base64.b64decode(base64_str)
                        timestamp = int(time.time())
                        file_name = f'post_image_{timestamp}.{image_format}'
                        validated_data['image'] = ContentFile(
                            image_data, name=file_name)
                    except Exception as e:
                        raise serializers.ValidationError({
                            'image_data': f'Invalid base64 image data: {str(e)}'
                        })
                else:
                    raise serializers.ValidationError({
                        'image_data': 'Invalid image data format. Must be base64 encoded.'
                    })
            except Exception as e:
                raise serializers.ValidationError({
                    'image_data': f'Error processing image data: {str(e)}'
                })

        return super().create(validated_data)


class CommentCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['content']
