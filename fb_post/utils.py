from fb_post.models import Reaction, User, Post, Comment
from django.db.models import *
from collections import Counter, defaultdict
from fb_post.exceptions import InvalidUserException, InvalidPostException, \
    InvalidPostContent, InvalidCommentContent, InvalidReplyContent, \
    InvalidReactionTypeException, UserCannotDeletePostException


def validate_user(user_id):
    try:
        User.objects.get(pk=user_id)
    except:
        raise InvalidUserException("InvalidUserException")


def validate_post(post_id):
    try:
        Post.objects.get(pk=post_id)
    except:
        raise InvalidPostException("InvalidPostException")


def validate_comment(comment_id):
    try:
        Comment.objects.get(pk=comment_id)
    except:
        raise InvalidUserException("InvalidCommentException")


def create_post(user_id, post_content):
    validate_user(user_id)
    if len(post_content) == 0:
        raise InvalidPostContent("InvalidPostContent")
    new_post = Post.objects.create(user_id=user_id, content=
    post_content)
    return new_post.pk


def create_comment(user_id, post_id, comment_content):
    validate_user(user_id)
    validate_post(post_id)
    if len(comment_content) == 0:
        raise InvalidCommentContent("InvalidCommentContent")
    new_comment = Comment.objects.create(content=comment_content, user_id=
    user_id, post_id=post_id)
    return new_comment.pk


def reply_to_comment(user_id, comment_id, reply_content):
    validate_user(user_id)
    validate_comment(comment_id)
    if len(reply_content) == 0:
        raise InvalidReplyContent("InvalidReplyContent")
    post_object = Post.objects.get(user_id=user_id)
    reply_comment = Comment.objects.create(content=reply_content, user_id=
    user_id, post=post_object, parent_id=comment_id)
    return reply_comment.id


def react_to_post(user_id, post_id, reaction_type):
    list_of_reaction = ["WOW", "LIT", "LOVE", "HAHA", "THUMBS-UP",
                        "THUMBS-DOWN", "ANGRY", "SAD"]
    validate_user(user_id)
    validate_post(post_id)
    frequency = Counter(list_of_reaction)
    if frequency[reaction_type] <= 0:
        raise InvalidReactionTypeException("InvalidReactionTypeException")

    reaction = Reaction.objects.filter(user_id=user_id)
    if len(reaction) > 0:
        if reaction[0].react == reaction_type:
            Reaction.objects.filter(user_id=user_id).delete()
        else:
            Reaction.objects.filter(user_id=user_id).update(
                react=reaction_type)

    else:
        Reaction.objects.create(user_id=user_id,
                                post_id=post_id,
                                react=reaction_type)


def react_to_comment(user_id, comment_id, reaction_type):
    list_of_reaction = ["WOW", "LIT", "LOVE", "HAHA", "THUMBS-UP",
                        "THUMBS-DOWN", "ANGRY", "SAD"]
    validate_user(user_id)
    validate_comment(comment_id)
    frequency = Counter(list_of_reaction)
    if frequency[reaction_type] <= 0:
        raise InvalidReactionTypeException("InvalidReactionTypeException")

    reaction = Reaction.objects.filter(user_id=user_id)
    if len(reaction) > 0:
        if reaction[0].react == reaction_type:
            Reaction.objects.filter(user_id=user_id).delete()
        else:
            Reaction.objects.filter(user_id=user_id).update(
                react=reaction_type)

    else:
        Reaction.objects.create(user_id=user_id,
                                comment_id=comment_id,
                                react=reaction_type)


def get_total_reaction_count():
    reaction_count = Reaction.objects.aggregate(count=Count(
        'reaction'))
    return reaction_count


def get_reaction_metrics(post_id):
    validate_post(post_id)
    reactions = Reaction.objects.filter(
        post=post_id).values('post_id',
                             'reaction').annotate(Count('reaction'))
    reaction_materics = {reaction['reaction']: reaction['reaction__count']
                         for reaction in reactions}
    return reaction_materics


