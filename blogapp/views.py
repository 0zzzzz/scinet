from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, UpdateView, DeleteView, DetailView, ListView
from django.template.loader import render_to_string
from django.http import JsonResponse

from adminapp.views import AccessMixin, DeleteMixin
from authapp.models import SNUser
from blogapp.forms import SNPostForm, CommentForm
from blogapp.models import SNPosts, Comments, LikeDislike, Notifications, SNFavorites, Ip

import json
from django.http import HttpResponse
from django.views import View
from django.contrib.contenttypes.models import ContentType


class SNPostDetailView(DetailView):
    """Показывает пост"""
    model = SNPosts
    template_name = 'blogapp/post_crud/post_view.html'
    form_class = CommentForm

    def get_context_data(self, *args, **kwargs):
        """Засчитывание просмотров"""
        ip = get_user_ip(self.request)
        try:
            ip_object = Ip.objects.get(ip=ip)
        except Ip.DoesNotExist:
            ip_object = Ip.create(ip=ip)
            ip_object.save()
        self.object.views.add(ip_object)

        context = super().get_context_data(**kwargs)
        context['form'] = self.form_class
        context['post'] = SNPosts.objects.get(pk=self.kwargs['pk'])
        context['comments'] = Comments.objects.filter(is_active=True, post__pk=self.kwargs['pk'])
        context['title'] = 'Пост'
        context['is_favorite'] = False
        if self.request.user.is_authenticated:
            if SNFavorites.objects.filter(Q(user=self.request.user) &
                                          Q(post=SNPosts.objects.get(pk=self.kwargs['pk']))):
                context['is_favorite'] = True
        return context

    def get_success_url(self):
        return reverse('blogs:post_read', args=[self.kwargs['pk']])

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            form = self.form_class(request.POST)
            if form.is_valid():
                comment = form.save(
                    commit=False)
                comment.user = request.user
                comment.post = SNPosts.objects.get(pk=self.kwargs['pk'])
                comment.save()
                notify_comment(comment)
                return HttpResponseRedirect(self.get_success_url())


@method_decorator(login_required, name='dispatch')
class SNPostCreateView(CreateView):
    """Создание поста"""
    model = SNPosts
    template_name = 'blogapp/post_crud/post_form.html'
    success_url = reverse_lazy('index')
    form_class = SNPostForm

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Создание поста'
        return context

    def post(self, request, *args, **kwargs):
        """Автоматически делаем пользователя сессии автором поста"""
        if request.user.is_authenticated:
            form = self.form_class(request.POST)
            if form.is_valid():
                blog_post = form.save(
                    commit=False)
                blog_post.user = request.user
                blog_post.save()
                return HttpResponseRedirect(reverse("index"))


@method_decorator(login_required, name='dispatch')
class SNPostUpdateView(UpdateView):
    """Редактирование поста"""
    model = SNPosts
    template_name = 'blogapp/post_crud/post_form.html'
    form_class = SNPostForm
    success_url = reverse_lazy('index')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Редактирование поста'
        return context


@method_decorator(login_required, name='dispatch')
class SNPostDeleteView(DeleteView):
    """Удаление поста"""
    model = SNPosts
    template_name = 'blogapp/post_crud/post_delete.html'

    def get_success_url(self):
        return reverse('index')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Удаление поста'
        return context

    def form_valid(self, form, *args, **kwargs):
        """По умолчанию скрывает пост, если отметить чекбокс, то удалит пост полностью"""
        success_url = self.get_success_url()
        checkbox = self.request.POST.get('del_box', None)
        if checkbox:
            self.object.delete()
            return HttpResponseRedirect(success_url)
        else:
            if self.object.is_active:
                self.object.is_active = False
            else:
                self.object.is_active = True
            self.object.save()
            return HttpResponseRedirect(success_url)


