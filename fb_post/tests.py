import json
from collections import defaultdict
from datetime import datetime

import snapshot as snapshot
from freezegun import freeze_time

import pytest as pytest
from fb_post.utils import validate_user, validate_post, validate_comment, \
    create_post, create_comment, reply_to_comment, react_to_post, \
    react_to_comment, get_reaction_metrics, delete_post, \
    get_posts_with_more_positive_reactions, get_posts_reacted_by_user, \
    get_reactions_to_post, get_user_details, get_reactions_detail, \
    get_reactions_detail_of_comments, get_reactions_detail_of_comments_replies, \
    get_replies_details, get_comments_details, get_posts, get_user_posts, \
    get_replies_for_comments
from fb_post.exceptions import InvalidUserException, InvalidPostException, \
    InvalidPostContent, InvalidCommentContent, InvalidReplyContent, \
    InvalidReactionTypeException, UserCannotDeletePostException
from fb_post.models import User, Post, Comment, Reaction


def test_validate_user():
    # Arrange
    # Act
    with pytest.raises(InvalidUserException) as e:
        assert validate_user(1)
    # Assert
    assert str(e.value) == 'InvalidUserException'


def test_validate_post():
    with pytest.raises(InvalidPostException) as e:
        assert validate_post(2)
    assert str(e.value) == 'InvalidPostException'


def test_validate_comment():
    with pytest.raises(InvalidUserException) as e:
        assert validate_comment(3)
    assert str(e.value) == 'InvalidCommentException'


@pytest.mark.django_db
def test_create_post_valid_post_content():
    # Arrange
    user = User.objects.create(name="Champak", profile_pic="abc")
    # Act
    with pytest.raises(InvalidPostContent) as e:
        create_post(user.pk, "")
    # Assert
    assert str(e.value) == 'InvalidPostContent'


@pytest.mark.django_db
def test_create_post_to_validate_user():
    # Arrange
    User.objects.create(name='Rohit',
                        profile_pic='https://www.shutterstock.com/image-photo/large-thick-industrial-black-metal-chain-1081708619')

    # Act
    with pytest.raises(Exception) as e:
        create_post(2, 'first post')

    # Assert
    assert str(e.value) == "InvalidUserException"


@pytest.mark.django_db
def test_create_post_if_post_is_created():
    # Arrange
    user = User.objects.create(name="Champak", profile_pic="abc")

    # Act
    post = create_post(user.pk, "check it")

    # Assert
    assert post == 1


@pytest.mark.django_db
def test_create_comment_is_user_valid():
    # Arrange
    user = User.objects.create(name="mohan", profile_pic="Kallu")
    post = Post.objects.create(content="abc", user=user)

    # Act
    with pytest.raises(InvalidUserException) as e:
        create_comment(5, post.pk, "ok")
    # Assert
    assert str(e.value) == "InvalidUserException"


@pytest.mark.django_db
def test_create_comment_is_post_valid():
    # Arrange
    user = User.objects.create(name="mohan", profile_pic="Kallu")

    # Act
    with pytest.raises(InvalidPostException) as e:
        create_comment(user.pk, 9, "ok")

    # Assert
    str(e.value) == "InvalidPostException"


@pytest.mark.django_db
def test_create_comment_for_empty_content():
    # Arrange
    user = User.objects.create(name="mohan", profile_pic="Kallu")
    post = Post.objects.create(content="abc", user=user)

    # Act
    with pytest.raises(InvalidCommentContent) as e:
        create_comment(user.pk, post.pk, "")

    # Assert
    str(e.value) == "InvalidCommentContent"


@pytest.mark.django_db
def test_create_comment_if_comment_updated_in_db():
    # Arrange
    user = User.objects.create(name="mohan", profile_pic="Kallu")
    post = Post.objects.create(content="abc", user_id=user.pk)

    # Act
    comment = create_comment(user_id=user.pk, post_id=post.pk,
                             comment_content="fine")

    # Assert
    assert comment == 1


@pytest.mark.django_db
def test_reply_to_comment_for_valid_user():
    # Arrange
    user = User.objects.create(name="mohan", profile_pic="Kallu")
    post = Post.objects.create(content="abc", user_id=user.id)
    comment = Comment.objects.create(user_id=user.id, post_id=post.id)

    # Act
    with pytest.raises(InvalidUserException) as e:
        reply_to_comment(user_id=5, comment_id=comment.id,
                         reply_content="ewe")

    # Assert
    str(e.value) == "InvalidUserException"


