from cgitb import text
from typing import Mapping

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import *
from django.utils.translation import gettext_lazy as _

from qalib.models import ContentBlockContainer, Tag
from user.models import Student, UserCommonInfo, Teacher
from walter.json_tag_extractor import JsonTagExtractor


class QFLRPageMaterial(models.Model):
    lr_page = models.OneToOneField('NonExerciseLearningResource', on_delete=RESTRICT)

    @staticmethod
    def create_from_json(json: Mapping[str, any]):
        return QFLRPageMaterial.objects.create(lr_page_id=json['lrPageId'])

    def update_from_json(self, json: Mapping[str, any]):
        self.lr_page_id = json['lrPageId']
        self.save()


class QFVideoLinkMaterial(models.Model):
    youtube_uri = models.TextField()
    display_text = models.TextField()

    @staticmethod
    def create_from_json(json: Mapping[str, any]):
        return QFVideoLinkMaterial.objects.create(
            youtube_uri=json['youtubeUrl'],
            display_text=json['displayText']
        )

    def update_from_json(self, json: Mapping[str, any]):
        self.youtube_uri = json['youtubeUrl']
        self.display_text = json['displayText']


class QFFeedback(models.Model):
    text = models.TextField()
    lr_page_suggest = models.OneToOneField(QFLRPageMaterial, on_delete=RESTRICT, null=True)
    youtube_link_suggest = models.OneToOneField(QFVideoLinkMaterial, on_delete=RESTRICT, null=True)

    @staticmethod
    def create_from_json(json: Mapping[str, any]):
        f = QFFeedback.objects.create(text=json['text'])
        if json.get('lrPageSuggest'):
            f.lr_page_suggest = QFLRPageMaterial.create_from_json(json['lrPageSuggest'])
        if json.get('youtubeLinkSuggest'):
            f.youtube_link_suggest = QFVideoLinkMaterial.create_from_json(json['youtubeLinkSuggest'])
        return f

    def update_from_json(self, json: Mapping[str, any]):
        self.text = json['text']
        if json.get('lrPageSuggest'):
            self.lr_page_suggest.update_from_json(json['lrPageSuggest'])
        if json.get('youtubeLinkSuggest'):
            self.youtube_link_suggest.update_from_json(json['youtubeLinkSuggest'])
        self.save()


class QFGrading(models.Model):
    point_value = models.IntegerField()
    general_feedback = models.OneToOneField(QFFeedback, on_delete=RESTRICT)
    correct_answer = models.TextField()

    @staticmethod
    def create_from_json(json: Mapping[str, any]):
        g = QFGrading.objects.create(
            point_value=json['point_value'],
            general_feedback=QFFeedback.create_from_json(json['general_feedback']),
            correct_answer=json['correct_answer']
        )

        return g

    def update_from_json(self, json: Mapping[str, any]):
        self.point_value = json['point_value']
        self.general_feedback.update_from_json(json['general_feedback'])
        self.correct_answer = json['correct_answer']
        self.save()

# question start

class QFQuestionInfo(models.Model):
    title = models.CharField(max_length=255)
    grading = models.OneToOneField(QFGrading, on_delete=RESTRICT)
    quiz_form = models.ForeignKey('QuizForm', on_delete=RESTRICT, related_name='question_infos')

    @staticmethod
    def createFromJson(json: Mapping[str, any], ):
        return QFQuestionInfo.objects.create(
            title=json['title'],
            grading=QFGrading.create_from_json(json['grading']),
            quiz_form_id=json['quizFormId']
        )

    def update_from_json(self, json: Mapping[str, any]):
        self.title = json['title']
        self.grading.update_from_json(json['grading'])
        self.save()


class QFTextQuestion(models.Model):
    info = models.OneToOneField(QFQuestionInfo, on_delete=RESTRICT)

    @staticmethod
    def create_from_json(json: Mapping[str, any]):
        return QFTextQuestion.objects.create(
            info=QFQuestionInfo.createFromJson(json['info']),
        )

    def update_from_json(self, json: Mapping[str, any]):
        self.info.update_from_json(json['info'])
        self.save()


class QFMCQuestionOption(models.Model):
    value = models.CharField(max_length=255)
    belong_to_question = models.ForeignKey('QFMCQuestion', on_delete=CASCADE, related_name='options')

    @staticmethod
    def create_option_set_from_json(json: list[Mapping[str, any]], belongs_to_question):
        return [QFMCQuestionOption.create_from_json(j, belongs_to_question) for j in json]

    @staticmethod
    def create_from_json(json: Mapping[str, any], belongs_to_question):
        return QFMCQuestionOption.objects.create(
            value=json['value'],
            belong_to_question=belongs_to_question
        )


