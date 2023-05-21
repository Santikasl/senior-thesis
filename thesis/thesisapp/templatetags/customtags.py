from django import template
from ..models import *
from django.db.models import Q
import re

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
    chats_sender = Chat.objects.filter(Q(sender=profile) & Q(receiver=follow))
    chats_receiver = Chat.objects.filter(Q(sender=follow) & Q(receiver=profile))
    for message in chats_sender:
        if message.receiver == follow:
            messages.extend({"sender": item} for item in chats_sender)
            messages.extend({"receiver": item} for item in chats_receiver)
            sorted_messages = sorted(messages,
                                     key=lambda x: x.get('sender').timestamp if 'sender' in x else x.get('receiver').timestamp)

            return sorted_messages
        else:
            return None



@register.filter(name='smile')
def smile(content):
    regex = re.compile("[\U0001F000-\U0001F6FF\U00002600-\U000027BF\U0001F300-\U0001F5FF\u200d]+", re.UNICODE)
    return bool(regex.search(content))


@register.filter(name='chatCounter')
def chatCounter(pk,user):
    sender = Profile.objects.get(user=user)
    receiver = Profile.objects.get(pk=pk)
    messages = Chat.objects.filter(sender=receiver, receiver=sender)
    return messages.count()