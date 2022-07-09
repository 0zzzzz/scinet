from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import ListView, CreateView, DeleteView, UpdateView, DetailView
from django.contrib.contenttypes.models import ContentType

from adminapp.forms import SNPostAdminForm, SNUserAdminEditForm
from authapp.forms import SNUserRegisterForm, SNUserEditForm
from authapp.models import SNUser
from blogapp.models import SNPosts, SNSections, Notifications
from adminapp.forms import SNSectionForm


class AccessMixin:
    """Делает view доступным только для суперпользователя"""

    @method_decorator(user_passes_test(lambda u: u.is_superuser))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class DeleteMixin:
    """Даёт выбор для полного удаления через чекбокс"""

    def form_valid(self, form, *args, **kwargs):
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


"""CRUD для управления пользователями"""


class SNUserCreateView(AccessMixin, CreateView):
    model = SNUser
    template_name = 'adminapp/users_crud/user_form.html'
    success_url = reverse_lazy('index')
    form_class = SNUserRegisterForm

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['title'] = 'Создание пользователя'
        return context


class SNUserListView(AccessMixin, ListView):
    model = SNUser
    template_name = 'adminapp/users_crud/users.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['object_list'] = SNUser.objects.all().order_by('-is_active')
        context['title'] = 'Список пользователей'
        return context


class SNUserUpdateView(AccessMixin, UpdateView):
    model = SNUser
    template_name = 'adminapp/users_crud/user_form.html'
    form_class = SNUserAdminEditForm
    success_url = reverse_lazy('index')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Редактирование пользователя'
        return context


class SNUserDeleteView(AccessMixin, DeleteMixin, DeleteView):
    model = SNUser
    template_name = 'adminapp/users_crud/user_delete.html'

    def get_success_url(self):
        return reverse('index')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Удаление пользователя'
        return context


"""CRUD для управления постами"""


class SNPostCreateView(AccessMixin, CreateView):
    model = SNPosts
    template_name = 'adminapp/posts_crud/post_form.html'
    success_url = reverse_lazy('index')
    form_class = SNPostAdminForm

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['title'] = 'Создание поста'
        return context


class SNPostsListView(AccessMixin, ListView):
    model = SNPosts
    template_name = 'adminapp/posts_crud/posts_list.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['object_list'] = SNPosts.objects.filter(is_moderated=False).order_by('-is_active')
        context['title'] = 'Список всех постов'
        return context


class SNPostUpdateView(AccessMixin, UpdateView):
    model = SNPosts
    template_name = 'adminapp/posts_crud/post_form.html'
    form_class = SNPostAdminForm
    success_url = reverse_lazy('index')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Редактирование поста'
        return context


class SNPostDeleteView(AccessMixin, DeleteMixin, DeleteView):
    model = SNPosts
    template_name = 'adminapp/posts_crud/post_delete.html'

    def get_success_url(self):
        return reverse('index')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Удаление поста'
        return context


class SNPostsDetail(AccessMixin, DetailView):
    model = SNPosts
    template_name = 'adminapp/posts_crud/post_detail.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['title'] = 'Детализация поста'
        return context


def notify_post(post, from_user):
    """Функция для создания уведомления по одобренному посту"""
    from_user = from_user
    content_type = ContentType.objects.get_for_model(post)
    post_id = post.id
    to_user = post.user

    notification = Notifications.create(content_type, post_id, to_user, from_user)
    notification.save()


def post_moderated(request, pk=None):
    moderate_post = SNPosts.objects.get(id=pk)
    if moderate_post:
        moderate_post.moderated()
        notify_post(moderate_post, request.user)
    return render(request, 'adminapp/posts_crud/post_moderated.html')


"""CRUD для управления категориями"""


class SNSectionListView(AccessMixin, ListView):
    model = SNSections
    template_name = 'adminapp/sections_crud/section_list.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['object_list'] = SNSections.objects.all().order_by('-is_active')
        context['title'] = 'Список всех постов'
        return context


class SNSectionAllPostInCategories(ListView):
    model = SNSections
    template_name = 'adminapp/sections_crud/all_post_in_category.html'

    # def get

    def get_context_data(self, pk=None, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['post_list'] = SNPosts.objects.filter(section__pk=self.kwargs.get('pk')).select_related('section')
        context['category_name'] = SNSections.objects.filter(id=self.kwargs.get('pk')).first()
        context['title'] = 'Список всех постов в категории'
        return context


class SNSectionCreateView(AccessMixin, CreateView):
    model = SNSections
    template_name = 'adminapp/sections_crud/sections_create.html'
    success_url = reverse_lazy('index')
    form_class = SNSectionForm

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['title'] = 'Создание поста'
        return context


class SNSectionUpdateView(AccessMixin, UpdateView):
    model = SNSections
    template_name = 'adminapp/sections_crud/sections_create.html'
    form_class = SNSectionForm
    success_url = reverse_lazy('adminapp:sections')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Редактирование поста'
        return context


class SNSectionDeleteView(AccessMixin, DeleteMixin, DeleteView):
    model = SNSections
    template_name = 'adminapp/sections_crud/sections_delete.html'

    def get_success_url(self):
        return reverse('adminapp:sections_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Удаление поста'
        return context


def locked(request, pk):
    user = SNUser.objects.filter(pk=pk).first()
    if user:
        user.locked_user()
    return render(request, 'adminapp/users_crud/user_blocked.html')


def unlocked(request, pk):
    user = SNUser.objects.filter(pk=pk).first()
    if user:
        user.unlocked_user()
    return render(request, 'adminapp/users_crud/user_unblocked.html')
