import json
from abc import ABC
from os import path

from rest_framework import serializers

from fypserver import settings
from learning_resources.models import *
from qalib.models import *


class LearningResourceCommonInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = LearningResourceCommonInfo
        fields = '__all__'
        depth = 5


class RecursiveField(serializers.Serializer):
    def to_representation(self, value):
        serializer = self.parent.parent.__class__(value, context=self.context)
        return serializer.data


class NonExerciseLearningResourceSerializer(serializers.ModelSerializer):
    related = RecursiveField(many=True)

    class Meta:
        model = NonExerciseLearningResource
        fields = ['id', 'info', 'content', 'related']
        depth = 3


class QFGradingSerializer(serializers.ModelSerializer):
    class Meta:
        model = QFGrading
        fields = '__all__'
        depth = 5


class QFQuestionInfoSerializer(serializers.ModelSerializer):
    grading = QFGradingSerializer()

    class Meta:
        model = QFQuestionInfo
        fields = '__all__'
        depth = 5


# class QFTextQuestionSerializer(serializers.ModelSerializer):
#     info = QFQuestionInfoSerializer()
#
#     class Meta:
#         model = QFTextQuestion
#         fields = '__all__'
#         depth = 5

class QFMCQuestionOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = QFMCQuestionOption
        fields = '__all__'
        depth = 5


class QFMCQuestionSerializer(serializers.ModelSerializer):
    info = QFQuestionInfoSerializer()
    options = QFMCQuestionOptionSerializer(many=True)

    class Meta:
        model = QFMCQuestion
        fields = ['id', 'info', 'type', 'shuffle', 'options']
        depth = 5


class QuizFormSerializer(serializers.ModelSerializer):
    questions = serializers.SerializerMethodField('get')

    def get(self, obj: QuizForm):
        return [
            QFMCQuestionSerializer(QFMCQuestion.objects.get(info=qinfo)).data for
            qinfo in obj.question_infos.all()]

    class Meta:
        model = QuizForm
        fields = ['id', 'description', 'questions']
        depth = 10


class ExerciseLearningResourceSerializer(serializers.ModelSerializer):
    content = QuizFormSerializer()
    related = NonExerciseLearningResourceSerializer(many=True)

    class Meta:
        model = ExerciseLearningResource
        fields = ['id', 'info', 'content', 'published', 'related']
        depth = 10


class QFMCQuestionResponseSerializer(serializers.ModelSerializer):
    responding_question = QFMCQuestionSerializer()

    class Meta:
        model = QFMCQuestionResponse
        fields = '__all__'
        depth = 10

# class QALibQuestionSerializer(serializers.ModelSerializer):
#     view_count = serializers.IntegerField(source='views.count', read_only=True)
#     answer_count = serializers.IntegerField(source='answers.count', read_only=True)
#
#     # question_details = ContentBlockCommonInfoSerializer(source='question_details.blocks', many=True)
#
#     info = serializers.SerializerMethodField('get_info')
#     def get_info(self, obj):
#         return QACommonInfoSerializer(info=obj.info).to_dict()
#
#     class Meta:
#         model = QALibQuestion
#         fields = [
#             'id',
#             'info',
#             'question',
#             'question_details_block',
#             'view_count',
#             'asked_on',
#             'asked_by',
#             'resolved',
#             'visible',
#             'tags',
#             'answer_count',
#         ]
#         depth = 2
#
