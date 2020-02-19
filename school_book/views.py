from django.shortcuts import render

# Create your views here.

from django.http import HttpResponse

from school_book.models import (
    User,
    SchoolSubject,
    Grade,
    Event,
    Absence
)
from school_book.helper import (
    ok_response,
    error_handler
)
from school_book.serializers import (
    UserSerializer,
    ParentSerializer,
    SchoolSubjectSerializer,
    GradeSerializer,
    EventSerializer,
    AbsenceSerializer
)
from django.http.response import JsonResponse
import json
from rest_framework.decorators import api_view
import django


@api_view(['GET'])
def get_user_by_id(request, user_id):
    """
    This method will get user, depends on filters.
    :param request:
    :param user_id:
    :return: message, data
    """
    if 'Authorization' not in request.headers:
        return error_handler(error_status=401, message=f'Security token is missing!')
    security_token = request.headers['Authorization']
    decoded_security_token = User.check_security_token(security_token=security_token)
    requester_user = User.get_user_by_email(email=decoded_security_token['email'])
    if not requester_user:
        return error_handler(error_status=404, message=f'Not found!')
    try:
        int(user_id)
    except ValueError as ex:
        print(ex)
        return error_handler(error_status=404, message=f'Not found!')
    user = User.get_user_by_id(user_id=user_id, requester=requester_user.role.name, parent_id=requester_user.id)
    if not user:
        return error_handler(error_status=404, message=f'Not found!')
    if decoded_security_token['role'] != 'Administrator':
        if decoded_security_token['role'] == 'Professor' or decoded_security_token['role'] == 'Parent':
            if requester_user.security_token() != security_token:
                return error_handler(error_status=403, message='Forbidden permission!')
        else:
            return error_handler(error_status=403, message='Forbidden permission!')
    user = UserSerializer(many=False, instance=user).data
    user = dict(user)
    user['role'] = dict(user['role'])
    user['gender'] = dict(user['gender'])
    user['parent_mother'] = dict(user['parent_mother']) if dict(user['parent_mother']) else {}
    user['parent_father'] = dict(user['parent_father']) if dict(user['parent_father']) else {}
    return ok_response('User', additional_data=user)


@api_view(['GET'])
def get_users(request):
    """
    This method will get users, depends on filters.
    :param request:
    :param query_string:
    :return: message, data
    """
    if 'Authorization' not in request.headers:
        return error_handler(error_status=401, message=f'Security token is missing!')
    security_token = request.headers['Authorization']
    decoded_security_token = User.check_security_token(security_token=security_token)
    user = User.get_user_by_email(email=decoded_security_token['email'])
    if not user:
        return error_handler(error_status=404, message=f'Not found!')
    if decoded_security_token['role'] != 'Administrator':
        if decoded_security_token['role'] == 'Professor':
            if user.security_token() != security_token:
                return error_handler(error_status=403, message='Forbidden permission!')
        else:
            return error_handler(error_status=403, message='Forbidden permission!')
    query_string = request.GET
    users = User.get_all_users(data=query_string, requester=user.role.name)
    users = UserSerializer(many=True, instance=users).data
    users_json = []
    if not users:
        return error_handler(error_status=404, message=f'Not found!')
    for u in users:
        u = dict(u)
        u['role'] = dict(u['role'])
        u['gender'] = dict(u['gender'])
        u['parent_mother'] = dict(u['parent_mother']) if u['parent_mother'] else {}
        u['parent_father'] = dict(u['parent_father']) if u['parent_father'] else {}
        users_json.append(u)
    return ok_response('Users', additional_data=users_json)


