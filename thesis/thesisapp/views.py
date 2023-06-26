import urllib
import urllib
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, \
    PasswordResetCompleteView
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.hashers import check_password
from django.db.models import Q
from django.views.generic import ListView, View
from django.shortcuts import redirect, render
from django.http import JsonResponse
from django.contrib import messages
from .models import *
from .forms import *
import random
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404


class Index(ListView, PasswordResetView):
    queryset = Profile
    template_name = 'thesisapp/index.html'

    def get_context_data(self, **kwargs):
        context = super(Index, self).get_context_data(**kwargs)
        form = AuthForm()
        register_form = ExtendedRegisterForm()
        password = PasswordResetForm()

        context = {
            'form': form,
            'password': password,
            'register_form': register_form,
        }

        return context

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('main')
        return super().get(request)


class SignIn(View):
    def post(self, request):
        auth_form = AuthForm(request.POST)
        if auth_form.is_valid():
            name = auth_form.cleaned_data['name']
            password = auth_form.cleaned_data['password']
            user = User.objects.filter(username=name.lower()).first()
            if not user:
                messages.error(request, "Пользователь не найден, пожалуйста зарегистрируйтесь")
                return redirect(request.META.get('HTTP_REFERER') + '#3')
            elif not check_password(password, user.password):
                messages.error(request, "Проверьте правильность пароля")
                return redirect(request.META.get('HTTP_REFERER') + '#3')
            else:
                login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                return redirect('main')


class MyPasswordResetDoneView(PasswordResetDoneView):
    def get(self, request):
        messages.error(request, "Ссылка отправлена, проверьте прочту")
        return redirect('index')


class MyPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'thesisapp/reset_password.html'


class MyPasswordResetCompleteView(PasswordResetCompleteView):
    def get(self, request):
        messages.error(request, "Пароль успешно изменён, войдите в аккаунт")
        return redirect('index')


class SignUp(View):
    def post(self, request):
        register_form = ExtendedRegisterForm(request.POST)
        if register_form.is_valid():
            password = request.POST.get("password1")
            password2 = request.POST.get("password2")
            username = register_form.cleaned_data.get('username').lower()
            email = register_form.cleaned_data.get('email')
            if User.objects.filter(username=username).first():
                messages.error(request, "Пользователь с таким ником уже существует")
                return redirect(request.META.get('HTTP_REFERER') + '#3')
            elif User.objects.filter(email=email).first():
                messages.error(request, "Пользователь с таким e-mail уже существует")
                return redirect(request.META.get('HTTP_REFERER') + '#3')
            elif password == password2:
                profile = Profile()
                profile.name = request.POST.get("username").lower()
                profile.male = request.POST.get("male")
                profile.email = request.POST.get("email")
                profile.password = request.POST.get("password1")
                profile.user = register_form.save()
                profile.save()
                raw_password = register_form.cleaned_data.get('password1')
                user = authenticate(username=username.lower(), password=raw_password)
                login(request, user)
                return redirect('main')
            else:
                return redirect(request.META.get('HTTP_REFERER') + '#3')
        else:
            return redirect(request.META.get('HTTP_REFERER') + '#3')


def logout_user(request):
    logout(request)
    port = request.META.get('SERVER_PORT')
    host = request.META.get('REMOTE_ADDR')
    return redirect('http://' + host + ':' + port + '/' + '#3')


class Main(ListView):
    queryset = Profile
    template_name = 'thesisapp/main.html'
    context_object_name = 'profile'

    def get(self, request):
        if not request.user.is_authenticated:
            port = request.META.get('SERVER_PORT')
            host = request.META.get('REMOTE_ADDR')
            return redirect('http://' + host + ':' + port + '/' + '#3')
        else:
            super().get(request)
            profile = Profile.objects.get(user=request.user)
            follows = profile.user.following.all()
            users = [user for user in follows]
            post_follow = []
            for u in users:
                posts = Posts.objects.filter(user=u).first()

                if posts is not None:
                    post_follow.append(posts)
            comments = Comments.objects.filter(post__in=post_follow)
            chats_sender = Chat.objects.filter(sender=profile, receiver__in=follows)
            context = self.get_context_data()
            post = NewPosts()
            context = {
                'profile': profile,
                'post': post,
                'post_follow': post_follow,
                'comments': comments,
                'follows': follows,
                'num': chats_sender.count()
            }
            return self.render_to_response(context)