def delete_post(user_id, post_id):
    validate_user(user_id)
    validate_post(post_id)

    if user_id not in Post.objects.filter(id=post_id).values_list(
            'user', flat=True):
        raise UserCannotDeletePostException(
            'UserCannotDeletePostException')

    Post.objects.filter(pk=post_id).delete()


def get_posts_with_more_positive_reactions():
    positive_reaction = ('HAHA', 'LOL', 'WOW', 'LOVE', 'LIT')
    negative_reaction = ('SAD', 'THUMBS-DOWN', 'ANGRY')
    posts = Reaction.objects.values('post_id').annotate(
        positive_reaction_count=Count(Case(
            When(react__in=positive_reaction, then=1),
            output_field=IntegerField(),
        )), negative_reaction_count=Count(Case(
            When(react__in=negative_reaction, then=1),
            output_field=IntegerField(),
        ))).filter(positive_reaction_count__gt=F('negative_reaction_count')) \
        .values_list('post_id', flat=True)
    return list(posts)


def get_posts_reacted_by_user(user_id):
    validate_user(user_id)

    posts = Post.objects.filter(reaction__user=user_id).values_list('id',
                                                                    flat=True)
    return list(posts)


def get_reactions_to_post(post_id):
    validate_post(post_id)
    reactions_list = list(Reaction.objects.filter(
        post_id=post_id).select_related('user'))
    reactions = [
        {
            "user_id": reaction.user.id,
            "name": reaction.user.name,
            "profile_pic": reaction.user.profile_pic,
            "reaction": reaction.react,
        }
        for reaction in reactions_list
    ]
    return reactions


def get_user_details(user_id):
    user = User.objects.get(id=user_id)
    user_detail = {
        "user_id": user_id,
        "name": user.name,
        "profile_pic": user.profile_pic
    }
    return user_detail


def get_reactions_detail(post_ids):
    """
    :param post_ids:
    :return:
    """
    reactions_list = list(Reaction.objects.filter(
        post_id__in=post_ids).select_related('post'))
    reactions_obj = defaultdict(list)
    for reaction in reactions_list:
        reactions_obj[reaction.post_id].append(reaction)

    data = defaultdict(list)
    for reactions in reactions_list:
        reaction_detail_dict = dict()
        reaction_detail_dict["count"] = len(reactions_obj[reactions.post_id])
        type_of_reaction = set()
        for i in reactions_obj[reactions.post_id]:
            type_of_reaction.add(i.react)
        reaction_detail_dict["type"] = set(type_of_reaction)
        data[reactions.post_id].append(reaction_detail_dict)
    return data


def get_reactions_detail_of_comments(comment_ids):
    """
    :param comment_ids:
    :return:
    """
    reactions_list = list(Reaction.objects.filter(
        comment_id__in=comment_ids).select_related('comment'))
    reaction_obj = defaultdict(list)
    for reaction in reactions_list:
        reaction_obj[reaction.comment_id].append(reaction)

    data = defaultdict(list)
    for reactions in reactions_list:
        reaction_detail_dict = dict()
        reaction_detail_dict["count"] = len(reaction_obj[reactions.comment_id])
        type_of_reaction = set()
        for i in reaction_obj[reactions.comment_id]:
            type_of_reaction.add(i.react)
        reaction_detail_dict["type"] = list(type_of_reaction)
        data[reactions.comment_id].append(reaction_detail_dict)
    return data


def get_reactions_detail_of_comments_replies(comment_ids):
    """
    :param comment_ids:
    :return:
    """
    reactions_list = list(Reaction.objects.filter(
        comment__parent_id__in=comment_ids).select_related('comment'))
    g = defaultdict(list)
    for reaction in reactions_list:
        g[reaction.comment_id].append(reaction)

    d = defaultdict(list)
    for reactions in reactions_list:
        reaction_detail_dict = dict()
        reaction_detail_dict["count"] = len(g[reactions.comment_id])
        type_of_reaction = set()
        for i in g[reactions.comment_id]:
            type_of_reaction.add(i.react)
        reaction_detail_dict["type"] = list(type_of_reaction)
        d[reactions.comment_id].append(reaction_detail_dict)
    return d


