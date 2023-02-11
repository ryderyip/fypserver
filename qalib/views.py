import json

from django.db.models import Q
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt

from factories.custom_methods import paginate_query
from qalib.models import *
from qalib.serializers import *


@csrf_exempt
def get_QALibQuestions(request):
    def get_serialized_jsonResponse(querySet):
        data = QALibQuestionSerializer(querySet, many=True).data
        return JsonResponse(data=data, status=200, safe=False)

    search_term = request.GET.get('search_term', None)
    question_id = request.GET.get('id', None)
    tags = request.GET.get('tags', None)
    tags = tags.split(' ') if tags else None

    qs = QALibQuestion.objects.all()

    if question_id:
        qs = qs.filter(id=question_id)
        return get_serialized_jsonResponse(qs)

    if search_term:
        qs = qs.filter(question__icontains=search_term)

    if tags:
        qs = qs.filter(tags__in=tags)

    qs = paginate_query(request=request, query=qs)

    return get_serialized_jsonResponse(qs)


@csrf_exempt
def create_QALibQuestion(request):
    no_of_blocks = int(request.POST['no_of_blocks'])

    content_block = ContentBlockContainer.objects.create()

    student = Student.objects.get(info__email__exact=request.POST['asking_student_email'])
    QALibQuestion.objects.create(question=request.POST['question'],
                                 question_details_block=content_block,
                                 asked_by=student)
    for i in range(1, no_of_blocks):
        block = request.POST.get(f'text_block_{i}')
        if block:
            TextBlock.objects.create(content_block=content_block, text=block, ordering=i)
            continue

        block = request.FILES.get(f'image_block_{i}')
        if block:
            ImageBlock.objects.create(content_block=content_block, image=block, ordering=i)
            continue

        return HttpResponse(content=f'xxxx_block_{i} not specified', status=400)
    return HttpResponse(status=200)


def get_serialized_content_blocks(container_id):
    q = ContentBlockCommonInfo.objects.all().order_by('ordering') \
        .filter(content_container_id=container_id)
    return [(ImageBlockSerializer(ImageBlock.objects.get(
        info=blockInfo)).data if blockInfo.type == ContentBlockCommonInfo.BlockType.IMAGE
             else TextBlockSerializer(TextBlock.objects.get(info=blockInfo)).data) for blockInfo in
            q]


@csrf_exempt
def get_QALibContentBlock(request):
    data = get_serialized_content_blocks(container_id=request.GET['content_container_id'])
    return JsonResponse(data=data, status=200, safe=False)


class ContentBlockUpdateOrCreator:
    def __init__(self, block_info: ContentBlockCommonInfo):
        self.block_info = block_info

    def uoc_text_block(self, text: str):
        if self.block_info.type == ContentBlockCommonInfo.BlockType.TEXT:
            tb = TextBlock.objects.update_or_create(info=self.block_info, defaults={'text': text})

    def uoc_image_block(self):
        print('uniomplemented')


def update_or_create_content_block(block_info: ContentBlockCommonInfo, json_block):
    # [{'info': {'type': 'txt', 'ordering': 1}, 'text': '(question)'}]
    updater = ContentBlockUpdateOrCreator(block_info)
    if block_info.type == ContentBlockCommonInfo.BlockType.TEXT:
        updater.uoc_text_block(json_block['text'])
    elif block_info.type == ContentBlockCommonInfo.BlockType.IMAGE:
        updater.uoc_image_block()
    else:
        print('unknown block type !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')


@csrf_exempt
def save_QALibContentBlock(request):
    data = json.loads(request.body)
    content_blocks = data['content_blocks']
    container_id = data['content_block_container_id']

    has_existing_container = container_id is not None \
        and isinstance(container_id, int) and ContentBlockContainer.objects.filter(id=container_id).exists()

    # get or create container
    if has_existing_container:
        container = ContentBlockContainer.objects.get(id=container_id)
    else:
        container = ContentBlockContainer.objects.create()

    # clear all first
    for block_info in container.blocks.all():
        block_info.delete()

    # update or create content blocks
    for json_block in content_blocks:
        json_block_info = json_block['info']
        block_info, is_created = ContentBlockCommonInfo.objects.update_or_create(
            ordering=json_block_info['ordering'],
            type=json_block_info['type'],
            content_container=container
        )
        update_or_create_content_block(block_info, json_block)

    return HttpResponse(status=200)


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
    data = json.loads(request.POST['data'])
    answer_id = data['answer_id']
    answered_by_id = data['answered_by_id']
    question_id = data['question_id']

    teacher = Teacher.objects.get(id=answered_by_id)

    if isinstance(answered_by_id, int) and QALibAnswer.objects.filter(id=answer_id).exists():  # update
        a = QALibAnswer.objects.get(id=answer_id)
        a.answered_by = teacher
        a.save()
    else:  # create
        QALibAnswer.objects.create(answered_by=teacher,
                                   question_id=question_id,
                                   info=QACommonInfo.objects.create(),
                                   answer_block=ContentBlockContainer.objects.create())

    return HttpResponse(status=200)