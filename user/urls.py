from django.urls import path
from . import views

urlpatterns = [
    path('login', views.login_as_nonadmin),
    path('admin/login', views.login_as_admin),
    path('student/create', views.create_new_student),
    path('student/get', views.get_students),
    path('student/update', views.update_student),
    path('student/remove', views.remove_student),
    path('teacher/create', views.create_new_teacher),
    path('teacher/get', views.get_teachers),
    path('teacher/update', views.update_teacher),
    path('teacher/remove', views.remove_teacher),
    path('teacher/occupation/get', views.get_occupations),
    path('admin/get', views.get_admins),
    path('admin/create', views.create_new_admin),
    path('admin/update', views.update_admin),
    path('admin/remove', views.remove_admin),
    path('availability_check/username', views.check_is_username_available),
    path('availability_check/email', views.check_is_email_available),
]
