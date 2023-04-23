from django.contrib import admin

from qalib.models import *

admin.site.register(ContentBlockContainer)
admin.site.register(TextBlock)
admin.site.register(ImageBlock)
admin.site.register(LatexBlock)
admin.site.register(QALibQuestionView)
admin.site.register(QALibQuestion)
admin.site.register(ContentBlockCommonInfo)
admin.site.register(QACommonInfo)
admin.site.register(Tag)
admin.site.register(QALibAnswer)

