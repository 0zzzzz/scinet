from django.db import models
from authapp.models import SNUser
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.db.models import Sum
from django.contrib.contenttypes.fields import GenericRelation
from ckeditor.fields import RichTextField

NULLABLE = {'blank': True, 'null': True}


class SNSections(models.Model):
    """Разделы"""
    name = models.CharField(max_length=64, unique=True, verbose_name='Название раздела')
    title = models.CharField(max_length=30, verbose_name='Title раздела')
    description = models.TextField(verbose_name='Описание раздела')
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.name}'

    class Meta:
        verbose_name = 'Раздел'
        verbose_name_plural = 'Разделы'


class LikeDislikeManager(models.Manager):
    """Менеджер лайков"""
    use_for_related_fields = True

    def likes(self):
        return self.get_queryset().filter(vote__gt=0)

    def dislikes(self):
        return self.get_queryset().filter(vote__lt=0)

    def sum_rating(self):
        return self.get_queryset().aggregate(Sum('vote')).get('vote__sum') or 0

    def posts(self):
        return self.get_queryset().filter(content_type__model='snposts').order_by('-id')

    def comments(self):
        return self.get_queryset().filter(content_type__model='sncomments').order_by('-id')


class LikeDislike(models.Model):
    """Лайки"""
    LIKE = 1
    DISLIKE = -1

    VOTES = (
        (DISLIKE, 'Не нравится'),
        (LIKE, 'Нравится')
    )

    vote = models.SmallIntegerField(verbose_name='Голос', choices=VOTES)
    user = models.ForeignKey(SNUser, verbose_name='Пользователь', on_delete=models.CASCADE)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()

    objects = LikeDislikeManager()


class SNPosts(models.Model):
    """Посты"""
    section = models.ForeignKey(SNSections, on_delete=models.CASCADE, verbose_name='Раздел поста', **NULLABLE)
    user = models.ForeignKey(SNUser, on_delete=models.CASCADE, verbose_name='Автор')
    name = models.CharField(max_length=128, verbose_name='Заголовок поста')
    image = models.ImageField(upload_to='posts', blank=True, null=True, verbose_name='Превьюшка поста')
    # text = models.TextField(verbose_name='Текст поста')
    text = RichTextField(verbose_name='Текст поста')
    short_desc = models.CharField(max_length=255, verbose_name='Краткое описание поста')
    is_active = models.BooleanField(default=True, db_index=True)
    is_moderated = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    votes = GenericRelation(LikeDislike, related_query_name='snposts')

    def __str__(self):
        return f'{self.name}'

    class Meta:
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'

    def moderated(self):
        self.is_moderated = True
        self.is_active = True
        self.save()


class Comments(models.Model):
    """Комментарии"""
    user = models.ForeignKey(SNUser, on_delete=models.CASCADE, verbose_name='Комментатор')
    post = models.ForeignKey(SNPosts, on_delete=models.CASCADE, verbose_name='Пост')
    text = models.CharField(max_length=1000, verbose_name='Текст комментария')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True, db_index=True)
    votes = GenericRelation(LikeDislike, related_query_name='sncomments')

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'


class SNSubscribe(models.Model):
    """Подписки пользователя"""
    user = models.ForeignKey(SNUser, on_delete=models.CASCADE, verbose_name='Пользователь')
    section = models.ForeignKey(SNSections, on_delete=models.CASCADE, verbose_name='Раздел на который он подписан')


class Notifications(models.Model):
    """Уведомления"""

    # LIKE_NOTIFICATION = 'L'
    # COMMENT_NOTIFICATION = 'C'
    #
    # MODES = (
    #     (LIKE_NOTIFICATION, 'Лайк'),
    #     (COMMENT_NOTIFICATION, 'Комментарий')
    # )

    # post = models.ForeignKey(SNPosts, on_delete=models.CASCADE, verbose_name='Пост')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_seen = models.BooleanField(default=False, db_index=True)
    is_active = models.BooleanField(default=True, db_index=True)
    # mode = models.CharField(max_length=1, verbose_name="Вид уведомления", choices=MODES, default=LIKE_NOTIFICATION)
    from_user = models.ForeignKey(SNUser, on_delete=models.CASCADE, verbose_name='Уведомитель',
                                  related_name='%(class)s_notifier')
    to_user = models.ForeignKey(SNUser, on_delete=models.CASCADE, verbose_name='Пользователь',
                                related_name='%(class)s_getter')

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()

    class Meta:
        verbose_name = 'Уведомление'
        verbose_name_plural = 'Уведомления'

    @classmethod
    def create(cls, content_type, object_id, to_user, from_user):
        notification = cls(content_type=content_type, object_id=object_id, to_user=to_user, from_user=from_user)
        return notification


class SNFavorites(models.Model):
    """Избранное пользователя"""
    user = models.ForeignKey(SNUser, on_delete=models.CASCADE, verbose_name='Пользователь')
    post = models.ForeignKey(SNPosts, on_delete=models.CASCADE, verbose_name='Пост')
