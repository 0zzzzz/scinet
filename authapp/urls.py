from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from authapp import views as authapp

app_name = 'authapp'

urlpatterns = [
    path('login/', authapp.LoginView.as_view(), name='login'),
    path('logout/', authapp.LogoutView.as_view(), name='logout'),
    path('register/', authapp.RegisterView.as_view(), name='register'),
    # path('register/', authapp.register, name='register'),
    path('edit/', authapp.EditView.as_view(), name='edit'),
    path('profile/<str:username>', authapp.SNProfileDetailView.as_view(), name='profile_user'),
    path('posts/', authapp.SNPostDetailView.as_view(), name='posts_user_list'),
    path('subscribe/', authapp.SNSectionsDetailView.as_view(), name='section_subscribe'),
    path('subscribe/add/<int:pk>/', authapp.add_subscribe, name='subscribe_add'),
    path('subscribe/del/<int:pk>/', authapp.del_subscribe, name='subscribe_del'),
    path('comments/', authapp.SNCommentsDetailView.as_view(), name='user_comments'),
    path('dialogs/', authapp.SNDialogsView.as_view(), name='user_dialogs'),
    path('dialogs/create/<int:user_id>/', authapp.SNCreateDialogsView.as_view(), name='create_dialogs'),
    path('dialogs/<int:chat_id>/', authapp.SNDialogView.as_view(), name='view_dialog'),
    # path('api/user_create/', authapp.SNUserCreateAPIView.as_view(), name='api_user_create'),
    # path('api/user_update/<int:pk>/', authapp.SNUserUpdateAPIView.as_view(), name='api_user_update'),
    path('verify/<email>/<key>/', authapp.verify, name='verify'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