@pytest.mark.django_db
def test_test_reply_to_comment_for_valid_comment():
    # Arrange
    user = User.objects.create(name="mohan", profile_pic="Kallu")
    # Act
    with pytest.raises(InvalidUserException) as e:
        reply_to_comment(user_id=user.id, comment_id=5, reply_content="pk")

    # Assert
    str(e.value) == "InvalidCommentException"


@pytest.mark.django_db
def test_reply_to_comment_for_valid_reply_content():
    # Arrange
    user = User.objects.create(name="mohan", profile_pic="Kallu")
    post = Post.objects.create(content="abc", user_id=user.id)
    comment = Comment.objects.create(user_id=user.id, post_id=post.id)

    # Act
    with pytest.raises(InvalidReplyContent) as e:
        reply_to_comment(user_id=user.id, comment_id=comment.id,
                         reply_content="")

    # Assert
    str(e.value) == "InvalidReplyContent"


@pytest.mark.django_db
def test_reply_to_comment_stored_in_db():
    # Arrange
    user = User.objects.create(name="mohan", profile_pic="Kallu")
    post = Post.objects.create(content="abc", user_id=user.id)
    comment = Comment.objects.create(user_id=user.id, post_id=post.id)

    # Act
    reply = reply_to_comment(user_id=user.id, comment_id=comment.id,
                             reply_content="dfg")

    # Assert
    assert reply == 2


@pytest.mark.django_db
def test_react_to_post_valid_user():
    user = User.objects.create(name="mohan", profile_pic="Kallu")
    post = Post.objects.create(content="abc", user_id=user.id)

    with pytest.raises(InvalidUserException) as e:
        react_to_post(5, post.id, "WOW")

    assert str(e.value) == "InvalidUserException"


@pytest.mark.django_db
def test_react_to_post_valid_post():
    user = User.objects.create(name="mohan", profile_pic="Kallu")
    with pytest.raises(InvalidPostException) as e:
        react_to_post(user.id, 5, "WOW")

    assert str(e.value) == "InvalidPostException"


@pytest.mark.django_db
def test_react_to_post_for_invalid_reaction_type():
    user = User.objects.create(name="mohan", profile_pic="Kallu")
    post = Post.objects.create(content="abc", user_id=user.id)
    with pytest.raises(InvalidReactionTypeException) as e:
        react_to_post(user.id, post.id, "HAH")

    assert str(e.value) == "InvalidReactionTypeException"


@pytest.mark.django_db
def test_react_to_post_for_already_reacted():
    # Arrange
    user = User.objects.create(name="mohan", profile_pic="Kallu")
    post = Post.objects.create(content="abc", user_id=user.id)
    react_to_post(user.id, post.id, "HAHA")
    # Act
    reaction = react_to_post(user.id, post.id, "HAHA")

    # Assert
    assert Reaction.objects.filter(user_id=user.id, post_id=post.id).exists() \
           == False


@pytest.mark.django_db
def test_react_to_post_for_already_reacted_but_different_reaction():
    # Arrange
    user = User.objects.create(name="mohan", profile_pic="Kallu")
    post = Post.objects.create(content="abc", user_id=user.id)
    react_to_post(user.id, post.id, "HAHA")
    # Act
    react_to_post(user.id, post.id, "SAD")
    new_reaction = Reaction.objects.values_list('react', flat=True).filter(
        user_id=user.id, post_id=post.id)

    # Assert
    assert new_reaction[0] == "SAD"


@pytest.mark.django_db
def test_react_to_post_is_reaction_store_in_db():
    # Arrange
    user = User.objects.create(name="mohan", profile_pic="Kallu")
    post = Post.objects.create(content="abc", user_id=user.id)
    # Act
    react_to_post(user.id, post.id, "SAD")

    # Assert
    assert Reaction.objects.filter(user_id=user.id, post_id=post.id).exists() \
           == True


@pytest.mark.django_db
def test_react_to_comment_valid_user():
    user = User.objects.create(name="mohan", profile_pic="Kallu")
    comment = Comment.objects.create(content="abc", user_id=user.id)

    with pytest.raises(InvalidUserException) as e:
        react_to_comment(5, comment.id, "WOW")

    assert str(e.value) == "InvalidUserException"


@pytest.mark.django_db
def test_react_to_comment_valid_comment():
    user = User.objects.create(name="mohan", profile_pic="Kallu")
    with pytest.raises(InvalidUserException) as e:
        react_to_comment(user.id, 5, "WOW")

    assert str(e.value) == "InvalidCommentException"


@pytest.mark.django_db
def test_react_to_comment_for_invalid_reaction_type():
    user = User.objects.create(name="mohan", profile_pic="Kallu")
    comment = Comment.objects.create(content="abc", user_id=user.id)
    with pytest.raises(InvalidReactionTypeException) as e:
        react_to_comment(user.id, comment.id, "HAH")

    assert str(e.value) == "InvalidReactionTypeException"


