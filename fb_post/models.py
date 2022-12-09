from django.db import models


class User(models.Model):
    # objects = None
    name = models.CharField(max_length=20)
    profile_pic = models.CharField(max_length=1000)


class Post(models.Model):
    content = models.CharField(max_length=1000)
    posted_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)


class Comment(models.Model):
    content = models.TextField(max_length=50, null=True, blank=True)
    commented_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True)
    parent = models.ForeignKey('self', null=True, blank=True,
                               on_delete=models.CASCADE)


class Reaction(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True,
                             blank=True)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE,
                                null=True, blank=True)
    react_choices = (
        ("WOW", "WOW"),
        ("LIT", "LIT"),
        ("LOVE", "LOVE"),
        ("HAHA", "HAHA"),
        ("THUMBS-UP", "THUMBS-UP"),
        ("THUMBS-DOWN", "THUMBS-DOWN"),
        ("ANGRY", "ANGRY"),
        ("SAD", "SAD"),
    )
    react = models.CharField(max_length=100, choices=react_choices,
                             default="Like")
    reaction = models.CharField(max_length=100, blank=True, null=True)
    reacted_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