@api_view(['DELETE'])
def delete_user(request, user_id):
    """
    This method will set is_delete flag to True. This method will never delete user from database
    :param request:
    :param user_id:
    :return: message
    """
    if 'Authorization' not in request.headers:
        return error_handler(error_status=401, message=f'Security token is missing!')
    security_token = request.headers['Authorization']
    decoded_security_token = User.check_security_token(security_token=security_token)
    try:
        int(user_id)
    except ValueError as ex:
        print(ex)
        return error_handler(error_status=404, message=f'Not found!')
    user = User.objects.filter(id=user_id).first()
    if not user:
        return error_handler(error_status=404, message=f'Not found!')
    if decoded_security_token['role'] != 'Administrator':
        if user.security_token() != security_token:
            return error_handler(error_status=403, message='Forbidden permission!')
    user.delete()
    return ok_response('User is successfully deleted!')


@api_view(['PATCH'])
def activate_or_deactivate_user(request, user_id):
    """
    This method will set is_active flag to True or False, depends on last state.
    :param request:
    :param user_id:
    :param activate_flag:
    :body_param is_active:
    :return:
    """
    if 'Authorization' not in request.headers:
        return error_handler(error_status=401, message=f'Security token is missing!')
    security_token = request.headers['Authorization']
    decoded_security_token = User.check_security_token(security_token=security_token)
    requester_user = User.get_user_by_email(email=decoded_security_token['email'])
    if not requester_user:
        return error_handler(error_status=404, message=f'Not found!')
    body = request.data
    if 'is_active' not in body:
        return error_handler(error_status=400, message=f'Wrong data!')
    try:
        int(user_id)
    except ValueError as ex:
        print(ex)
        return error_handler(error_status=400, message=f'Wrong data!')
    user = User.objects.filter(id=user_id).first()
    if not user:
        return error_handler(error_status=404, message=f'Not found!')
    if decoded_security_token['role'] != 'Administrator':
        if user.security_token() != security_token:
            return error_handler(error_status=403, message='Forbidden permission!')
    if body['is_active']:
        if user.activate_user():
            return ok_response('User is successfully activated!')
        else:
            return error_handler(error_status=400, message='Something is wrong! User is not activated!')
    else:
        if user.deactivate_user(user_id=requester_user.id):
            return ok_response('User is successfully deactivated!')
        else:
            return error_handler(error_status=400, message='Something is wrong! User is not deactivated!')


@api_view(['PATCH'])
def activate_user(request):
    """
    This method will set is_active flag to True through login activation modal form
    :param request:
    :body_param email, code:
    :return:
    """
    body = request.data
    if 'email' not in body or 'code' not in body:
        return error_handler(error_status=400, message=f'Wrong data!')
    user = User.get_user_by_email(email=body['email'])
    if not user:
        return error_handler(error_status=404, message=f'Not found!')
    if user.activation_code != body['code']:
        return error_handler(error_status=403, message='An activation code is wrong')
    if django.utils.timezone.now() >= user.expired_activation_code:
        return error_handler(error_status=403, message='An activation code expired!')
    if user.activate_user():
        return ok_response('User is successfully activated!')
    else:
        return error_handler(error_status=400, message='Something is wrong! User is not activated!')


@api_view(['POST'])
def login_user(request):
    """
    Login method
    :param request:
    :return:
    """
    body = request.data
    if 'email' not in body and 'password' not in body:
        return error_handler(error_status=400, message=f'Wrong data!')
    user = User.get_user_by_email(email=body['email'])
    if not user:
        return error_handler(error_status=403, message=f'User or password is wrong!')
    if not User.check_user_login_password(user=user, password=body['password']):
        return error_handler(error_status=403, message=f'User or password is wrong!')
    if not user.is_active:
        return error_handler(error_status=403, message=f'User is deactivated!')
        # if not user.activation_code:
        #     return error_handler(error_status=403, message=f'User is deactivated!')
        # if not user.activate_user():
        #     return error_handler(error_status=403, message=f'User is deactivated!')
    security_token = user.security_token()
    user = UserSerializer(many=False, instance=user).data
    user = dict(user)
    user['role'] = dict(user['role'])
    user['gender'] = dict(user['gender'])
    user['token'] = security_token
    return ok_response(message='User is successfully logged!', additional_data=user)


