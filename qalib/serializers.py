from os import path

from rest_framework import serializers

from fypserver import settings
from qalib.models import *
from user.custom_serializers import TeacherSerializer


class QALibQuestionViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = QALibQuestionView
        fields = '__all__'
        depth = 0


class ContentBlockCommonInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContentBlockCommonInfo
        fields = ['id', 'type', 'ordering']
        depth = 0


class QALibQuestionSerializer(serializers.ModelSerializer):
    view_count = serializers.IntegerField(source='views.count', read_only=True)
    answer_count = serializers.IntegerField(source='answers.count', read_only=True)
    info = serializers.SerializerMethodField('get_info')

    # question_details = ContentBlockCommonInfoSerializer(source='question_details.blocks', many=True)

    def get_info(self, obj):
        return QACommonInfoSerializer(info=obj.info).to_dict()

    class Meta:
        model = QALibQuestion
        fields = [
            'id',
            'info',
            'question',
            'question_details_block',
            'view_count',
            'asked_on',
            'asked_by',
            'resolved',
            'visible',
            'tags',
            'answer_count',
        ]
        depth = 2


class TextBlockSerializer(serializers.ModelSerializer):
    class Meta:
        model = TextBlock
        fields = '__all__'
        depth = 1


class LatexBlockSerializer(serializers.ModelSerializer):
    class Meta:
        model = LatexBlock
        fields = '__all__'
        depth = 1


class ImageBlockSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageBlock
        fields = ['info', 'image_name']
        depth = 1


class QACommonInfoSerializer:
    def __init__(self, info: QACommonInfo):
        self.info = info

    def to_dict(self) -> dict:
        return {
            "upvote_count": self.info.upvotes.count(),
            "downvote_count": self.info.downvotes.count()
        }


class QALibAnswerSerializer(serializers.ModelSerializer):
    info = serializers.SerializerMethodField('get_info')
    answer_block_container_id = serializers.SerializerMethodField('get_answer_block_container_id')
    answer_id = serializers.SerializerMethodField('get_answer_id')
    question = serializers.SerializerMethodField('get_answer')

    def get_answer_id(self, obj):
        return obj.id

    def get_answer_block_container_id(self, obj):
        return obj.answer_block.id

    def get_info(self, obj):
        return QACommonInfoSerializer(info=obj.info).to_dict()

    def get_answer(self, obj: QALibAnswer):
        return QALibQuestionSerializer(obj.question).data

    class Meta:
        model = QALibAnswer
        fields = [
            'info',
            'answered_by',
            'answered_on',
            'answer_id',
            'answer_block_container_id',
            'question'
        ]
        # fix this and check using postman
        depth = 2


class TagSerializer:
    def to_dict(self, tags: list[Tag]):
        return [{'id': tag.id, 'name': tag.name} for tag in tags]