def get_replies_details(comment_ids):
    """
    :param comment_ids:
    :return:
    """
    reply_list = list(Comment.objects.filter(
        parent_id__in=comment_ids).select_related('user'))
    x = get_reactions_detail_of_comments_replies(comment_ids)
    d = defaultdict(list)
    for i in reply_list:
        reactions_details = x[i.id]
        reply_detail = dict()
        reply_detail["comment_id"] = i.pk
        user_detail_dict = {"user_id": i.user.id,
                            "name": i.user.name,
                            "profile_pic": i.user.profile_pic}
        reply_detail["commenter"] = user_detail_dict
        reply_detail["commented_at"] = str(i.commented_at)
        reply_detail["comment_content"] = i.content
        reply_detail["reactions"] = reactions_details
        d[i.parent_id].append(reply_detail)
    return d


def get_comments_details(post_ids):
    """
    :param post_ids:
    :return:{1:[{1:}, {]}
    """
    comment_list = list(
        Comment.objects.filter(post_id__in=post_ids).select_related(
            'user'))
    d = defaultdict(list)
    comment_ids = list(Comment.objects.filter(
        post_id__in=post_ids).values_list('id', flat=True)
                       )
    x = get_replies_details(comment_ids)
    y = get_reactions_detail_of_comments(comment_ids)
    for i in comment_list:
        replies = x[i.id]
        reactions_details = y[i.id]
        comment_details = dict()
        comment_details["comment_id"] = i.pk
        user_detail_dict = {"user_id": i.user.id,
                            "name": i.user.name,
                            "profile_pic": i.user.profile_pic}
        comment_details["commenter"] = user_detail_dict
        comment_details["commented_at"] = str(i.commented_at)
        comment_details["comment_content"] = i.content
        comment_details["reaction"] = reactions_details
        comment_details["replies_count"] = len(replies)
        comment_details["replies"] = replies
        d[i.post_id].append(comment_details)
    return d


def get_posts(post_ids):
    """
    :param post_ids:
    :return:
    """
    for post_id in post_ids:
        validate_post(post_id)

    post_objs = Post.objects.filter(id__in=post_ids).select_related(
        'user')
    list_of_posts = []
    x = get_comments_details(post_ids)
    y = get_reactions_detail(post_ids)
    for post_obj in post_objs:
        comments = x[post_obj.id]
        reactions = y[post_obj.id]
        user_detail_dict = {"user_id": post_obj.user.id,
                            "name": post_obj.user.name,
                            "profile_pic": post_obj.user.profile_pic}
        detail_dict = {

            "post_id": post_obj.id,
            "posted_by": user_detail_dict,
            "posted_at": str(post_obj.posted_at),
            "post_content": post_obj.content,
            "reactions": reactions,
            "comments": comments,
            "comments_count": len(comments)
        }
        list_of_posts.append(detail_dict)
    return list_of_posts


def get_user_posts(user_id):
    """
    :param user_id:
    :return:
    """
    validate_user(user_id)

    posts = Post.objects.filter(user_id=user_id).values()
    list_of_post_ids = [post['id'] for post in posts]
    post_list = get_posts(list_of_post_ids)
    return post_list


def get_replies_for_comments(comment_id):
    """
    :param comment_id:
    :return:
    """
    validate_comment(comment_id)

    reply_list = list(Comment.objects.filter(
        parent_id=comment_id).select_related('user'))
    all_replies = list()
    for reply in reply_list:
        single_reply_detail = dict()
        single_reply_detail["comment_id"] = reply.pk
        user_detail_dict = {"user_id": reply.user.id,
                            "name": reply.user.name,
                            "profile_pic": reply.user.profile_pic}
        single_reply_detail["commenter"] = user_detail_dict
        single_reply_detail["commented_at"] = str(reply.commented_at)
        single_reply_detail["comment_content"] = reply.content
        all_replies.append(single_reply_detail)
    return all_replies





