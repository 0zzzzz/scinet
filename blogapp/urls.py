from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from blogapp import views as blogapp
from .models import LikeDislike, SNPosts, Comments

app_name = 'blogapp'

urlpatterns = [
    path('post_create/', blogapp.SNPostCreateView.as_view(), name='post_create'),
    path('post_read/<pk>/', blogapp.SNPostDetailView.as_view(), name='post_read'),
    path('post_update/<pk>/', blogapp.SNPostUpdateView.as_view(), name='post_update'),
    path('post_delete/<pk>/', blogapp.SNPostDeleteView.as_view(), name='post_delete'),

    path('comment_create/<post_pk>', blogapp.CommentCreateView.as_view(), name='comment_create'),
    path('comment_delete/<post_pk>/<pk>', blogapp.CommentDeleteView.as_view(), name='comment_delete'),
    path('comment_update/<post_pk>/<pk>', blogapp.CommentUpdateView.as_view(), name='comment_update'),

    path('notifications/', blogapp.NotificationListView.as_view(), name='notifications'),
    path('notification_delete/<pk>', blogapp.delete_notification, name='notification_delete'),
    path('notifications_delete/', blogapp.delete_all_notifications, name='notifications_delete_all'),
    path('notifications/notifications_set_seen/', blogapp.seen_notifications, name='notifications_set_seen'),

    path('favorites/', blogapp.Favorites.as_view(), name='favorites'),
    path('favorites/change/<pk>', blogapp.change_favorites, name='favorite_change'),

    path('post/<pk>/like/', blogapp.VotesView.as_view(model=SNPosts, vote_type=LikeDislike.LIKE),
         name='post_like'),
    path('post/<pk>/dislike/', blogapp.VotesView.as_view(model=SNPosts, vote_type=LikeDislike.DISLIKE),
         name='post_dislike'),
    path('comment/<pk>/like/', blogapp.VotesView.as_view(model=Comments, vote_type=LikeDislike.LIKE),
         name='comment_like'),
    path('comment/<pk>/dislike/', blogapp.VotesView.as_view(model=Comments, vote_type=LikeDislike.DISLIKE),
         name='comment_dislike'),

]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