@pytest.mark.django_db
def test_react_to_comment_for_already_reacted():
    # Arrange
    user = User.objects.create(name="mohan", profile_pic="Kallu")
    comment = Comment.objects.create(content="abc", user_id=user.id)
    react_to_comment(user.id, comment.id, "HAHA")
    # Act
    reaction = react_to_comment(user.id, comment.id, "HAHA")

    # Assert
    assert Reaction.objects.filter(user_id=user.id,
                                   comment_id=comment.id).exists() \
           == False


@pytest.mark.django_db
def test_react_to_comment_for_already_reacted_but_different_reaction():
    # Arrange
    user = User.objects.create(name="mohan", profile_pic="Kallu")
    comment = Comment.objects.create(content="abc", user_id=user.id)
    react_to_comment(user.id, comment.id, "HAHA")
    # Act
    react_to_comment(user.id, comment.id, "SAD")
    new_reaction = Reaction.objects.values_list('react', flat=True).filter(
        user_id=user.id, comment_id=comment.id)

    # Assert
    assert new_reaction[0] == "SAD"


@pytest.mark.django_db
def test_react_to_comment_is_reaction_store_in_db():
    # Arrange
    user = User.objects.create(name="mohan", profile_pic="Kallu")
    comment = Comment.objects.create(content="abc", user_id=user.id)
    # Act
    react_to_comment(user.id, comment.id, "SAD")

    # Assert
    assert Reaction.objects.filter(user_id=user.id,
                                   comment_id=comment.id).exists() \
           == True


def get_total_reaction_count():
    user = User.objects.create(name='Sulekh',
                               profile_pic='ok its time to react')
    post = Post.objects.create(content='new post', posted_at=datetime.now(),
                               posted_by_id=user.id)
    Reaction.objects.create(post_id=post.id,
                            reaction='HAHA',
                            reacted_at=datetime.now(),
                            reacted_by_id=user.id)
    total_count = {'count': 1}
    # Act
    total = get_total_reaction_count()

    # Assert
    assert total == total_count


@pytest.mark.django_db
def test_get_reaction_metrics_validate_post_id():
    # Arrange
    User.objects.create(name='Mohan',
                        profile_pic='Black adams')

    # Act
    with pytest.raises(InvalidPostException) as e:
        assert get_reaction_metrics(9)

    # Assert
    assert str(e.value) == "InvalidPostException"


@pytest.mark.django_db
def test_get_reaction_metrics_returns_metrics_of_reactions():
    # Arrange
    user_one = User.objects.create(name='Mohan',
                                   profile_pic='Ok')
    user_two = User.objects.create(name='Shyam',
                                   profile_pic='Ok')

    post = Post.objects.create(content='Valid Post', posted_at=datetime.now(),
                               user_id=user_one.id)
    Reaction.objects.create(post_id=post.id,
                            reaction='HAHA',
                            reacted_at=datetime.now(),
                            user_id=user_one.id)
    Reaction.objects.create(post_id=post.id,
                            reaction='LOL',
                            reacted_at=datetime.now(),
                            user_id=user_two.id)
    metrics = {'HAHA': 1, 'LOL': 1}

    # Act
    output = get_reaction_metrics(post.id)

    # Assert
    assert output == metrics


@pytest.mark.django_db
def test_delete_post_validate_user_id():
    # Arrange
    User.objects.create(name='Mohan',
                        profile_pic='Black adams')
    # Act
    with pytest.raises(InvalidUserException) as e:
        delete_post(2, 2)
    # Assert
    assert str(e.value) == "InvalidUserException"


@pytest.mark.django_db
def test_delete_post_validate_Post_id():
    # Arrange
    User.objects.create(name='Mohan',
                        profile_pic='Black adams')
    # Act
    with pytest.raises(InvalidPostException) as e:
        delete_post(1, 2)
    # Assert
    assert str(e.value) == "InvalidPostException"


@pytest.mark.django_db
def test_delete_post_if_user_is_not_the_creator_of_post():
    # Arrange
    user_1 = User.objects.create(name='Mohan',
                                 profile_pic='Black adams')
    user_2 = User.objects.create(name='Shyam',
                                 profile_pic='OK_OK')
    post = Post.objects.create(content='first post', posted_at=datetime.now(),
                               user_id=user_1.id)

    # Act
    with pytest.raises(UserCannotDeletePostException) as e:
        delete_post(user_2.id, post.id)

    # Assert
    assert str(e.value) == "UserCannotDeletePostException"