@method_decorator(login_required, name='dispatch')
class CommentCreateView(CreateView):
    """Создание комментария"""
    model = Comments
    template_name = 'blogapp/comment_crud/comment_create.html'
    form_class = CommentForm

    def get_success_url(self):
        return reverse('blogs:post_read', args=[self.kwargs['post_pk']])

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            form = self.form_class(request.POST)
            if form.is_valid():
                post_pk = self.kwargs['post_pk']
                comment = form.save(
                    commit=False)
                comment.user = request.user
                comment.post = SNPosts.objects.get(pk=post_pk)
                comment.save()
                notify_comment(comment)
                return HttpResponseRedirect(self.get_success_url())


@method_decorator(login_required, name='dispatch')
class CommentUpdateView(UpdateView):
    """Редактирование комментария"""
    model = Comments
    template_name = 'blogapp/comment_crud/comment_create.html'
    form_class = CommentForm

    def get_success_url(self):
        return reverse('blogs:post_read', args=[self.kwargs['post_pk']])


@method_decorator(login_required, name='dispatch')
class CommentDeleteView(DeleteView):
    """Удаление комментария"""
    model = Comments
    template_name = 'blogapp/comment_crud/comment_delete.html'

    def get_success_url(self):
        return reverse('blogs:post_read', args=[self.kwargs['post_pk']])

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.is_active = False
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())


# @method_decorator(login_required, name='dispatch')
class VotesView(View):
    """Лайки"""
    model = None
    """Модель данных (лайк статьи или комментария)"""
    vote_type = None
    """Like or dislike"""

    def post(self, request, pk):
        obj = self.model.objects.get(pk=pk)
        """GenericForeignKey не поддерживает метод get_or_create"""
        try:
            likedislike = LikeDislike.objects.get(content_type=ContentType.objects.get_for_model(obj), object_id=obj.id,
                                                  user=request.user)
            if likedislike.vote is not self.vote_type:
                likedislike.vote = self.vote_type
                likedislike.save(update_fields=['vote'])
                notify_like(likedislike)
                result = True
            else:
                likedislike.delete()
                result = False
        except LikeDislike.DoesNotExist:
            likedislike = obj.votes.create(user=request.user, vote=self.vote_type)
            notify_like(likedislike)
            result = True

        return HttpResponse(
            json.dumps({
                'result': result,
                'like_count': obj.votes.likes().count(),
                'dislike_count': obj.votes.dislikes().count(),
                'sum_rating': obj.votes.sum_rating()
            }),
            content_type='application/json'
        )


