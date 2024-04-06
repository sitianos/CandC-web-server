from django.urls import path
from . import views

#app_name='candc'
urlpatterns = [
    path('', views.index, name='index'),
    path('notify/', views.notify, name='notify'),
    path('action/', views.action, name='action'),
    path('upload/', views.upload, name='upload'),
    path('download/', views.download, name='download'),
    path('download/<path:path>', views.download, name='download'),
]
