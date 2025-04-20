from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserPoints(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='points')
    points = models.IntegerField(default=0)

    def __str__(self):
        return f'{self.user.username} - {self.points} points'


class UserActivity(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='activities')
    activity_type = models.CharField(max_length=50)
    points = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.username} - {self.activity_type} - {self.points} points'


@receiver(post_save, sender=User)
def create_user_points(sender, instance, created, **kwargs):
    if created:
        UserPoints.objects.create(user=instance)
    else:
        # Ensure UserPoints exists for existing users
        UserPoints.objects.get_or_create(user=instance)


class UserFollow(models.Model):
    follower = models.ForeignKey(
        User, related_name='following', on_delete=models.CASCADE)
    following = models.ForeignKey(
        User, related_name='followers', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('follower', 'following')
        indexes = [
            models.Index(fields=['follower']),
            models.Index(fields=['following']),
        ]

    def __str__(self):
        return f'{self.follower.username} follows {self.following.username}'


class Post(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='posts')
    content = models.TextField()
    image = models.ImageField(upload_to='posts/', blank=True, null=True)
    location = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.author.username} - {self.created_at}'

    @property
    def likes_count(self):
        return self.likes.count()

    @property
    def comments_count(self):
        return self.comments.count()


class Comment(models.Model):
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    parent = models.ForeignKey(
        'self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.author.username} on {self.post}'

    @property
    def likes_count(self):
        return self.likes.count()


class Like(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, null=True, blank=True, related_name='likes')
    comment = models.ForeignKey(
        Comment, on_delete=models.CASCADE, null=True, blank=True, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'post'],
                condition=models.Q(post__isnull=False),
                name='unique_user_post_like'
            ),
            models.UniqueConstraint(
                fields=['user', 'comment'],
                condition=models.Q(comment__isnull=False),
                name='unique_user_comment_like'
            ),
        ]
        indexes = [
            models.Index(fields=['user', 'post']),
            models.Index(fields=['user', 'comment']),
        ]

    def __str__(self):
        if self.post:
            return f'{self.user.username} likes {self.post}'
        return f'{self.user.username} likes {self.comment}'
