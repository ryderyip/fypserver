import base64
import json
import os

from django.db.models import Q
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt

from factories.custom_methods import paginate_query
from qalib.serializers import *
from walter.content_block_create_update import ContentBlockUOCHandler
from walter.json_tag_extractor import JsonTagExtractor


@csrf_exempt
def get_QALibQuestions(request):
    def get_serialized_jsonResponse(querySet):
        data = QALibQuestionSerializer(querySet, many=True).data
        return JsonResponse(data=data, status=200, safe=False)

    search_term = request.GET.get('search_term', None)
    question_id = request.GET.get('id', None)
    hide_archived = str.lower(request.GET.get('hide_archived', 'false')) == 'true'
    show_resolved = str.lower(request.GET.get('show_resolved', 'false')) == 'true'
    asked_by_student_id = request.GET.get('asked_by_student_id', None)

    tags = request.GET.get('tag_filters', None)
    tags = tags.split('&') if tags else None

    qs = QALibQuestion.objects.all()

    if question_id:
        qs = qs.filter(id=question_id)
        return get_serialized_jsonResponse(qs)

    if search_term:
        qs = qs.filter(question__icontains=search_term)

    if tags:
        qs = qs.filter(tags__name__in=tags)

    if hide_archived:
        qs = qs.filter(visible=True)

    if not show_resolved:
        qs = qs.filter(resolved=False)

    if asked_by_student_id:
        qs = qs.filter(asked_by_id=asked_by_student_id)

    qs = paginate_query(request=request, query=qs)
    return get_serialized_jsonResponse(qs)


def get_serialized_content_blocks(container_id):
    container = ContentBlockContainer.objects.get(id=container_id)
    q = ContentBlockCommonInfo.objects.all().order_by('ordering').filter(content_container=container)
    return [(ImageBlockSerializer(ImageBlock.objects.get(info=blockInfo)).data if blockInfo.type == ContentBlockCommonInfo.BlockType.IMAGE
             else TextBlockSerializer(TextBlock.objects.get(info=blockInfo)).data if blockInfo.type == ContentBlockCommonInfo.BlockType.TEXT
    else LatexBlockSerializer(LatexBlock.objects.get(info=blockInfo)).data
             ) for blockInfo in q]


@csrf_exempt
def get_QALibContentBlock(request):
    data = get_serialized_content_blocks(container_id=request.GET['content_container_id'])
    return JsonResponse(data=data, status=200, safe=False)


@csrf_exempt
def get_QALibAnswers(request):
    question_id = request.GET['question_id']
    answers = QALibAnswer.objects.filter(question_id=question_id)

    data = []
    for answer in answers:
        serialized = QALibAnswerSerializer(answer).data
        serialized['answer'] = get_serialized_content_blocks(answer.answer_block.id)

        data.append(serialized)

    return JsonResponse(data, status=200, safe=False)


@csrf_exempt
def save_QALibAnswers(request):
    data = json.loads(request.body)
    answer_id = data['answer_id']
    answered_by_id = data['answered_by_id']
    question_id = data['question_id']

    teacher = Teacher.objects.get(id=answered_by_id)

    if QALibAnswer.objects.filter(id=answer_id).exists():  # update
        a = QALibAnswer.objects.get(id=answer_id)
        a.answered_by = teacher
        a.save()
    else:  # create
        a = QALibAnswer.objects.create(answered_by=teacher,
                                       question_id=question_id,
                                       info=QACommonInfo.objects.create(),
                                       answer_block=ContentBlockContainer.objects.create())

    ContentBlockUOCHandler.uoc(content_container=a.answer_block, json=data['answer_block_container'])
    a.save()
    return JsonResponse(data={'id': answer_id})


@csrf_exempt
def remove_QALibAnswer(request):
    QALibAnswer.objects.get(id=request.POST['answer_id']).delete()
    return HttpResponse(status=200)


@csrf_exempt
def save_QALibQuestion(request):
    data = json.loads(request.POST['data'])

    question_id = data['id']
    question_title = data['question']
    tag_jsons = data['tags']

    if question_id and QALibQuestion.objects.filter(id=question_id).exists():  # update
        question = QALibQuestion.objects.get(id=question_id)
        question.question = question_title
        question.resolved = data['resolved']
        question.visible = data['visible']
    else:
        question = QALibQuestion.objects.create(question=question_title,
                                                info=QACommonInfo.objects.create(),
                                                question_details_block=ContentBlockContainer.objects.create(),
                                                asked_by=Student.objects.get(id=data['asked_by_id']))

    tags = JsonTagExtractor.extract(tag_jsons)
    for tag in tags:
        question.tags.add(tag)

    question.save()
    ContentBlockUOCHandler.uoc(content_container=question.question_details_block, json=data['question_details_block'])
    question.save()

    return JsonResponse(data={'id': question.id}, status=200)


@csrf_exempt
def remove_QALibQuestion(request):
    q = QALibQuestion.objects.get(id=request.POST['id'])
    q.answers.all().delete()
    q.delete()
    return HttpResponse(status=200)


@csrf_exempt
def get_tags(request):
    q = Tag.objects.all()
    return JsonResponse(data=TagSerializer().to_dict(q), status=200, safe=False)


@csrf_exempt
def update_tag(request):
    data = json.loads(request.POST['data'])
    id = data['id']
    tag = Tag.objects.get(id=id)
    tag.name = data['name']
    tag.save()
    return HttpResponse(status=200)


@csrf_exempt
def create_tag(request):
    data = json.loads(request.POST['data'])
    name = data['name']

    if Tag.objects.filter(name__iexact=name).exists():
        return HttpResponse(status=400, content=f'Tag with name \'{name}\' already exists')

    tag = Tag.objects.create(name=name)
    data = {'id': tag.id, 'name': tag.name}
    return JsonResponse(data=data, status=200)


@csrf_exempt
def upload_image(request):
    image_bytes = base64.b64decode(request.POST['image'])

    folder = 'storage\QALib'

    name = str(len(os.listdir(folder)) + 1) + '.png'

    with open(os.path.join(folder, name), 'wb+') as destination:
        destination.write(image_bytes)

    return JsonResponse(data={'image_name': name})


@csrf_exempt
def rate_QALibQuestion(request):
    data = json.loads(request.POST['data'])

    rated_question = QALibQuestion.objects.get(id=data['rated_question_id'])
    rater_user_commoninfo = UserCommonInfo.objects.get(id=data['by_user_commoninfo_id'])
    rating_option = int(data['rating_option'])
    assert rating_option is 0 or 1 or -1

    if rating_option == 0:  # clear rating by rater
        rated_question.info.upvotes.filter(upvoters_info=rater_user_commoninfo).delete()
        rated_question.info.downvotes.filter(downvoters_info=rater_user_commoninfo).delete()
    if rating_option == 1:  # upvote or un-upvote
        q = rated_question.info.upvotes.filter(upvoters_info=rater_user_commoninfo)
        if q.exists():
            q.delete()
        else:
            rated_question.info.upvotes.add(rater_user_commoninfo)
    if rating_option == -1:  # downvote or un-downvote
        q = rated_question.info.downvotes.filter(downvoters_info=rater_user_commoninfo)
        if q.exists():
            q.delete()
        else:
            rated_question.info.downvotes.add(rater_user_commoninfo)

    return HttpResponse(status=200)
