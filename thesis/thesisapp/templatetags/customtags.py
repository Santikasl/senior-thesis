from django import template
from ..models import *
from django.db.models import Q
import re
import os
from django import template
from django.core.files.storage import default_storage
import os

register = template.Library()


@register.filter(name='color')
def color(post, user):
    return user in post.liked.all()


@register.filter(name='count')
def color(follow):
    return follow.count()


@register.filter(name='comments')
def color(post):
    comments = Comments.objects.filter(post=post)
    return comments


@register.filter(name='message')
def message(follow, user):
    profile = Profile.objects.get(user=user)
    messages = []
    chats_sender = Chat.objects.filter(sender=profile, receiver=follow)
    chats_receiver = Chat.objects.filter(sender=follow, receiver=profile)

    messages.extend({"sender": item} for item in chats_sender)
    messages.extend({"receiver": item} for item in chats_receiver)
    sorted_messages = sorted(messages,
                             key=lambda x: x['sender'].timestamp if 'sender' in x else x['receiver'].timestamp)

    return sorted_messages if sorted_messages else None


@register.filter(name='smile')
def smile(content):
    regex = re.compile("[\u1F000-\u1F6FF\u2600-\u27BF\u1F300-\u1F5FF\u200d]+", re.UNICODE)
    return False if regex.search(content) else True


@register.filter(name='chatCounter')
def chatCounter(pk, user):
    sender = Profile.objects.get(user=user)
    receiver = Profile.objects.get(pk=pk)
    messages = Chat.objects.filter(sender=receiver, receiver=sender)
    return messages.count()


@register.filter(name='photo')
def is_photo(file):
    path = default_storage.path(file.name)
    extension = os.path.splitext(path)[1].lower()
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp']

    if extension in image_extensions and default_storage.exists(path):
        return True
    else:
        return False


@register.filter(name='messageGroup')
def message_group(group_pk, user):
    profile = Profile.objects.get(user=user)
    group = Group.objects.get(pk=group_pk)
    messages = []
    chats_sender = group.messages.filter(sender=profile)
    chats_receiver = group.messages.exclude(sender=profile)
    messages.extend({"sender": item} for item in chats_sender)
    messages.extend({"receiver": item} for item in chats_receiver)
    sorted_messages = sorted(messages,
                             key=lambda x: x['sender'].timestamp if 'sender' in x else x['receiver'].timestamp)

    return sorted_messages if sorted_messages else None


@register.filter(name='members')
def members(membersss):
    for i in membersss.members:
        print(i)

    return [1, 2, 3]\

@register.filter(name='two')
def two(name):
    string = name
    result = string[:2].upper()
    return result\

@register.filter(name='groupMessage')
def groupMessage(name):
    if name is None:
        name = "Начни диалог"
        return name
    return name
