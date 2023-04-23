import base64
import json
import os

import requests
from django.db.models import Q
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt

from factories.custom_methods import paginate_query
from learning_resources.models import *
from learning_resources.serializers import *
from qalib.serializers import *
from user.custom_serializers import StudentSerializer
from walter.content_block_create_update import ContentBlockUOCHandler
from walter.json_tag_extractor import JsonTagExtractor


@csrf_exempt
def get_nonexercise_learning_resource(request):
    lr = NonExerciseLearningResource.objects.all()
    id = request.GET.get('id')
    if id:
        lr = lr.filter(id=id)
    data = NonExerciseLearningResourceSerializer(lr, many=True).data
    return JsonResponse(data, safe=False, status=200)


@csrf_exempt
def get_exercise_learning_resource(request):
    lrs = ExerciseLearningResource.objects.all()
    id = request.GET.get('id')
    if id:
        lrs = lrs.filter(id=id)
    data = [ExerciseLearningResourceSerializer(lr).data for lr in lrs]
    return JsonResponse(data, safe=False, status=200)


@csrf_exempt
def create_nonexercise_lr(request):
    data = json.loads(request.POST['data'])
    info = LearningResourceCommonInfo.create_from_preEntity_json(data['info'])

    res = NonExerciseLearningResource.objects.create(
        info=info,
        content=ContentBlockContainer.objects.create(),
    )

    for non_exe_lr_id in data['related_non_exercise_lr_ids']:
        res.related.add(NonExerciseLearningResource.objects.get(id=non_exe_lr_id))

    ContentBlockUOCHandler.uoc(content_container=res.content, json=data['content_container'])

    LearningResource_CommonInfo_Map.objects.create(
        info=res.info,
        non_exercise=res
    )

    return JsonResponse(data=get_nonexercise_serialized(res.info.id))


def get_nonexercise_serialized(lr_commoninfo_id):
    lr = NonExerciseLearningResource.objects.get(learningresource_commoninfo_map__info_id=lr_commoninfo_id)
    return NonExerciseLearningResourceSerializer(lr).data


def get_exercise_serialized(lr_commoninfo_id):
    lr = ExerciseLearningResource.objects.get(learningresource_commoninfo_map__info_id=lr_commoninfo_id)
    return ExerciseLearningResourceSerializer(lr).data


@csrf_exempt
def get_learning_resource(request):
    q = LearningResource_CommonInfo_Map.objects.all()

    search = request.GET.get('search_term')
    if search:
        q = q.filter(info__name__icontains=search.strip())

    tag_filters = request.GET.get('tag_filters')
    if tag_filters:
        q = q.filter(info__tags__name__in=tag_filters.split('&'))

    hide_unpublished = request.GET.get('hide_unpublished')
    if hide_unpublished and hide_unpublished.lower() == 'true':
        q = q.filter(Q(exercise__published=True) | Q(exercise__isnull=True))

    q = q.distinct()

    things = []
    for resource in q:
        if resource.non_exercise:
            data = NonExerciseLearningResourceSerializer(resource.non_exercise).data
            data['type'] = 'nonexercise'
            things.append(data)
        elif resource.exercise:
            data = ExerciseLearningResourceSerializer(resource.exercise).data
            data['type'] = 'exercise'
            things.append(data)

    return JsonResponse(data=things, safe=False)


@csrf_exempt
def remove_nonexercise_lr(request):
    NonExerciseLearningResource.objects.get(id=request.POST['id']).delete()
    return HttpResponse(status=200)


@csrf_exempt
def update_nonexercise_lr(request):
    data = json.loads(request.POST['data'])

    res = NonExerciseLearningResource.objects.get(id=data['id'])
    res.info.update_from_preEntity_json(data['info'])

    res.related.clear()
    for non_exe_lr_id in data['related_non_exercise_lr_ids']:
        res.related.add(NonExerciseLearningResource.objects.get(id=non_exe_lr_id))

    res.save()
    ContentBlockUOCHandler.uoc(content_container=res.content, json=data['content_container'])

    res.save()
    return HttpResponse(status=200)


@csrf_exempt
def create_exercise_lr(request):
    data = json.loads(request.POST['data'])
    info = LearningResourceCommonInfo.create_from_preEntity_json(data['info'])

    qf_json = data['content']
    # create questions for corresponding types
    qf = QuizForm.objects.create(description=qf_json['description'])
    for q_json in qf_json['questions']:
        question_type = q_json['question_type']
        # assert question_type == 'text' or question_type == 'mc'
        # if question_type == 'text':
        #     q = QFTextQuestion.create_from_json(q_json)
        # else:
        #     q = QFMCQuestion.create_from_json(q_json)
        assert question_type == 'mc'
        q = QFMCQuestion.create_from_json(q_json)
        qf.question_infos.add(q.info)

    res = ExerciseLearningResource.objects.create(
        info=info,
        content=qf,
    )

    LearningResource_CommonInfo_Map.objects.create(
        info=res.info,
        exercise=res
    )

    return JsonResponse(get_exercise_serialized(res.info.id))


