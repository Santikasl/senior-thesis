from PIL import Image, ImageDraw
from django.db import models
from datetime import datetime
from django.core.validators import *
from django.contrib.auth.models import User
from django.core.files import File
import qrcode
from io import BytesIO


def default_datetime():
    return datetime.now()


class Profile(models.Model):
    MALE_CHOICES = (
        ('female', 'FEMALE'),
        ('male', 'MALE'),
    )
    name = models.CharField(max_length=100, default='none')
    following = models.ManyToManyField(User, related_name='following', blank=True)
    img = models.ImageField(upload_to='images/', default='images/default.png')
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    male = models.CharField(max_length=6, choices=MALE_CHOICES, default='male')
    qr_code = models.ImageField(upload_to='qr_code/', blank=True)

    def __str__(self):
        return str(self.name)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        qrcode_img = qrcode.make('http://localhost:8000/' + str(self.pk))
        canvas = Image.new('RGB', (350, 350), 'white')
        draw = ImageDraw.Draw(canvas)
        canvas.paste(qrcode_img)
        fname = f'qr_code-{self.name}.png'
        buffer = BytesIO()
        canvas.save(buffer, 'PNG')
        self.qr_code.save(fname, File(buffer), save=False)
        canvas.close()
        super().save(*args, **kwargs)


class Posts(models.Model):
    description = models.TextField(max_length=2000)
    date = models.DateTimeField(default=default_datetime)
    user = models.ForeignKey(Profile, null=True, blank=True, on_delete=models.CASCADE, related_name='creators')
    img = models.ImageField(upload_to='posts/')
    liked = models.ManyToManyField(User, default=None, blank=True)

    @property
    def num_likes(self):
        return self.liked.all().count()

    def save(self, **kwargs):
        super().save()
        img = Image.open(self.img.path)

        if img.height > 900 or img.width > 900:
            output_size = (720, 900)
            img.thumbnail(output_size)
            img.save(self.img.path)

    def __str__(self):
        return "Публикация пользователя: " + str(self.user)


class Facts(models.Model):
    description = models.TextField(max_length=2000)

    def __str__(self):
        return "Факт № " + str(self.pk)


class Comments(models.Model):
    creator = models.ForeignKey(Profile, on_delete=models.CASCADE, default=None, blank=True,
                                verbose_name='Пользователь')
    post = models.ForeignKey(Posts, on_delete=models.CASCADE, default=None, blank=True, verbose_name='Пост')
    text = models.TextField()
    date = models.DateTimeField(auto_now=True, null=True)
    replies = models.ForeignKey('self', null=True, blank=True, related_name='replies_to', on_delete=models.CASCADE)
    liked = models.ManyToManyField(User, default=None, blank=True, related_name="likeComment",
                                   verbose_name='Пользователи лайкнувшие комментарий')
    repliesUsername = models.CharField(max_length=20, null=True, blank=True, verbose_name="Имя пользователя для ответа")

    @property
    def num_likes(self):
        return self.liked.all().count()

    def __str__(self):
        return self.text

    class Meta:
        ordering = ['-date']
        verbose_name = 'Коментарий к посту'
        verbose_name_plural = "Коментарии к постам"


class Chat(models.Model):
    sender = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='received_messages', blank=True,
                                 null=True)
    content = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    file = models.FileField(default=None, blank=True, null=True)
    to_group = models.BooleanField(default=False)

    def __str__(self):
        message = self.content if self.content else "Файл"
        return f'{self.sender.name}:  {message} '


class Group(models.Model):
    name = models.CharField(blank=True, null=True, max_length=40)
    user = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='creator')
    members = models.ManyToManyField(Profile, related_name='members')
    messages = models.ManyToManyField(Chat, related_name='messages', null=True, blank=True)
    unic_id = models.IntegerField(null=True, blank=True, default=None)

    def __str__(self):
        return f'Группа {self.name}'