def get_user_ip(request):
    """Функции для обработки просмотров"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[-1].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


@method_decorator(login_required, name='dispatch')
class NotificationListView(ListView):
    """Уведомления. Отображение всех уведомлений пользователя"""
    model = Notifications
    template_name = 'authapp/user_auth/notifications.html'

    def get_queryset(self):
        user_notifications = super().get_queryset().filter(to_user=self.request.user, is_active=True). \
            order_by('-updated_at')
        return make_equal_notifications(user_notifications)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Уведомления'
        return context


@login_required
def delete_notification(request, pk):
    """Удалить уведомление"""
    notification = Notifications.objects.get(pk=pk)
    notification.is_active = False
    notification.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required
def delete_all_notifications(request):
    """Удалить все уведомления"""
    notifications = Notifications.objects.filter(to_user=request.user, is_active=True)
    for el in notifications:
        el.is_active = False
        el.save()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))



def is_ajax(request):
    """Вспомогательные функции для уведомлений"""
    """Почему-то is_ajax не хотел работать, нашел такое вот решение"""
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'


def make_equal_notifications(notifications):
    """Создает словари по уведомлениям, чтобы привести форматы их данных к одному виду"""
    user_notifications = notifications
    notifications_list = []
    for notify in user_notifications:
        try:
            new_obj = dict()
            new_obj['pk'] = notify.id
            new_obj['from_user'] = notify.from_user
            new_obj['created_at'] = notify.created_at
            new_obj['is_seen'] = notify.is_seen
            content_type = notify.content_type
            # Проверяем, что за контент несет с собой уведомление
            if content_type.model == 'snposts':
                new_obj['name'] = 'одобрил публикацию поста:'
                post = content_type.get_object_for_this_type(id=notify.object_id)
            elif content_type.model == 'comments':
                comment = content_type.get_object_for_this_type(id=notify.object_id)
                new_obj['name'] = f'оставил комментарий: "{comment.text}" под постом:'
                post = comment.post
            elif content_type.model == 'likedislike':
                # У лайков тоже свой контент, поэтому еще проверки
                like = content_type.get_object_for_this_type(id=notify.object_id)
                liked_object = like.content_type.get_object_for_this_type(id=like.object_id)
                if like.content_type.model == 'snposts':
                    if like.vote == 1:
                        new_obj['name'] = 'оценил пост:'
                    else:
                        new_obj['name'] = 'негативно оценил пост:'
                    post = liked_object
                elif like.content_type.model == 'comments':
                    if like.vote == 1:
                        new_obj['name'] = f'оценил комментарий под постом: {liked_object.post.name}'
                    else:
                        new_obj['name'] = f'негативно оценил комментарий под постом: {liked_object.post.name}'
                    post = liked_object.post
            new_obj['post'] = post
            notifications_list.append(new_obj)
        except (LikeDislike.DoesNotExist, Comments.DoesNotExist, SNPosts.DoesNotExist) as e:
            notify.is_seen = True
    return notifications_list


def seen_notifications(request):
    """Помечает уведомления как просмотренные"""
    if is_ajax(request):
        notifications = Notifications.objects.filter(to_user=request.user, is_active=True).order_by('-updated_at')
        for el in notifications:
            if not el.is_seen:
                el.is_seen = True
            el.save()

        context = {
            'object_list': make_equal_notifications(notifications),
        }

        result = render_to_string('authapp/includes/inc_notifications.html', context)

        return JsonResponse({'result': result})


def check_notifications(request):
    """Проверяет наличие уведомлений"""
    if is_ajax(request):
        notifications = Notifications.objects.filter(to_user=request.user, is_active=True, is_seen=False)
        if len(notifications) > 0:
            new_notify = True
        else:
            new_notify = False

        context = {
            'new_notify': new_notify,
            'user': request.user,
        }

        result = render_to_string('mainapp/includes/inc_menu.html', context)

        return JsonResponse({'result': result})


def notify_like(likedislike):
    """Функция для создания уведомления по лайку"""
    from_user = likedislike.user
    content_type = ContentType.objects.get_for_model(likedislike)
    like_id = likedislike.id
    like_obj = likedislike.content_type.get_object_for_this_type(id=likedislike.object_id)
    to_user = like_obj.user

    try:
        notification = Notifications.objects.get(object_id=like_id, content_type=content_type, to_user=to_user,
                                                 from_user=from_user)
        notification.is_seen = False
    except Notifications.DoesNotExist:
        notification = Notifications.create(content_type, like_id, to_user, from_user)
    notification.save()


def notify_comment(comment):
    """Функция для создания уведомления по комментарию"""
    from_user = comment.user
    content_type = ContentType.objects.get_for_model(comment)
    comment_id = comment.id
    to_user = comment.post.user

    notification = Notifications.create(content_type, comment_id, to_user, from_user)
    notification.save()

    
class Favorites(ListView):
    """Показывает всё избранное пользователя"""
    model = SNFavorites
    template_name = 'blogapp/favorites/section_favorites.html'

    def get(self, request):
        """Получаем для шаблона всё избранное конкретного пользователя"""
        user = SNUser.objects.get(username=request.user)
        user_favorites = SNFavorites.objects.filter(user=user.id)
        context = {
            'user_favorites': user_favorites,
        }
        return render(request, self.template_name, context=context)


def change_favorites(request, pk):
    """Добавляет статью в избранное если её там нет, и удаляет если наоборот"""
    user = SNUser.objects.get(username=request.user)
    post = get_object_or_404(SNPosts, id=pk)
    if not SNFavorites.objects.filter(Q(user=user) & Q(post=post)):
        subscribe = SNFavorites(user=user, post=post)
        subscribe.save()
    else:
        SNFavorites.objects.filter(Q(user=user) & Q(post=post)).delete()
    return HttpResponseRedirect(reverse('blogapp:favorites'))