@pytest.mark.django_db
def test_delete_post_if_user_is_the_creator_of_post():
    # Arrange
    user_1 = User.objects.create(name='Mohan',
                                 profile_pic='Black adams')
    post = Post.objects.create(content='first post', posted_at=datetime.now(),
                               user_id=user_1.id)

    # Act
    delete_post(user_1.id, post.id)
    does_exists = Post.objects.filter(id=post.id).exists()

    # Assert
    assert does_exists is False


@pytest.mark.django_db
def test_get_posts_with_more_positive_reactions_returns_list_of_post_ids():
    # Arrange
    user_1 = User.objects.create(name='Mohan',
                                 profile_pic='Black adams')
    user_2 = User.objects.create(name='Shyam',
                                 profile_pic='Black')
    post_1 = Post.objects.create(content='first post',
                                 posted_at=datetime.now(),
                                 user_id=user_1.id)
    post_2 = Post.objects.create(content='second post',
                                 posted_at=datetime.now(),
                                 user_id=user_2.id)
    Reaction.objects.create(post_id=post_1.id,
                            react='HAHA',
                            reacted_at=datetime.now(),
                            user_id=user_1.id)
    Reaction.objects.create(post_id=post_2.id,
                            react='WOW',
                            reacted_at=datetime.now(),
                            user_id=user_2.id)
    list_of_post_ids = [1, 2]

    # Act
    output = get_posts_with_more_positive_reactions()

    # Assert
    assert output == list_of_post_ids


@pytest.mark.django_db
def test_get_posts_reacted_by_user_validate_user_id():
    # Arrange
    User.objects.create(name='Mohan',
                        profile_pic='Black adams')
    # Act
    with pytest.raises(InvalidUserException) as e:
        get_posts_reacted_by_user(2)
    # Assert
    assert str(e.value) == "InvalidUserException"


@pytest.mark.django_db
def test_get_posts_reacted_by_user_returns_list_of_post_ids():
    # Arrange
    user_1 = User.objects.create(name='Mohan',
                                 profile_pic='Black adams')
    post_1 = Post.objects.create(content='first post',
                                 posted_at=datetime.now(),
                                 user_id=user_1.id)
    post_2 = Post.objects.create(content='second post',
                                 posted_at=datetime.now(),
                                 user_id=user_1.id)
    Reaction.objects.create(post_id=post_1.id,
                            reaction='HAHA',
                            reacted_at=datetime.now(),
                            user_id=user_1.id)
    Reaction.objects.create(post_id=post_2.id,
                            reaction='WOW',
                            reacted_at=datetime.now(),
                            user_id=user_1.id)
    list_of_post_ids = [1, 2]

    # Act
    output = get_posts_reacted_by_user(user_1.id)

    # Assert
    assert output == list_of_post_ids


@pytest.mark.django_db
def test_get_reactions_to_post_validate_post_id():
    # Arrange
    User.objects.create(name='Mohan',
                        profile_pic='Black adams')
    # Act
    with pytest.raises(InvalidPostException) as e:
        get_reactions_to_post(1)
    # Assert
    assert str(e.value) == "InvalidPostException"


@pytest.mark.django_db
def test_get_reactions_to_post_returns_list_of_dictionaries():
    # Arrange
    user_1 = User.objects.create(name='Mohan',
                                 profile_pic='Black adams')
    user_2 = User.objects.create(name='Shyam',
                                 profile_pic='Black')
    post_1 = Post.objects.create(content='first post',
                                 posted_at=datetime.now(),
                                 user_id=user_1.id)
    Reaction.objects.create(post_id=post_1.id,
                            react='HAHA',
                            reacted_at=datetime.now(),
                            user_id=user_1.id)
    Reaction.objects.create(post_id=post_1.id,
                            react='WOW',
                            reacted_at=datetime.now(),
                            user_id=user_2.id)
    list_of_dictionaries = [{'user_id': 1,
                             'name': 'Mohan',
                             'profile_pic': 'Black adams',
                             'reaction': 'HAHA'},
                            {'user_id': 2,
                             'name': 'Shyam',
                             'profile_pic': 'Black',
                             'reaction': 'WOW'}]

    # Act
    output = get_reactions_to_post(post_1.id)

    # Assert
    assert output == list_of_dictionaries


@pytest.mark.django_db
def test_user_details():
    user = User.objects.create(name="Mohan", profile_pic="OK_OK")
    user_detail = {
        "user_id": user.id,
        "name": user.name,
        "profile_pic": user.profile_pic
    }
    detail = get_user_details(user.id)
    assert user_detail == detail


