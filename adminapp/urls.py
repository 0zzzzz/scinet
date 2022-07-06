from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from adminapp import views as adminapp

app_name = 'adminapp'


urlpatterns = [
    path('users/', adminapp.SNUserListView.as_view(), name='users_list'),
    path('user/create/', adminapp.SNUserCreateView.as_view(), name='user_create'),
    path('user/update/<int:pk>/', adminapp.SNUserUpdateView.as_view(),
         name='user_update'),
    path('user/delete/<int:pk>/', adminapp.SNUserDeleteView.as_view(),
         name='user_delete'),

    # Урлы для секций
    path('sections/', adminapp.SNSectionListView.as_view(), name='sections'),
    path('sections/<int:pk>/', adminapp.SNSectionAllPostInCategories.as_view(), name='sections_all_posts'),
    path('sections/list/<int:pk>/', adminapp.SNSectionListView.as_view(), name='sections_list'),
    path('sections/create/', adminapp.SNSectionCreateView.as_view(), name='sections_create'),
    path('sections/update/<int:pk>/', adminapp.SNSectionUpdateView.as_view(), name='sections_update'),
    path('sections/delete/<int:pk>/', adminapp.SNSectionDeleteView.as_view(), name='sections_delete'),

    # Урлы для постов
    path('posts/', adminapp.SNPostsListView.as_view(), name='posts_list'),
    path('posts/<int:pk>/', adminapp.SNPostsDetail.as_view(), name='posts_detail'),
    path('post/create/', adminapp.SNPostCreateView.as_view(), name='post_create'),
    path('post/update/<int:pk>/', adminapp.SNPostUpdateView.as_view(),
         name='post_update'),
    path('post/delete/<int:pk>/', adminapp.SNPostDeleteView.as_view(),
         name='post_delete'),
    path('post/modarated/<int:pk>', adminapp.post_moderated, name='moderated'),

    path('locked_user/<int:pk>/', adminapp.locked, name='locked'),
    path('unlocked_user/<int:pk>/', adminapp.unlocked, name='unlocked'),

]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
