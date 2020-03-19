from rest_framework import serializers
from .models import (
    User,
    Role,
    Gender,
    SchoolSubject,
    SchoolClass,
    Grade,
    Event,
    Absence,
    SchoolClassStudent,
    SchoolClassProfessor,
    ClassRoomSchoolSubject
)


class RoleSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Role
        fields = [
            'id',
            'created',
            'name'
        ]


class GenderSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Gender
        fields = [
            'id',
            'created',
            'name'
        ]


class ParentSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = [
            'id',
            'created',
            'first_name',
            'last_name'
        ]


class UserSerializer(serializers.HyperlinkedModelSerializer):
    gender = GenderSerializer(many=False)
    role = RoleSerializer(many=False)
    parent_mother = ParentSerializer(many=False)
    parent_father = ParentSerializer(many=False)

    class Meta:
        model = User
        fields = [
            'id',
            'created',
            'first_login',
            'last_login',
            'first_name',
            'last_name',
            'email',
            'address',
            'city',
            'phone',
            'is_active',
            'birth_date',
            'gender',
            'role',
            'parent_mother',
            'parent_father'
        ]


class SchoolSubjectSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = SchoolSubject
        fields = [
            'id',
            'created',
            'is_active',
            'name'
        ]


class SchoolClassSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = SchoolClass
        fields = [
            'id',
            'created',
            'school_year',
            'is_active',
            'name'
        ]


class GradeSerializer(serializers.HyperlinkedModelSerializer):
    professor = UserSerializer(many=False)
    student = UserSerializer(many=False)
    school_subject = SchoolSubjectSerializer(many=False)
    school_class = SchoolClassSerializer(many=False)

    class Meta:
        model = Grade
        fields = [
            'id',
            'created',
            'grade',
            'grade_type',
            'comment',
            'professor',
            'student',
            'school_subject',
            'school_class'
        ]


class EventSerializer(serializers.HyperlinkedModelSerializer):
    professor = UserSerializer(many=False)
    school_subject = SchoolSubjectSerializer(many=False)
    school_class = SchoolClassSerializer(many=False)

    class Meta:
        model = Event
        fields = [
            'id',
            'created',
            'title',
            'comment',
            'date',
            'professor',
            'school_subject',
            'school_class'
        ]


class AbsenceSerializer(serializers.HyperlinkedModelSerializer):
    professor = UserSerializer(many=False)
    student = UserSerializer(many=False)
    school_subject = SchoolSubjectSerializer(many=False)
    school_class = SchoolClassSerializer(many=False)

    class Meta:
        model = Absence
        fields = [
            'id',
            'created',
            'title',
            'comment',
            'is_justified',
            'professor',
            'student',
            'school_subject',
            'school_class'
        ]


class SchoolCLassProfessorsSerializer(serializers.HyperlinkedModelSerializer):
    professor = UserSerializer(many=False)
    school_class = SchoolClassSerializer(many=False)

    class Meta:
        model = SchoolClassProfessor
        fields = [
            'id',
            'created',
            'is_active',
            'professor',
            'school_class'
        ]


class SchoolCLassStudentsSerializer(serializers.HyperlinkedModelSerializer):
    student = UserSerializer(many=False)
    school_class = SchoolClassSerializer(many=False)

    class Meta:
        model = SchoolClassStudent
        fields = [
            'id',
            'created',
            'is_active',
            'student',
            'school_class'
        ]


class SchoolClassSubjectsSerializer(serializers.HyperlinkedModelSerializer):
    professor = UserSerializer(many=False)
    school_subject = SchoolSubjectSerializer(many=False)
    school_class = SchoolClassSerializer(many=False)

    class Meta:
        model = ClassRoomSchoolSubject
        fields = [
            'id',
            'created',
            'is_active',
            'professor',
            'school_subject',
            'school_class'
        ]