@pytest.mark.django_db
def test_get_reactions_detail_returns_list_of_dictionaries():
    # Arrange
    user_1 = User.objects.create(name='Mohan',
                                 profile_pic='Black adams')
    user_2 = User.objects.create(name='Shyam',
                                 profile_pic='Black')
    post_1 = Post.objects.create(content='first post',
                                 posted_at=datetime.now(),
                                 user_id=user_1.id)
    Reaction.objects.create(post_id=post_1.id,
                            react='HAHA',
                            reacted_at=datetime.now(),
                            user_id=user_1.id)
    Reaction.objects.create(post_id=post_1.id,
                            react='WOW',
                            reacted_at=datetime.now(),
                            user_id=user_2.id)
    list_of_dictionaries = defaultdict(list,
                                       {1: [{'count': 2, 'type': {'HAHA',
                                                                  'WOW'}},
                                            {'count': 2,
                                             'type': {'HAHA', 'WOW'}}]})

    # Act
    output = get_reactions_detail([post_1.id])

    # Assert
    assert output == list_of_dictionaries


@pytest.mark.django_db
def test_get_reactions_detail_of_comments_returns_list_of_dictionaries():
    # Arrange
    user_1 = User.objects.create(name='Mohan',
                                 profile_pic='Black adams')
    post_1 = Post.objects.create(content='first post',
                                 posted_at=datetime.now(),
                                 user_id=user_1.id)
    comment_one = Comment.objects.create(content='first comment',
                                         commented_at=datetime.now(),
                                         user=user_1,
                                         post_id=post_1.id)
    Reaction.objects.create(comment_id=comment_one.id,
                            react='HAHA',
                            reacted_at=datetime.now(),
                            user_id=user_1.id)

    list_of_dictionaries = defaultdict(list,
                                       {1: [{'count': 1, 'type': ['HAHA']}]})

    # Act
    output = get_reactions_detail_of_comments([post_1.id])

    # Assert
    assert output == list_of_dictionaries


@pytest.mark.django_db
def test_get_reactions_detail_of_comments_replies_returns_list_of_dictionaries():
    # Arrange
    user_1 = User.objects.create(name='Mohan',
                                 profile_pic='Black adams')
    post_1 = Post.objects.create(content='first post',
                                 posted_at=datetime.now(),
                                 user_id=user_1.id)
    comment_one = Comment.objects.create(content='first comment',
                                         commented_at=datetime.now(),
                                         user=user_1,
                                         post_id=post_1.id)
    reply_one = Comment.objects.create(content='first comment',
                                       commented_at=datetime.now(),
                                       user=user_1,
                                       parent_id=comment_one.id)
    Reaction.objects.create(comment_id=reply_one.id,
                            react='HAHA',
                            reacted_at=datetime.now(),
                            user_id=user_1.id)

    list_of_dictionaries = defaultdict(list, {2: [{'count': 1, 'type': [
        'HAHA']}]})

    # Act
    output = get_reactions_detail_of_comments_replies([comment_one.id])

    # Assert
    assert output == list_of_dictionaries


@freeze_time("2022-11-14 05:52:30+00:00", tz_offset=-4)
@pytest.mark.django_db
def test_get_replies_details_returns_list_of_dictionaries():
    # Arrange
    user_1 = User.objects.create(name='Mohan',
                                 profile_pic='Black adams')
    post_1 = Post.objects.create(content='first post',
                                 posted_at=datetime.now(),
                                 user_id=user_1.id)
    comment_one = Comment.objects.create(content='first reply',
                                         commented_at=datetime.now(),
                                         user=user_1,
                                         post_id=post_1.id)
    reply_one = Comment.objects.create(content='first reply',
                                       commented_at=datetime.now(),
                                       user=user_1,
                                       parent_id=comment_one.id)
    Reaction.objects.create(comment_id=reply_one.id,
                            react='HAHA',
                            reacted_at=datetime.now(),
                            user_id=user_1.id)

    list_of_dictionaries = defaultdict(list,
                                       {1: [{'comment_id': 2,
                                             'commenter': {'user_id': 1,
                                                           'name': 'Mohan',
                                                           'profile_pic':
                                                               'Black adams'},
                                             'commented_at': '2022-11-14 '
                                                             '05:52:30+00:00',
                                             'comment_content': 'first reply',
                                             'reactions': [{'count': 1,
                                                            'type': [
                                                                'HAHA']}]}]})

    # Act
    output = get_replies_details([comment_one.id])

    # Assert
    assert output == list_of_dictionaries


