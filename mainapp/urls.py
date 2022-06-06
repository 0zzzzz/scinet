from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from mainapp import views as mainapp

app_name = 'mainapp'

urlpatterns = [
    path('<int:pk>', mainapp.SNPostsListView.as_view(), name='section'),
    path('random', mainapp.RandomSNPostDetailView.as_view(), name='read_random'),
    path('read/<pk>/', mainapp.SNPostDetailView.as_view(), name='read'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

