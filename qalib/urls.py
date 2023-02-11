from django.urls import path
from . import views

urlpatterns = [
    path('question/get', views.get_QALibQuestions),
    path('question/create', views.create_QALibQuestion),
    path('content_block/get', views.get_QALibContentBlock),
    path('content_block/save', views.save_QALibContentBlock),
    path('answer/get', views.get_QALibAnswers),
    path('answer/save', views.save_QALibAnswers),
]