@freeze_time("2022-11-14 05:52:30+00:00", tz_offset=-4)
@pytest.mark.django_db
def test_get_comments_details_returns_list_of_dictionaries():
    # Arrange
    user_1 = User.objects.create(name='Mohan',
                                 profile_pic='Black adams')
    post_1 = Post.objects.create(content='first post',
                                 posted_at=datetime.now(),
                                 user_id=user_1.id)
    comment_one = Comment.objects.create(content='first comment',
                                         commented_at=datetime.now(),
                                         user=user_1,
                                         post_id=post_1.id)
    comment_two = Comment.objects.create(content='second comment',
                                         commented_at=datetime.now(),
                                         user=user_1,
                                         post_id=post_1.id)
    Reaction.objects.create(comment_id=comment_one.id,
                            react='HAHA',
                            reacted_at=datetime.now(),
                            user_id=user_1.id)
    Reaction.objects.create(comment_id=comment_two.id,
                            react='WOW',
                            reacted_at=datetime.now(),
                            user_id=user_1.id)

    list_of_dictionaries = defaultdict(list,
                                       {1: [{'comment_id': 1,
                                             'commenter': {'user_id': 1,
                                                           'name': 'Mohan',
                                                           'profile_pic':
                                                               'Black adams'},
                                             'commented_at': '2022-11-14 '
                                                             '05:52:30+00:00',
                                             'comment_content': 'first comment',
                                             'reaction': [
                                                 {'count': 1, 'type': [
                                                     'HAHA']}],
                                             'replies_count': 0,
                                             'replies': []},
                                            {'comment_id': 2,
                                             'commenter': {'user_id': 1,
                                                           'name': 'Mohan',
                                                           'profile_pic': 'Black adams'
                                                           },
                                             'commented_at': '2022-11-14 '
                                                             '05:52:30+00:00',
                                             'comment_content': 'second comment',
                                             'reaction': [
                                                 {'count': 1, 'type': [
                                                     'WOW']}],
                                             'replies_count': 0,
                                             'replies': []}]})

    # Act
    output = get_comments_details([post_1.id])

    # Assert
    assert output == list_of_dictionaries


@freeze_time("2022-11-14 05:52:30+00:00", tz_offset=-4)
@pytest.mark.django_db
def test_get_posts_returns_list_of_dictionaries():
    # Arrange
    user_1 = User.objects.create(name='Mohan',
                                 profile_pic='Black adams')
    post_1 = Post.objects.create(content='first post',
                                 posted_at=datetime.now(),
                                 user_id=user_1.id)
    comment_one = Comment.objects.create(content='first comment',
                                         commented_at=datetime.now(),
                                         user=user_1,
                                         post_id=post_1.id)
    comment_two = Comment.objects.create(content='second comment',
                                         commented_at=datetime.now(),
                                         user=user_1,
                                         post_id=post_1.id)
    Reaction.objects.create(comment_id=comment_one.id,
                            react='HAHA',
                            reacted_at=datetime.now(),
                            user_id=user_1.id)
    Reaction.objects.create(comment_id=comment_two.id,
                            react='WOW',
                            reacted_at=datetime.now(),
                            user_id=user_1.id)

    list_of_dictionaries = [{'post_id': 1,
                             'posted_by': {'user_id': 1,
                                           'name': 'Mohan',
                                           'profile_pic':
                                               'Black adams'},
                             'posted_at': '2022-11-14 ''05:52:30+00:00',
                             'post_content': 'first post',
                             'reactions': [],
                             'comments': [{'comment_id': 1,
                                           'commenter': {'user_id': 1,
                                                         'name': 'Mohan',
                                                         'profile_pic':
                                                             'Black adams'},
                                           'commented_at': '2022-11-14 '
                                                           '05:52:30+00:00',
                                           'comment_content': 'first comment',
                                           'reaction': [
                                               {'count': 1, 'type': ['HAHA']}],
                                           'replies_count': 0,
                                           'replies': []},
                                          {'comment_id': 2,
                                           'commenter': {'user_id': 1,
                                                         'name': 'Mohan',
                                                         'profile_pic':
                                                             'Black adams'},
                                           'commented_at': '2022-11-14 '
                                                           '05:52:30+00:00',
                                           'comment_content': 'second comment',
                                           'reaction': [
                                               {'count': 1, 'type': ['WOW']}],
                                           'replies_count': 0,
                                           'replies': []}],
                             'comments_count': 2}]

    # Act
    output = get_posts([post_1.id])

    # Assert
    assert output == list_of_dictionaries