class UserProfile(ListView):
    queryset = Profile
    template_name = 'thesisapp/profile.html'
    context_object_name = 'profile'

    def post(self, request):
        profile = Profile.objects.get(user=request.user)
        imgForm = Imgform(request.POST, request.FILES)
        if imgForm.is_valid():
            if imgForm.cleaned_data['img'] is not None:
                profile.img = imgForm.cleaned_data['img']
                profile.save()
                return redirect('profile')
        else:
            return redirect('profile')

    def get(self, request):
        if not request.user.is_authenticated:
            port = request.META.get('SERVER_PORT')
            host = request.META.get('REMOTE_ADDR')
            return redirect('http://' + host + ':' + port + '/' + '#3')
        else:
            super().get(request)
            profile = Profile.objects.get(user=request.user)
            user_post = Posts.objects.filter(user=profile).order_by('-date')
            context = self.get_context_data()
            follow = profile.user.following.all()
            all_followers = profile.following.all()
            comments = Comments.objects.filter(post__in=user_post)

            followers = Profile.objects.filter(user__in=all_followers)
            context = {
                'followers': followers,
                'follow': follow,
                'user_post': user_post,
                'imgForm': Imgform(),
                'comments': comments,
                'profile': profile,
                'post': NewPosts(),

            }
            return self.render_to_response(context)


class NewPost(View):
    def post(self, request):
        profile = Profile.objects.get(user=request.user)
        post = Posts(user=profile)
        newPost = NewPosts(request.POST, request.FILES)
        if newPost.is_valid():
            post.img = newPost.cleaned_data['postImg']
            post.description = newPost.cleaned_data['description']
            post.save()
            return redirect('profile')


class CommentView(View):
    def post(self, request):
        user = request.user
        profile = Profile.objects.get(user=user)
        post_id = request.POST.get('post_id')
        post_obj = Posts.objects.get(id=post_id)
        message = request.POST.get('comment')
        mats = ["ромашка", "розочка", "лилия"]
        words = message.split()
        new_string = ''
        for word in words:
            if word in mats:
                count = len(word)
                mat = '*' * count
                new_string = message.replace(word, mat)
        comments = Comments.objects.create(creator=profile, post=post_obj, text=new_string if new_string else message)

        data = {
            'user': comments.creator.name,
            'id': comments.pk
        }
        return JsonResponse(data, safe=False)


class MessageView(View):

    def post(self, request):
        if request.method == 'POST':
            if request.POST.get('unic_id'):
                sender = Profile.objects.get(user=request.user)
                group = Group.objects.get(unic_id=request.POST.get('unic_id'))
                message = request.POST.get('message')

                mats = ["ромашка", "розочка", "лилия"]
                words = message.split()
                new_string = ''
                for word in words:
                    if word in mats:
                        count = len(word)
                        mat = '*' * count
                        new_string = message.replace(word, mat)
                if message:
                    message = Chat.objects.create(sender=sender, content=new_string if new_string else message,
                                                  to_group=True)
                    group.messages.add(message)
                    group.save()
                data = {
                    "text": message.content
                }
                return JsonResponse(data, safe=False)
            else:
                sender = Profile.objects.get(user=request.user)
                receiver = Profile.objects.get(pk=request.POST.get('follow_pk'))
                message = request.POST.get('message')
                mats = ["ромашка", "розочка", "лилия"]
                like = request.POST.get('like')
                words = message.split()
                new_string = ''
                for word in words:
                    if word in mats:
                        count = len(word)
                        mat = '*' * count
                        new_string = message.replace(word, mat)
                if not message:
                    message = Chat.objects.create(sender=sender, receiver=receiver, content=like)
                else:
                    message = Chat.objects.create(sender=sender, receiver=receiver,
                                                  content=new_string if new_string else message)
                data = {
                    "text": message.content
                }
                return JsonResponse(data, safe=False)


def sent_file(request):
    if request.method == 'POST':
        if request.POST.get('unic_id'):
            sender = Profile.objects.get(user=request.user)
            group = Group.objects.get(unic_id=request.POST.get('unic_id'))
            if request.FILES.get("add-file"):
                photo = request.FILES.get("add-file")
                message = Chat.objects.create(sender=sender, file=photo, to_group=True)
                group.messages.add(message)
                group.save()
            return redirect('massage')
        else:
            sender = Profile.objects.get(user=request.user)
            receiver = Profile.objects.get(pk=request.POST.get('follow_pk'))
            if request.FILES.get("add-file"):
                photo = request.FILES.get("add-file")
                message = Chat.objects.create(sender=sender, receiver=receiver, file=photo)
            return redirect('massage')


