from django.db import models


class UserCommonInfo(models.Model):
    name = models.CharField(max_length=255)
    gender = models.CharField(max_length=1)
    date_of_birth = models.DateField()
    phone = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=255, null=True, unique=True)
    password = models.CharField(max_length=255)

    class Meta:
        ordering = ["name"]


class Student(models.Model):
    info = models.OneToOneField(UserCommonInfo, on_delete=models.RESTRICT)

    class Meta:
        ordering = ["info__name"]


class Teacher(models.Model):
    info = models.OneToOneField(UserCommonInfo, on_delete=models.RESTRICT)
    occupation = models.CharField(max_length=255)

    class Meta:
        ordering = ["info__name"]


class Admin(models.Model):
    info = models.OneToOneField(UserCommonInfo, on_delete=models.RESTRICT)

    class Meta:
        ordering = ["info__name"]