@api_view(['GET'])
def get_children_by_parent_id(request):
    """
    This method will get all children by parent_id
    :param request:
    :return: list of children
    """
    if 'Authorization' not in request.headers:
        return error_handler(error_status=401, message=f'Security token is missing!')
    security_token = request.headers['Authorization']
    decoded_security_token = User.check_security_token(security_token=security_token)
    requester_user = User.get_user_by_email(email=decoded_security_token['email'])
    if decoded_security_token['role'] != 'Parent':
        return error_handler(error_status=403, message='Forbidden permission!')
    if not requester_user:
        return error_handler(error_status=404, message=f'Not found!')
    user = User.objects.filter(id=requester_user.id).first()
    if not user:
        return error_handler(error_status=404, message=f'Not found!')
    children = user.get_children_by_parent_id()
    children = UserSerializer(many=True, instance=children).data
    for child in children:
        child = dict(child)
        child['role'] = dict(child['role'])
        child['gender'] = dict(child['gender'])
    return ok_response(message='Children', additional_data=children)


@api_view(['GET'])
def get_all_school_subjects(request):
    """
    This method will get all school subjects
    :param request:
    :return: list of school subjects
    """
    if 'Authorization' not in request.headers:
        return error_handler(error_status=401, message=f'Security token is missing!')
    security_token = request.headers['Authorization']
    decoded_security_token = User.check_security_token(security_token=security_token)
    requester_user = User.get_user_by_email(email=decoded_security_token['email'])
    if decoded_security_token['role'] not in ['Parent', 'Professor', 'Admin']:
        return error_handler(error_status=403, message='Forbidden permission!')
    if not requester_user:
        return error_handler(error_status=404, message=f'Not found!')
    user = User.objects.filter(id=requester_user.id).first()
    if not user:
        return error_handler(error_status=404, message=f'Not found!')
    school_subjects = SchoolSubject.get_all_school_subjects()
    school_subjects = SchoolSubjectSerializer(many=True, instance=school_subjects).data
    for school_subject in school_subjects:
        school_subject = dict(school_subject)
    return ok_response(message='Children', additional_data=school_subjects)


@api_view(['GET'])
def get_all_student_grades(request, user_id, school_subject_id):
    """
    This method will get all student grades
    :param request:
    :param user_id:
    :param school_subject_id:
    :return: list of grades
    """
    if 'Authorization' not in request.headers:
        return error_handler(error_status=401, message=f'Security token is missing!')
    security_token = request.headers['Authorization']
    decoded_security_token = User.check_security_token(security_token=security_token)
    requester_user = User.get_user_by_email(email=decoded_security_token['email'])
    if decoded_security_token['role'] not in ['Parent', 'Professor', 'Admin']:
        return error_handler(error_status=403, message='Forbidden permission!')
    if not requester_user:
        return error_handler(error_status=404, message=f'Not found!')
    user = User.objects.filter(id=requester_user.id).first()
    if not user:
        return error_handler(error_status=404, message=f'Not found!')
    grades = Grade.get_all_grades_by_student_id_or_school_subject_id(user_id, school_subject_id)
    grades = GradeSerializer(many=True, instance=grades).data
    for grade in grades:
        grade = dict(grade)
        grade['professor'] = dict(grade['professor'])
        grade['professor']['role'] = dict(grade['professor']['role'])
        grade['professor']['gender'] = dict(grade['professor']['gender'])
        grade['student'] = dict(grade['student'])
        grade['student']['role'] = dict(grade['student']['role'])
        grade['student']['gender'] = dict(grade['student']['gender'])
        grade['school_subject'] = dict(grade['school_subject'])
        grade['school_class'] = dict(grade['school_class'])
    return ok_response(message='Grades', additional_data=grades)