@freeze_time("2022-11-14 05:52:30+00:00", tz_offset=-4)
@pytest.mark.django_db
def test_get_user_posts_validate_user():
    # Arrange
    user_1 = User.objects.create(name='Mohan',
                                 profile_pic='Black adams')
    post_1 = Post.objects.create(content='first post',
                                 posted_at=datetime.now(),
                                 user_id=user_1.id)
    comment_one = Comment.objects.create(content='first comment',
                                         commented_at=datetime.now(),
                                         user=user_1,
                                         post_id=post_1.id)
    comment_two = Comment.objects.create(content='second comment',
                                         commented_at=datetime.now(),
                                         user=user_1,
                                         post_id=post_1.id)
    Reaction.objects.create(comment_id=comment_one.id,
                            react='HAHA',
                            reacted_at=datetime.now(),
                            user_id=user_1.id)
    Reaction.objects.create(comment_id=comment_two.id,
                            react='WOW',
                            reacted_at=datetime.now(),
                            user_id=user_1.id)

    # Act
    with pytest.raises(Exception) as e:
        get_user_posts(2)
    # Assert
    assert str(e.value) == "InvalidUserException"


@freeze_time("2022-11-14 05:52:30+00:00", tz_offset=-4)
@pytest.mark.django_db
def test_get_user_posts_returns_list_of_dictionaries():
    # Arrange
    user_1 = User.objects.create(name='Mohan',
                                 profile_pic='Black adams')
    post_1 = Post.objects.create(content='first post',
                                 posted_at=datetime.now(),
                                 user_id=user_1.id)
    comment_one = Comment.objects.create(content='first comment',
                                         commented_at=datetime.now(),
                                         user=user_1,
                                         post_id=post_1.id)
    comment_two = Comment.objects.create(content='second comment',
                                         commented_at=datetime.now(),
                                         user=user_1,
                                         post_id=post_1.id)
    Reaction.objects.create(comment_id=comment_one.id,
                            react='HAHA',
                            reacted_at=datetime.now(),
                            user_id=user_1.id)
    Reaction.objects.create(comment_id=comment_two.id,
                            react='WOW',
                            reacted_at=datetime.now(),
                            user_id=user_1.id)

    list_of_dictionaries = [{'post_id': 1,
                             'posted_by': {'user_id': 1,
                                           'name': 'Mohan',
                                           'profile_pic':
                                               'Black adams'},
                             'posted_at': '2022-11-14 ''05:52:30+00:00',
                             'post_content': 'first post',
                             'reactions': [],
                             'comments': [{'comment_id': 1,
                                           'commenter': {'user_id': 1,
                                                         'name': 'Mohan',
                                                         'profile_pic':
                                                             'Black adams'},
                                           'commented_at': '2022-11-14 '
                                                           '05:52:30+00:00',
                                           'comment_content': 'first comment',
                                           'reaction': [
                                               {'count': 1, 'type': ['HAHA']}],
                                           'replies_count': 0,
                                           'replies': []},
                                          {'comment_id': 2,
                                           'commenter': {'user_id': 1,
                                                         'name': 'Mohan',
                                                         'profile_pic':
                                                             'Black adams'},
                                           'commented_at': '2022-11-14 '
                                                           '05:52:30+00:00',
                                           'comment_content': 'second comment',
                                           'reaction': [
                                               {'count': 1, 'type': ['WOW']}],
                                           'replies_count': 0,
                                           'replies': []}],
                             'comments_count': 2}]

    # Act
    output = get_user_posts(user_1.id)

    # Assert
    assert output == list_of_dictionaries


@freeze_time("2022-11-14 05:52:30+00:00", tz_offset=-4)
@pytest.mark.django_db
def test_get_user_posts_validate_user():
    # Arrange
    user_1 = User.objects.create(name='Mohan',
                                 profile_pic='Black adams')
    post_1 = Post.objects.create(content='first post',
                                 posted_at=datetime.now(),
                                 user_id=user_1.id)
    comment_one = Comment.objects.create(content='first comment',
                                         commented_at=datetime.now(),
                                         user=user_1,
                                         post_id=post_1.id)
    comment_two = Comment.objects.create(content='second comment',
                                         commented_at=datetime.now(),
                                         user=user_1,
                                         post_id=post_1.id)
    Reaction.objects.create(comment_id=comment_one.id,
                            react='HAHA',
                            reacted_at=datetime.now(),
                            user_id=user_1.id)
    Reaction.objects.create(comment_id=comment_two.id,
                            react='WOW',
                            reacted_at=datetime.now(),
                            user_id=user_1.id)

    # Act
    with pytest.raises(Exception) as e:
        get_user_posts(2)
    # Assert
    assert str(e.value) == "InvalidUserException"


