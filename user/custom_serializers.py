from rest_framework import serializers

from user.models import Student, Teacher, Admin


class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ['info']
        depth = 1


class TeacherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Teacher
        fields = [field.name for field in Teacher._meta.get_fields()]
        depth = 1


class AdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = Admin
        fields = [field.name for field in Admin._meta.get_fields()]
        depth = 1