class ReceiveMessageView(View):

    def get(self, request):
        sender = Profile.objects.get(user=request.user)
        query_string = request.META.get('QUERY_STRING')
        params = urllib.parse.parse_qs(query_string)
        follow_pk = params.get('follow_pk', [None])[0]
        if len(follow_pk) == 3:
            group = Group.objects.get(unic_id=follow_pk)
            all = group.messages.exclude(sender=sender)
            arr = []
            result = {'arr': [], 'user': [], 'userPk': []}  # Создание словаря с ключами-списками

            for i in all:
                if i.content is not None:
                    arr.append(i.content)
                    result['arr'].append(i.content)
                else:
                    arr.append(i.file.url)
                    result['arr'].append(i.file.url)

                result['user'].append(i.sender.img.url)
                result['userPk'].append(i.sender.pk)
            return JsonResponse(result, safe=False)
        receiver = Profile.objects.get(pk=follow_pk)
        all = Chat.objects.filter(sender=receiver, receiver=sender)
        arr = []
        result = {'arr': [], 'user': [], 'userPk': []}  # Создание словаря с ключами-списками
        for i in all:
            arr.append(i.content)
            result['arr'].append(i.content)
            if i.content is None:
                arr.append(i.file.url)
                result['arr'].append(i.file.url)
        return JsonResponse(result, safe=False)


class GetCountView(View):
    def get(self, request):
        sender = Profile.objects.get(user=request.user)
        query_string = request.META.get('QUERY_STRING')
        params = urllib.parse.parse_qs(query_string)
        follow_pk = params.get('follow_pk', [None])[0]
        if len(follow_pk) == 3:
            group = Group.objects.get(unic_id=follow_pk)
            all = group.messages.exclude(sender=sender)
            arr = []
            for i in all:
                if i.content is not None:
                    arr.append(i.content)
                else:
                    arr.append(i.file.url)

            countsss = len(arr)
            return JsonResponse(countsss, safe=False)
        receiver = Profile.objects.get(pk=follow_pk)
        all = Chat.objects.filter(sender=receiver, receiver=sender)
        arr = []
        for i in all:
            arr.append(i.content)
            if i.content is None and i.file is not None:
                arr.append(i.file.url)
        countsss = len(arr)
        return JsonResponse(countsss, safe=False)


class CommentLikeView(View):
    def post(self, request):
        user = request.user
        comments_id = request.POST.get('comments_id')
        if comments_id is None:
            comments_id = request.POST.get('ewfwegew')
        comment = Comments.objects.get(id=comments_id)
        if user in comment.liked.all():
            comment.liked.remove(user)
        else:
            comment.liked.add(user)
        data = {
            'num_likes': comment.num_likes,
        }
        return JsonResponse(data)


class Like(View):
    def post(self, request):
        user = request.user
        post_id = request.POST.get('post_id')
        post_obj = Posts.objects.get(id=post_id)
        if user in post_obj.liked.all():
            like = 'Like'
            post_obj.liked.remove(user)
        else:
            like = 'Unlike'
            post_obj.liked.add(user)
        data = {
            'like_value': like,
            'likes': post_obj.liked.all().count()
        }
        return JsonResponse(data, safe=False)


def delite(request):
    if request.method == 'POST':
        post_id = request.POST['id']
        post = Posts.objects.get(id=post_id)
        post.delete()
    return redirect('profile')

def newgroup(request):
    import random
    random_number = random.randint(100, 999)
    members = request.POST.getlist('members')
    profiles = Profile.objects.filter(user__username__in=members)
    name = request.POST['name']

    profile = Profile.objects.get(user=request.user)

    group = Group.objects.create(name=name, user=profile, unic_id=random_number)
    group.members.set(profiles)
    group.members.add(profile)

    return redirect('massage')



def edit(request):
    id = request.POST.get('id', None)
    post2 = Posts.objects.get(id=id)
    post2.description = request.POST.get('description', None)
    post2.save()
    data2 = post2.description
    res_post2 = data2
    return JsonResponse({'data': res_post2})


class Search(View):

    def post(self, request):
        res = None
        dataName = request.POST.get('dataName').strip().title()
        search_terms = dataName.split()

        qs = Profile.objects.all()

        if search_terms:
            qs = qs.filter(
                Q(user__first_name__icontains=search_terms[0]) |
                Q(user__last_name__icontains=search_terms[0])
            )

            for term in search_terms[1:]:
                qs = qs.filter(
                    Q(user__first_name__icontains=term) |
                    Q(user__last_name__icontains=term)
                )

        qs = qs[:4]

        if qs.exists() and dataName:
            data = []
            for pos in qs:
                name = f" {pos.user.first_name} {pos.user.last_name}"
                item = {
                    'pk': pos.pk,
                    'name': name,
                    'img': pos.img.url,
                }
                data.append(item)
            res = data
        else:
            res = 'Пользователь не найден'
        return JsonResponse({'data': res})

