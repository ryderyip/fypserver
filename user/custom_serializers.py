from rest_framework import serializers

from user.models import Student, Teacher, Admin


class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ['info', 'id']
        depth = 1


class TeacherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Teacher
        fields = '__all__'
        depth = 1


class AdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = Admin
        fields = '__all__'
        depth = 1
