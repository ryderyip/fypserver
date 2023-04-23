from django.urls import path
from . import views

urlpatterns = [
    path('question/get', views.get_QALibQuestions),
    path('question/save', views.save_QALibQuestion),
    path('question/remove', views.remove_QALibQuestion),
    path('question/rate', views.rate_QALibQuestion),
    path('content_block/get', views.get_QALibContentBlock),
    path('answer/get', views.get_QALibAnswers),
    path('answer/save', views.save_QALibAnswers),
    path('answer/remove', views.remove_QALibAnswer),
    path('tag/get', views.get_tags),
    path('tag/create', views.create_tag),
    path('tag/update', views.update_tag),
    path('image/upload', views.upload_image),
]