@csrf_exempt
def remove_exercise_lr(request):
    ExerciseLearningResource.objects.get(id=request.POST['id']).delete()
    return HttpResponse(status=200)


@csrf_exempt
def update_exercise_lr(request):
    data = json.loads(request.POST['data'])
    lr = ExerciseLearningResource.objects.get(id=data['id'])

    lr.info.update_from_preEntity_json(data['info'])
    lr.content.update_from_json(data['content'])

    lr.published = data['published']
    lr.save()

    lr.related.clear()
    for non_exe_lr_id in data['related_non_exercise_lr_ids']:
        lr.related.add(NonExerciseLearningResource.objects.get(id=non_exe_lr_id))

    return HttpResponse(status=200)


# @csrf_exempt
# def create_text_q(request):
#     data = json.loads(request.POST['data'])
#     q = QFTextQuestion.create_from_json(data)
#     return JsonResponse(data=QFTextQuestionSerializer(q).data, status=200)

# @csrf_exempt
# def update_text_q(request):
#     data = json.loads(request.POST['data'])
#     QFTextQuestion.objects.get(id=data['id']).update_from_json(data)
#     return HttpResponse(status=200)

@csrf_exempt
def remove_text_q(request):
    QFTextQuestion.objects.get(id=request.POST['id']).delete()
    return HttpResponse(status=200)


@csrf_exempt
def create_mc_q(request):
    data = json.loads(request.POST['data'])
    q = QFMCQuestion.create_from_json(data)
    return JsonResponse(data=QFMCQuestionSerializer(q).data, status=200)

@csrf_exempt
def update_mc_q(request):
    data = json.loads(request.POST['data'])
    print(data)
    QFMCQuestion.objects.get(id=data['id']).update_from_json(data)
    return HttpResponse(status=200)

@csrf_exempt
def remove_mc_q(request):
    q = QFMCQuestion.objects.get(id=request.POST['id'])
    q.info.delete()
    q.delete()
    return HttpResponse(status=200)


@csrf_exempt
def create_mc_q_res(request):
    data = json.loads(request.POST['data'])

    question_id = data['responding_question_id']
    print(data['response'])
    choice = QFMCQuestionOption.objects\
        .filter(belong_to_question_id=question_id)\
        .get(value__iexact=data['response']['value'])
    response = QFMCQuestionResponse.objects.create(
        responding_question_id=question_id,
        responder_id=data['responder_id'],
        choice=choice
    )
    data = QFMCQuestionResponseSerializer(response).data
    return JsonResponse(data=data, status=200)


@csrf_exempt
def get_mc_q_res(request):
    data = request.GET
    q = QFMCQuestionResponse.objects.all()
    if data.get('quiz_form_id'):
        q = q.filter(responding_question__info__quiz_form_id=data['quiz_form_id'])
    if data.get('student_id'):
        q = q.filter(responder_id=data['student_id'])
    data = QFMCQuestionResponseSerializer(q, many=True).data
    return JsonResponse(data=data, status=200, safe=False)

@csrf_exempt
def get_mc_q_attempted_students(request):
    data = request.GET
    quiz = QuizForm.objects.get(id=data['quiz_form_id'])
    q = Student.objects.filter(quizzes_done__in=quiz)
    data = StudentSerializer(q, many=True).data
    return JsonResponse(data=data, status=200, safe=False)


@csrf_exempt
def clear_exercise_lr(request):
    LearningResource_CommonInfo_Map.objects.filter(exercise__isnull=False).delete()
    return HttpResponse(status=200)


@csrf_exempt
def create_mcq_option(request):
    data = json.loads(request.POST['data'])

    o = QFMCQuestionOption.objects.create(
        value=data['value'],
        belong_to_question_id=data['belong_to_question_id']
    )
    data= QFMCQuestionOptionSerializer(o).data
    return JsonResponse(data=data, status=200)


@csrf_exempt
def update_mcq_option(request):
    data = json.loads(request.POST['data'])
    o = QFMCQuestionOption.objects.get(id=data['id'])
    o.value = data['value']
    o.save()
    return HttpResponse(status=200)


@csrf_exempt
def remove_mcq_option(request):
    QFMCQuestionOption.objects.get(id=request.POST['id']).remove()
    return HttpResponse(status=200)


