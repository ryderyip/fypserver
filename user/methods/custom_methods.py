from datetime import datetime

from django.core.handlers.wsgi import WSGIRequest
from django.db.models import Q

from user.models import UserCommonInfo, Student, Teacher, Admin


def common_info_from_post_get_or_create(request: WSGIRequest):
    email = request.POST['email']
    username = request.POST.get('username')
    info = UserCommonInfo.objects.filter(
        Q(email__exact=email) | Q(username__exact=username))
    if not info.exists():
        return UserCommonInfo.objects.create(
            name=request.POST['name'],
            gender=request.POST['gender'],
            date_of_birth=datetime.fromisoformat(request.POST['date_of_birth']),
            phone=request.POST['phone'],
            email=email,
            username=username,
            password=request.POST['password'])
    return info.get()


def filter_user_from_get_by_name_email_phone(request: WSGIRequest,
                                             model: type[Student, Teacher, Admin]):
    search_term = request.GET.get('search_term')
    user_id_for_search = request.GET.get('user_id_for_search')

    objs = model.objects.all()

    if user_id_for_search:
        return objs.filter(id=user_id_for_search)

    if search_term:
        objs = objs.filter(Q(info__name__icontains=search_term.strip())
                           | Q(info__email__icontains=search_term.strip())
                           | Q(info__phone__icontains=search_term.strip())
                           | Q(info__username__icontains=search_term.strip()))
    return objs


def update_info_from_post(request: WSGIRequest, info: UserCommonInfo):
    info.name = request.POST['name']
    info.gender = request.POST['gender']
    info.date_of_birth = datetime.fromisoformat(request.POST['date_of_birth'])
    info.phone = request.POST['phone']
    info.email = request.POST['email']
    info.password = request.POST['password']
    info.username = request.POST.get('username')
    info.save()