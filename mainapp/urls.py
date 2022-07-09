from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from mainapp import views as mainapp

app_name = 'mainapp'

urlpatterns = [
    path('<int:pk>/', mainapp.SNPostsListView.as_view(), name='posts'),  # заменил нейм с sections на posts
    path('random', mainapp.RandomSNPostDetailView.as_view(), name='read_random')
]