@freeze_time("2022-11-14 05:52:30+00:00", tz_offset=-4)
@pytest.mark.django_db
def test_get_user_posts_returns_list_of_dictionaries():
    # Arrange
    user_1 = User.objects.create(name='Mohan',
                                 profile_pic='Black adams')
    post_1 = Post.objects.create(content='first post',
                                 posted_at=datetime.now(),
                                 user_id=user_1.id)
    comment_one = Comment.objects.create(content='first comment',
                                         commented_at=datetime.now(),
                                         user=user_1,
                                         post_id=post_1.id)
    comment_two = Comment.objects.create(content='second comment',
                                         commented_at=datetime.now(),
                                         user=user_1,
                                         post_id=post_1.id)
    Reaction.objects.create(comment_id=comment_one.id,
                            react='HAHA',
                            reacted_at=datetime.now(),
                            user_id=user_1.id)
    Reaction.objects.create(comment_id=comment_two.id,
                            react='WOW',
                            reacted_at=datetime.now(),
                            user_id=user_1.id)
    list_of_dictionaries = [{'post_id': 1,
                             'posted_by': {'user_id': 1,
                                           'name': 'Mohan',
                                           'profile_pic': 'Black adams'},
                             'posted_at': '2022-11-14 ''05:52:30+00:00',
                             'post_content': 'first post',
                             'reactions': [],
                             'comments': [{'comment_id': 1,
                                           'commenter': {'user_id': 1,
                                                         'name': 'Mohan',
                                                         'profile_pic':
                                                             'Black adams'},
                                           'commented_at': '2022-11-14 '
                                                           '05:52:30+00:00',
                                           'comment_content': 'first comment',
                                           'reaction': [
                                               {'count': 1, 'type': ['HAHA']}],
                                           'replies_count': 0,
                                           'replies': []},
                                          {'comment_id': 2,
                                           'commenter': {'user_id': 1,
                                                         'name': 'Mohan',
                                                         'profile_pic':
                                                             'Black adams'},
                                           'commented_at': '2022-11-14 '
                                                           '05:52:30+00:00',
                                           'comment_content': 'second comment',
                                           'reaction': [
                                               {'count': 1, 'type': ['WOW']}],
                                           'replies_count': 0,
                                           'replies': []}],
                             'comments_count': 2}]

    # Act
    output = get_user_posts(user_1.id)

    # Assert
    assert output == list_of_dictionaries


@freeze_time("2022-11-14 05:52:30+00:00", tz_offset=-4)
@pytest.mark.django_db
def test_get_replies_for_comments_validate_comment():
    # Arrange
    user_1 = User.objects.create(name='Mohan',
                                 profile_pic='Black adams')
    post_1 = Post.objects.create(content='first post',
                                 posted_at=datetime.now(),
                                 user_id=user_1.id)
    comment_one = Comment.objects.create(content='first comment',
                                         commented_at=datetime.now(),
                                         user=user_1,
                                         post_id=post_1.id)
    comment_two = Comment.objects.create(content='second comment',
                                         commented_at=datetime.now(),
                                         user=user_1,
                                         post_id=post_1.id)
    Reaction.objects.create(comment_id=comment_one.id,
                            react='HAHA',
                            reacted_at=datetime.now(),
                            user_id=user_1.id)
    Reaction.objects.create(comment_id=comment_two.id,
                            react='WOW',
                            reacted_at=datetime.now(),
                            user_id=user_1.id)

    # Act
    with pytest.raises(Exception) as e:
        get_replies_for_comments(3)
    # Assert
    assert str(e.value) == "InvalidCommentException"


@freeze_time("2022-11-14 05:52:30+00:00", tz_offset=-4)
@pytest.mark.django_db
def test_get_replies_for_comments_returns_list_of_dictionaries(snapshot):
    # Arrange
    user_1 = User.objects.create(name='Mohan',
                                 profile_pic='Black adams')
    post_1 = Post.objects.create(content='first post',
                                 posted_at=datetime.now(),
                                 user_id=user_1.id)
    comment_one = Comment.objects.create(content='first comment',
                                         commented_at=datetime.now(),
                                         user_id=user_1.id,
                                         post_id=post_1.id)
    Comment.objects.create(content='first reply',
                           commented_at=datetime.now(),
                           user=user_1,
                           parent_id=comment_one.id)

    list_of_dictionaries = [{'comment_id': 2,
                             'commenter': {'user_id': 1,
                                           'name': 'Mohan',
                                           'profile_pic': 'Black adams'},
                             'commented_at': '2022-11-14 ''05:52:30+00:00',
                             'comment_content': 'first reply'}]

    # Act
    output = get_replies_for_comments(comment_one.id)

    # Assert
    k = json.dumps(list_of_dictionaries)
    snapshot.assert_match(k, output)