class SearchChat(View):

    def post(self, request):
        res = None
        dataName = request.POST.get('dataName').strip().title()
        search_terms = dataName.split()

        profile = Profile.objects.get(user=request.user)
        qs = profile.user.following.all()

        if search_terms:
            qs = qs.filter(
                Q(user__first_name__icontains=search_terms[0]) |
                Q(user__last_name__icontains=search_terms[0])
            )

            for term in search_terms[1:]:
                qs = qs.filter(
                    Q(user__first_name__icontains=term) |
                    Q(user__last_name__icontains=term)
                )

        qs = qs[:4]

        if qs.exists() and dataName:
            data = []
            for pos in qs:
                name = f" {pos.user.first_name} {pos.user.last_name}"
                item = {
                    'pk': pos.pk,
                    'name': name,
                    'img': pos.img.url,
                }
                data.append(item)
            res = data
            print(res)
        else:
            res = 'Пользователь не найден'
        return JsonResponse({'data': res})

class SearchProfile(ListView):
    queryset = Profile
    template_name = 'thesisapp/search_profile.html'
    context_object_name = 'searchProfile'

    def get(self, request, pk):
        anonim = False
        if not request.user.is_authenticated:
            anonim = True
            is_follow = False
        new_post = NewPosts()
        search_user = Profile.objects.get(pk=pk)
        profile = Profile.objects.filter(pk=pk).first()
        userFollowers = profile.following.all()
        followers = Profile.objects.filter(user__in=userFollowers)
        follow = profile.user.following.all()
        posts = Posts.objects.filter(user=search_user)
        try:
            user = Profile.objects.get(user=request.user)
            if profile == user:
                return redirect('profile')
            if user.user in profile.following.all():
                is_follow = True
            else:
                is_follow = False
        except Exception:
            user = None
            is_follow = False
        context = {
            'pk': pk,
            'is_follow': is_follow,
            'profile': profile,
            'posts': posts,
            'followers': followers,
            'follow': follow,
            'post': new_post,
            'anonim': anonim,
        }
        return render(request, 'thesisapp/search_profile.html', context)


class Follow(View):
    def post(self, request):
        if not request.user.is_authenticated:
            port = request.META.get('SERVER_PORT')
            host = request.META.get('REMOTE_ADDR')
            return redirect('http://' + host + ':' + port + '/' + '#3')
        else:
            if request.method == 'POST':
                my_profile = Profile.objects.get(user=request.user)
                pk = request.POST.get('profile_pk')
                obj = Profile.objects.get(pk=pk)
                if my_profile.user in obj.following.all():
                    obj.following.remove(my_profile.user)
                else:
                    obj.following.add(my_profile.user)
                return redirect(request.META.get('HTTP_REFERER'))


class Statistics(ListView):
    queryset = Profile
    template_name = 'thesisapp/statistics.html'

    def get(self, request):
        if not request.user.is_authenticated:
            port = request.META.get('SERVER_PORT')
            host = request.META.get('REMOTE_ADDR')
            return redirect('http://' + host + ':' + port + '/' + '#3')
        else:
            profile = Profile.objects.get(user=request.user)
            user_posts = Posts.objects.filter(user=profile)
            n = 0
            items = []
            all_post = []
            for post in user_posts:
                posts = {
                    'post': post,
                    'like': post.liked.all().count(),
                }
                all_post.append(posts)
                if post.liked.all().count() >= n:
                    items = {
                        'post': post,
                        'pk': post.pk,
                        'descriptions': post.description,
                        'img': post.img.url,
                        'like': post.liked.all().count(),
                        'user': post.user.id,
                        'imgUrl': post.user.img.url,
                        'name': post.user.name,
                    }
                    n = post.liked.all().count()
            followersUser = profile.following.all()
            followers = Profile.objects.filter(user__in=followersUser)
            count_male = 0
            count_female = 0
            for male in followers:
                if male.male == 'male':
                    count_male += 1
                else:
                    count_female += 1
            post = NewPosts()
            context = {
                'bestPost': items,
                'post': post,
                'count_male': count_male,
                'count_female': count_female,
                'all_post': all_post,
            }

            return render(request, 'thesisapp/statistics.html', context)


class MassageView(ListView):
    queryset = Chat
    template_name = 'thesisapp/massage.html'
    context_object_name = 'chat'

    def get(self, request):
        if not request.user.is_authenticated:
            port = request.META.get('SERVER_PORT')
            host = request.META.get('REMOTE_ADDR')
            return redirect('http://' + host + ':' + port + '/' + '#3')
        else:
            super().get(request)
            profile = Profile.objects.get(user=request.user)
            follows = profile.user.following.all()
            post = NewPosts()
            groups = Group.objects.filter(members=profile)
            context = {
                'profile': profile,
                'follows': follows,
                'post': post,
                'groups': groups,
            }
            return self.render_to_response(context)


class Settings(ListView, PasswordResetView):
    queryset = Profile
    template_name = 'thesisapp/settings.html'

    def get_context_data(self, **kwargs):
        context = super(Settings, self).get_context_data(**kwargs)
        password = PasswordResetForm()

        context = {
            'password': password,
        }

        return context
