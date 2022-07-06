from django.contrib import auth
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q
from django.http import Http404
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, ListView
from django.views.generic import View
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from authapp import tasks
from authapp.forms import SNUserLoginForm, SNUserRegisterForm, SNUserEditForm, SNUserProfileEditForm
from authapp.models import SNUser, SNUserProfile
from blogapp.models import SNPosts, SNSections, SNSubscribe, Comments
from authapp.serializers import SNUserSerializer


class LoginView(View):
    """Страница логина"""
    model = SNUser
    template_name = 'authapp/user_auth/login.html'
    form_class = SNUserLoginForm

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, context={'form': form,
                                                            'title': 'Логин'})

    def post(self, request):
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(username=username, password=password)
        if user.is_active and not user.user_blocked:
            auth.login(request, user)
            return HttpResponseRedirect(reverse('index'))
        form = self.form_class()
        return render(request, self.template_name, context={'form': form,
                                                            'title': 'Логин',
                                                            # 'error_text': 'Введён неправильный логин или пароль'})
                                                            'error_text': 'Ваш аккуант заблокирован'})


class LogoutView(View):
    """View для логаута"""

    def get(self, request):
        auth.logout(request)
        return HttpResponseRedirect(reverse('index'))


class RegisterView(CreateView):
    """Страница регистрации пользователя"""
    model = SNUser
    template_name = 'authapp/user_auth/register.html'
    success_url = reverse_lazy('index')
    form_class = SNUserRegisterForm

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Регистрация'
        return context

    def post(self, request, *args, **kwargs):
        register_form = SNUserRegisterForm(request.POST, request.FILES)

        if register_form.is_valid():
            register_form.save()
            # activate_key = self.request.user.snuser.activate_key
            # email_user = self.request.user.snuser.email
            # tasks.send_verify_email.delay(email_user, activate_key)
            return HttpResponseRedirect(reverse('auth:login'))

        context = {
            'register_form': register_form,
            'title': 'Регистрация пользователя',
        }
        return HttpResponseRedirect(reverse('auth:login'), context)


class EditView(View):
    """Страница редактирования профиля"""
    model = SNUser
    template_name = 'authapp/users_crud/user_form.html'
    form_class = SNUserEditForm
    success_url = reverse_lazy('authapp:users_list')

    def get(self, request):
        edit_form = SNUserEditForm(instance=self.request.user)
        edit_profile_form = SNUserProfileEditForm(instance=self.request.user.snuserprofile)
        context = {
            'title': 'Редактирование пользователя',
            'edit_form': edit_form,
            'edit_profile_form': edit_profile_form,
        }
        return render(self.request, 'authapp/user_auth/edit.html', context)

    def post(self, request, *args, **kwargs):
        edit_form = SNUserEditForm(request.POST, request.FILES, instance=request.user)
        edit_profile_form = SNUserProfileEditForm(request.POST, instance=request.user.snuserprofile)
        if edit_form.is_valid() and edit_profile_form.is_valid():
            edit_form.save()
            return HttpResponseRedirect(reverse('auth:edit'))


class SNUserCreateAPIView(APIView):
    """API Создание пользователя"""

    def get(self, request):
        item = SNUser.objects.all()
        serializer = SNUserSerializer(item, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = SNUserSerializer(data=request.data, many=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SNUserUpdateAPIView(APIView):
    """API Изменение пользователя"""

    def get_object(self, pk):
        try:
            return SNUser.objects.get(pk=pk)
        except SNUser.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        item = self.get_object(pk)
        serializer = SNUserSerializer(item)
        return Response(serializer.data)

    def put(self, request, pk):
        item = self.get_object(pk)
        serializer = SNUserSerializer(item, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        item = self.get_object(pk)
        item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class SNPostDetailView(ListView):
    """Показывает все посты пользователя"""
    model = SNPosts
    template_name = 'authapp/user_auth/all_users_post.html'

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)


class SNSectionsDetailView(ListView):
    """Показывает все разделы для подписки и отписки"""
    model = SNSections
    template_name = 'authapp/user_auth/section_subscribe.html'

    def get(self, request):
        """Получаем для шаблона все подписки конкретного пользователя"""
        section = SNSections.objects.all()
        user = SNUser.objects.get(username=request.user)
        user_subscribe = SNSubscribe.objects.filter(user=user.id)
        subscribe = []
        for el in user_subscribe:
            subscribe.append(el.section.id)
        context = {
            'section': section,
            'subscribe': subscribe,
        }
        return render(request, self.template_name, context=context)


def add_subscribe(request, pk):
    """Добавляет подписку для конкретного пользователя"""
    user = SNUser.objects.get(username=request.user)
    section = get_object_or_404(SNSections, id=pk)
    if not SNSubscribe.objects.filter(Q(user=user) & Q(section=section)):
        subscribe = SNSubscribe(user=user, section=section)
        subscribe.save()
    return HttpResponseRedirect(reverse('authapp:section_subscribe'))


def del_subscribe(request, pk):
    """Удаляет подписку для конкретного пользователя"""
    user = SNUser.objects.get(username=request.user)
    section = get_object_or_404(SNSections, id=pk)
    SNSubscribe.objects.filter(Q(user=user) & Q(section=section)).delete()
    return HttpResponseRedirect(reverse('authapp:section_subscribe'))


class SNCommentsDetailView(ListView):
    """Показывает все коментарии данного пользователя"""
    template_name = 'authapp/user_auth/show_comments.html'

    def get(self, request):
        """Получаем для шаблона все комментарии конкретного пользователя"""
        user = SNUser.objects.get(username=request.user)
        user_comments = Comments.objects.filter(user=user.id)
        context = {
            'user_comments': user_comments,
        }
        return render(request, self.template_name, context=context)


class SNProfileDetailView(ListView):
    """Показывает всю активность данного пользователя"""
    template_name = 'authapp/user_auth/new_profile.html'

    def get(self, request, username):
        """Получаем для шаблона все данные конкретного пользователя"""
        user = SNUser.objects.get(username=username)
        user_comments_count = Comments.objects.filter(user=user.id).count()
        user_post_count = SNPosts.objects.filter(user=user.id).count()
        context = {
            'user_profile': user,
            'user_comments_count': user_comments_count,
            'user_post_count': user_post_count,
        }
        return render(request, self.template_name, context=context)


def verify(request, email, key):
    user = SNUser.objects.filter(email=email).first()
    if user:
        if user.activate_key == key and not user.is_activation_key_expired():
            user.activate_user()
            auth.login(request, user, backend='django.contrib.auth.backends.ModelBackend')

    context = {
        'title': 'Активация',
    }

    return render(request, 'authapp/register_socifull.html', context)
