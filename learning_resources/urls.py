from django.urls import path
from . import views

urlpatterns = [
    path('nonexercise/get', views.get_nonexercise_learning_resource),
    path('nonexercise/create', views.create_nonexercise_lr),
    path('nonexercise/remove', views.remove_nonexercise_lr),
    path('nonexercise/update', views.update_nonexercise_lr),
    path('exercise/get', views.get_exercise_learning_resource),
    path('exercise/create', views.create_exercise_lr),
    path('exercise/remove', views.remove_exercise_lr),
    path('exercise/update', views.update_exercise_lr),
    path('get', views.get_learning_resource),
    # path('exercise/textq/create', views.create_text_q),
    # path('exercise/textq/update', views.update_text_q),
    path('exercise/textq/remove', views.remove_text_q),
    path('exercise/mcq/create', views.create_mc_q),
    path('exercise/mcq/update', views.update_mc_q),
    path('exercise/mcq/remove', views.remove_mc_q),
    path('exercise/mcq/response/create', views.create_mc_q_res),
    path('exercise/mcq/response/get', views.get_mc_q_res),
    path('exercise/mcq/response/get_attempted_students', views.get_mc_q_attempted_students),
    path('exercise/mcq/option/create', views.create_mcq_option),
    path('exercise/mcq/option/update', views.update_mcq_option),
    path('exercise/mcq/option/remove', views.remove_mcq_option),
    path('exercise/clear', views.clear_exercise_lr),

]