class QFMCQuestion(models.Model):
    class ChoiceType(models.TextChoices):
        RADIO = 'RADIO', _('Text')
        CHECKBOX = 'CHECKBOX', _('Text')

    info = models.OneToOneField(QFQuestionInfo, on_delete=CASCADE)
    type = models.CharField(max_length=255, choices=ChoiceType.choices, )
    shuffle = models.BooleanField()

    @staticmethod
    def create_from_json(json: Mapping[str, any]):
        q = QFMCQuestion.objects.create(
            info=QFQuestionInfo.createFromJson(json['info']),
            type=json['choice_type'],
            shuffle=json['shuffle'],
        )
        q.options.set(QFMCQuestionOption.create_option_set_from_json(json['options'], q))
        q.save()
        return q


    def update_from_json(self, json: Mapping[str, any]):
        print(self.ChoiceType.choices)
        assert json['choice_type'] in [choice[0] for choice in self.ChoiceType.choices]
        self.type = json['choice_type']
        self.info.update_from_json(json['info'])
        self.shuffle = json['shuffle']
        self.options.all().delete()
        for oj in json['options']:
            self.options.add(QFMCQuestionOption.create_from_json(oj, self))
        self.save()


# question end


class QuizForm(models.Model):
    description = models.TextField()

    def update_from_json(self, json: Mapping[str, any]):
        self.description = json['description']
        # for qj in json['questions']:
        #     question_type = qj['question_type']
        #     assert question_type == 'text' or question_type == 'mc'
        #     if question_type == 'text':
        #         self.question_infos.get(id=qj['id']).qftextquestion.update_from_json(qj)
        #     else:
        #         self.question_infos.get(id=qj['id']).qfmcquestion.update_from_json(qj)
        self.save()


class QFMCQuestionResponse(models.Model):
    responder = models.ForeignKey(Student, on_delete=RESTRICT, related_name='quizzes_done')
    responding_question = models.ForeignKey(QFMCQuestion, on_delete=RESTRICT, related_name='responses')
    choice = models.ForeignKey(QFMCQuestionOption, on_delete=RESTRICT, related_name='chosen_responses')

    class Meta:
        unique_together = ('responder', 'responding_question',)

# class QFTextQuestionResponse(models.Model):
#     responding_question_info = models.OneToOneField(QFQuestionInfo, on_delete=RESTRICT)
#     response = models.OneToOneField(ContentBlockContainer, on_delete=RESTRICT)
#     is_correct = models.BooleanField(default=False)


# quiz form end

class LearningResourceCommonInfo(models.Model):
    name = models.CharField(max_length=255)
    created_on = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(Teacher, on_delete=models.RESTRICT)
    tags = models.ManyToManyField(Tag, blank=True)

    @staticmethod
    def create_from_preEntity_json(json: Mapping[str, any]):
        teacher_id = json['created_by_id']
        assert Teacher.objects.filter(id=teacher_id).exists()

        res = LearningResourceCommonInfo.objects.create(
            name=json['name'],
            created_by_id=teacher_id,
        )

        tags = JsonTagExtractor.extract(json['tags'])
        for tag in tags:
            res.tags.add(tag)

        return res

    def update_from_preEntity_json(self, json: Mapping[str, any]):
        self.name = json['name']
        self.tags.set(JsonTagExtractor.extract(json['tags']))
        self.save()

class NonExerciseLearningResource(models.Model):
    info = models.OneToOneField(LearningResourceCommonInfo, on_delete=models.CASCADE)
    content = models.OneToOneField(ContentBlockContainer, on_delete=models.RESTRICT)
    related = models.ManyToManyField('NonExerciseLearningResource', related_name='+')

    def __str__(self):
        return f'Non-exercise \'{self.info.name}\''


class ExerciseLearningResource(models.Model):
    info = models.OneToOneField(LearningResourceCommonInfo, on_delete=models.CASCADE)
    content = models.OneToOneField(QuizForm, on_delete=models.RESTRICT)
    published = models.BooleanField(default=False)
    related = models.ManyToManyField('NonExerciseLearningResource', related_name='+')

    def __str__(self):
        return f'Exercise \'{self.info.name}\''


class LearningResource_CommonInfo_Map(models.Model):
    info = models.OneToOneField(LearningResourceCommonInfo, on_delete=models.CASCADE)
    non_exercise = models.OneToOneField(NonExerciseLearningResource, on_delete=models.CASCADE, null=True)
    exercise = models.OneToOneField(ExerciseLearningResource, on_delete=models.CASCADE, null=True)

    class Meta:
        constraints = [
            # number_of_info_rows_is_sum_of_rows_of_all_types_of_learning_resources
            CheckConstraint(
                check=Q(non_exercise__isnull=False) | Q(exercise__isnull=False),
                name='learningResource_info_correspondence'
            )
        ]
