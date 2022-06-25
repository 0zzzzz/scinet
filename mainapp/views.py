import random
from blogapp.models import SNSections, SNPosts
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.forms.models import model_to_dict
from mainapp.filters import PostsFilter


def get_links_menu():
    return SNSections.objects.filter(is_active=True)


class RandomSNPostDetailView(DetailView):
    """Для клика по логотипу: Переход на случайную статью"""
    model = SNPosts
    # Необходимо добавить шаблон для постов
    template_name = 'mainapp/post.html'

    def get_object(self, queryset=None):
        return random.sample(list(SNPosts.objects.exclude(is_active=False)), 1)[0]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['links_menu'] = get_links_menu()
        return context


class SNPostsListView(ListView):
    """Отображение постов в категории (или всех) по дате создания"""
    model = SNPosts
    template_name = 'mainapp/index.html'

    def get_queryset(self):
        section_pk = self.kwargs.get('pk')
        if section_pk is None:
            section_pk = 0
        queryset = super().get_queryset().filter(is_active=True).order_by('-created_at')
        if section_pk != 0:
            queryset = queryset.filter(is_moderated=True, is_active=True, section__pk=section_pk)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        section_pk = self.kwargs.get('pk')
        context['posts'] = SNPosts.objects.filter(is_moderated=True, is_active=True).order_by('-created_at')
        context['links_menu'] = get_links_menu()
        context['category'] = SNSections.objects.filter(pk=section_pk)
        context['categories'] = SNSections.objects.all()
        context['title'] = 'Главная'
        context['filter'] = PostsFilter(self.request.GET, queryset=self.get_queryset())
        return context


class SNPostDetailView(DetailView):
    """Отображение_поста"""
    model = SNPosts
    # Необходимо добавить шаблон для постов
    template_name = 'mainapp/post.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['links_menu'] = get_links_menu()
        return context
