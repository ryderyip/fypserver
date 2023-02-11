from django.db import models
from django.utils.translation import gettext_lazy as _
from user.models import Student, UserCommonInfo, Teacher


class ContentBlockContainer(models.Model):
    pass


class ContentBlockCommonInfo(models.Model):
    class BlockType(models.TextChoices):
        TEXT = 'txt', _('Text')
        IMAGE = 'img', _('Image')

    content_container = models.ForeignKey(ContentBlockContainer, on_delete=models.RESTRICT,
                                          related_name="blocks")
    type = models.CharField(max_length=3, choices=BlockType.choices, )
    ordering = models.IntegerField()

    class Meta:
        unique_together = ('content_container', 'ordering')


class TextBlock(models.Model):
    info = models.OneToOneField(ContentBlockCommonInfo, on_delete=models.CASCADE)
    text = models.TextField()


class ImageBlock(models.Model):
    info = models.OneToOneField(ContentBlockCommonInfo, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='QALib')


class QACommonInfo(models.Model):
    upvotes = models.ManyToManyField(UserCommonInfo, blank=True, related_name='upvotes', default=0)
    downvotes = models.ManyToManyField(UserCommonInfo, blank=True, related_name='downvotes', default=0)


class Tag(models.Model):
    name = models.CharField(max_length=50)


class QALibQuestion(models.Model):
    info = models.OneToOneField(QACommonInfo, on_delete=models.RESTRICT)
    question = models.CharField(max_length=255)
    question_details_block = models.OneToOneField(ContentBlockContainer, on_delete=models.RESTRICT)
    asked_on = models.DateTimeField(auto_now_add=True)
    asked_by = models.OneToOneField(Student, on_delete=models.RESTRICT)
    resolved = models.BooleanField(default=False)
    visible = models.BooleanField(default=True)
    tags = models.ManyToManyField(Tag, blank=True)


class QALibQuestionView(models.Model):
    viewed_question = models.ForeignKey(QALibQuestion, on_delete=models.RESTRICT,
                                        related_name='views')
    viewed_by = models.OneToOneField(UserCommonInfo, on_delete=models.RESTRICT)
    viewed_on = models.DateTimeField(auto_now_add=True)


class QALibAnswer(models.Model):
    info = models.OneToOneField(QACommonInfo, on_delete=models.RESTRICT)
    question = models.ForeignKey(QALibQuestion, on_delete=models.RESTRICT, related_name='answers')
    answer_block = models.OneToOneField(ContentBlockContainer, on_delete=models.RESTRICT)
    answered_by = models.ForeignKey(Teacher, related_name='answered_questions', on_delete=models.RESTRICT)
    answered_on = models.DateTimeField(auto_now_add=True)