@api_view(['GET'])
def get_all_events_by_parent_id(request):
    """
    This method will get all events by parent_id
    :param request:
    :return: list of events
    """
    if 'Authorization' not in request.headers:
        return error_handler(error_status=401, message=f'Security token is missing!')
    security_token = request.headers['Authorization']
    decoded_security_token = User.check_security_token(security_token=security_token)
    requester_user = User.get_user_by_email(email=decoded_security_token['email'])
    if decoded_security_token['role'] not in ['Parent', 'Professor', 'Admin']:
        return error_handler(error_status=403, message='Forbidden permission!')
    if not requester_user:
        return error_handler(error_status=404, message=f'Not found!')
    user = User.objects.filter(id=requester_user.id).first()
    if not user:
        return error_handler(error_status=404, message=f'Not found!')
    events = Event.get_all_events_by_parent_id(parent_id=user.id)
    events = EventSerializer(many=True, instance=events).data
    for event in events:
        event = dict(event)
        event['professor'] = dict(event['professor'])
        event['professor']['role'] = dict(event['professor']['role'])
        event['professor']['gender'] = dict(event['professor']['gender'])
        event['school_subject'] = dict(event['school_subject'])
        event['school_class'] = dict(event['school_class'])
    return ok_response(message='Grades', additional_data=events)


@api_view(['GET'])
def get_all_student_absences(request, user_id, school_subject_id, is_justified):
    """
    This method will get all student absences
    :param request:
    :param user_id:
    :param school_subject_id:
    :param is_justified:
    :return: list of absences
    """
    if 'Authorization' not in request.headers:
        return error_handler(error_status=401, message=f'Security token is missing!')
    security_token = request.headers['Authorization']
    decoded_security_token = User.check_security_token(security_token=security_token)
    requester_user = User.get_user_by_email(email=decoded_security_token['email'])
    if decoded_security_token['role'] not in ['Parent', 'Professor', 'Admin']:
        return error_handler(error_status=403, message='Forbidden permission!')
    if not requester_user:
        return error_handler(error_status=404, message=f'Not found!')
    user = User.objects.filter(id=requester_user.id).first()
    if not user:
        return error_handler(error_status=404, message=f'Not found!')
    absences = Absence.get_all_absences(
        student_id=user_id,
        school_subject_id=school_subject_id,
        is_justified=is_justified
    )
    justified_absences, unjustified_absences = Absence.count_all_absences_by_justified(
        student_id=user_id,
        school_subject_id=school_subject_id
    )
    absences = AbsenceSerializer(many=True, instance=absences).data
    for absence in absences:
        absence = dict(absence)
        absence['justified_absences'] = justified_absences
        absence['unjustified_absences'] = unjustified_absences
        absence['professor'] = dict(absence['professor'])
        absence['professor']['role'] = dict(absence['professor']['role'])
        absence['professor']['gender'] = dict(absence['professor']['gender'])
        absence['student'] = dict(absence['student'])
        absence['student']['role'] = dict(absence['student']['role'])
        absence['student']['gender'] = dict(absence['student']['gender'])
        absence['school_subject'] = dict(absence['school_subject'])
        absence['school_class'] = dict(absence['school_class'])
    return ok_response(message='Absences', additional_data=absences)


@api_view(['GET'])
def get_all_student_absences_number(request, user_id, school_subject_id):
    """
    This method will count all student absences
    :param request:
    :param user_id:
    :param school_subject_id:
    :return: number of justified and unjustified absences
    """
    if 'Authorization' not in request.headers:
        return error_handler(error_status=401, message=f'Security token is missing!')
    security_token = request.headers['Authorization']
    decoded_security_token = User.check_security_token(security_token=security_token)
    requester_user = User.get_user_by_email(email=decoded_security_token['email'])
    if decoded_security_token['role'] not in ['Parent', 'Professor', 'Admin']:
        return error_handler(error_status=403, message='Forbidden permission!')
    if not requester_user:
        return error_handler(error_status=404, message=f'Not found!')
    user = User.objects.filter(id=requester_user.id).first()
    if not user:
        return error_handler(error_status=404, message=f'Not found!')
    justified_absences, unjustified_absences = Absence.count_all_absences_by_justified(
        student_id=user_id,
        school_subject_id=school_subject_id
    )
    absences = {}
    absences['justified_absences'] = justified_absences
    absences['unjustified_absences'] = unjustified_absences
    return ok_response(message='Absences', additional_data=absences)
