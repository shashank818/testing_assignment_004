import factory
from faker import Faker

fake = Faker()
from fb_post.models import User, Post, Comment, Reaction


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    name = fake.name()
    profile_pic = fake.nam()
