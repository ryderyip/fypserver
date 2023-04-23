import json

from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from matplotlib.font_manager import json_dump

from factories.custom_methods import paginate_query, apply_user_sorting
from user.custom_serializers import *
from user.methods.custom_methods import *
from user.models import Student, Teacher, UserCommonInfo


@csrf_exempt
def login_as_nonadmin(request):
    email_username = request.POST['email_username']
    password = request.POST['password']

    info = UserCommonInfo.objects.filter(Q(email=email_username) | Q(username=email_username))

    if not info.exists() or info.first().password != password:
        return HttpResponse(status=401)

    info = info.first()
    query = Student.objects.filter(info=info)

    if not query.exists():
        query = Teacher.objects.filter(info=info)

    if not query.exists():
        return HttpResponse(content='commoninfo exists but user not exist', status=500)
    query = query.get()
    if isinstance(query, Student):
        serializer = StudentSerializer(query)
    else:
        serializer = TeacherSerializer(query)

    return JsonResponse(data=serializer.data, status=200)


def make_response_if_exist(info: UserCommonInfo, userModel: type[Student, Teacher, Admin]):
    existing_user = userModel.objects.filter(info=info)
    if existing_user.exists():
        existing_user = existing_user.first()
        msg = 'Student' if isinstance(existing_user, Student) else 'Teacher' if isinstance(
            existing_user, Teacher) else 'Admin'
        msg += f' with with email address \'{info.email}\''
        if existing_user.info.username == info.username:
            msg += f' and username \'{info.username}\''
        msg += ' already exists'
        return HttpResponse(status=400, reason=msg)


@csrf_exempt
def create_new_student(request):
    info = common_info_from_post_get_or_create(request)

    exist_response = make_response_if_exist(info, Student)
    if exist_response:
        return exist_response

    Student.objects.create(info=info)
    return HttpResponse(status=200)


@csrf_exempt
def create_new_teacher(request):
    info = common_info_from_post_get_or_create(request)

    exist_response = make_response_if_exist(info, Teacher)
    if exist_response:
        return exist_response

    occupation = request.POST['occupation'].lower().strip()
    Teacher.objects.create(info=info, occupation=occupation)
    return HttpResponse(status=200)


@csrf_exempt
def get_students(request):
    students = filter_user_from_get_by_name_email_phone(request, Student)
    students = apply_user_sorting(request, students, Student)
    students = paginate_query(request, students)
    data = StudentSerializer(students, many=True).data
    return JsonResponse(data=data, status=200, safe=False)


@csrf_exempt
def get_teachers(request):
    teachers = filter_user_from_get_by_name_email_phone(request, Teacher)
    teachers = apply_user_sorting(request, teachers, Teacher)
    teachers = paginate_query(request, teachers)
    data = TeacherSerializer(teachers, many=True).data
    return JsonResponse(data=data, status=200, safe=False)


@csrf_exempt
def get_admins(request):
    admin = filter_user_from_get_by_name_email_phone(request, Admin)
    admin = apply_user_sorting(request, admin, Admin)
    admin = paginate_query(request, admin)
    data = AdminSerializer(admin, many=True).data
    return JsonResponse(data=data, status=200, safe=False)


@csrf_exempt
def check_is_email_available(request):
    email = request.GET['email']
    exist = UserCommonInfo.objects.filter(email__exact=email).exists()
    return JsonResponse({'available': not exist}, status=200)


@csrf_exempt
def check_is_username_available(request):
    username = request.GET['username']
    exist = UserCommonInfo.objects.filter(username=username).exists()
    return JsonResponse({'available': not exist}, status=200)


@csrf_exempt
def get_occupations(request):
    occupations = set(t.occupation for t in Teacher.objects.all())
    return JsonResponse(list(occupations), safe=False, status=200)


@csrf_exempt
def create_new_admin(request):
    info = common_info_from_post_get_or_create(request)

    exist_response = make_response_if_exist(info, Admin)
    if exist_response:
        return exist_response

    Admin.objects.create(info=info)
    return HttpResponse(status=200)


@csrf_exempt
def update_student(request):
    info = UserCommonInfo.objects.filter(email__exact=request.POST['original_email']).first()
    update_info_from_post(request, info)
    return HttpResponse(status=200)


@csrf_exempt
def update_teacher(request):
    original_email = request.POST['original_email']
    info = UserCommonInfo.objects.filter(email__exact=original_email).first()
    update_info_from_post(request, info)
    teacher = Teacher.objects.get(info=info)
    teacher.occupation = request.POST['occupation']
    teacher.save()
    return HttpResponse(status=200)


@csrf_exempt
def update_admin(request):
    original_email = request.POST['original_email']
    info = UserCommonInfo.objects.filter(email__exact=original_email).first()
    update_info_from_post(request, info)
    return HttpResponse(status=200)


@csrf_exempt
def remove_student(request):
    email = request.POST['email']
    student = Student.objects.get(info__email__exact=email)
    student.delete()
    student.info.delete()
    return HttpResponse(status=200)


@csrf_exempt
def remove_teacher(request):
    email = request.POST['email']
    teacher = Teacher.objects.get(info__email__exact=email)
    teacher.delete()
    teacher.info.delete()
    return HttpResponse(status=200)


@csrf_exempt
def remove_admin(request):
    email = request.POST['email']
    admin = Admin.objects.get(info__email__exact=email)
    admin.delete()
    admin.info.delete()
    return HttpResponse(status=200)


@csrf_exempt
def login_as_admin(request):
    email_username = request.POST['email_username']
    password = request.POST['password']
    info = UserCommonInfo.objects.filter(Q(email=email_username) | Q(username=email_username))
    info = info.filter(password__exact=password)
    if not info.exists():
        return HttpResponse(status=401)

    info = info.first()
    query = Admin.objects.filter(info=info)

    if not query.exists():
        return HttpResponse(content='commoninfo exists but user not exist', status=500)

    serializer = AdminSerializer(query.get())

    return JsonResponse(data=serializer.data, status=200)
