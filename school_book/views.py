import json
import django
from rest_framework.decorators import api_view
from django.http import HttpResponse
from .models import (
    User,
    SchoolSubject,
    Grade,
    Event,
    Absence,
    Role,
    Gender,
    SchoolClass,
    SchoolClassProfessor,
    SchoolClassStudent,
    ClassRoomSchoolSubject
)
from .helper import (
    ok_response,
    error_handler,
    check_valid_limit_and_offset,
    authorization,
)
from .validators import Validation
from .serializers import (
    UserSerializer,
    ParentSerializer,
    SchoolSubjectSerializer,
    GradeSerializer,
    EventSerializer,
    AbsenceSerializer,
    RoleSerializer,
    GenderSerializer,
    SchoolClassSerializer,
    SchoolCLassProfessorsSerializer,
    SchoolCLassStudentsSerializer,
    SchoolClassSubjectsSerializer
)


@api_view(['GET'])
@authorization
def get_user_by_id(request, user_id):
    """
    This method will get a user by user id
    :param request:
    :param user_id:
    :return: message, data
    """
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
    return HttpResponse(
                json.dumps(
                    {
                        'status': f'OK',
                        'code': 200,
                        'server_time': django.utils.timezone.now().strftime("%Y-%m-%dT%H:%M:%S"),
                        'message': f'User',
                        'result': user
                    }
                ),
                content_type='application/json',
                status=200
            )


@api_view(['GET'])
@authorization
def get_users(request):
    """
    This method will get all the users, depends on the filters.
    :param request:
    :param query_string:
    :return: message, data
    """
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
    # if not users:
    #     return error_handler(error_status=404, message=f'Not found!')
    users_number = User.count_all_users(data=query_string, requester=user.role.name)
    for u in users:
        u['users_number'] = users_number
        u = dict(u)
        u['role'] = dict(u['role'])
        u['gender'] = dict(u['gender'])
        u['parent_mother'] = dict(u['parent_mother']) if u['parent_mother'] else {}
        u['parent_father'] = dict(u['parent_father']) if u['parent_father'] else {}
        users_json.append(u)
    return HttpResponse(
                json.dumps(
                    {
                        'status': f'OK',
                        'code': 200,
                        'server_time': django.utils.timezone.now().strftime("%Y-%m-%dT%H:%M:%S"),
                        'message': f'Users',
                        'results': users_json
                    }
                ),
                content_type='application/json',
                status=200
            )


@api_view(['DELETE'])
@authorization
def delete_user(request, user_id):
    """
    This method will delete the user by user_id
    :param request:
    :param user_id:
    :return: message
    """
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
    return HttpResponse(
                json.dumps(
                    {
                        'status': f'OK',
                        'code': 200,
                        'server_time': django.utils.timezone.now().strftime("%Y-%m-%dT%H:%M:%S"),
                        'message': f'User is successfully deleted!',
                    }
                ),
                content_type='application/json',
                status=200
            )


@api_view(['PATCH'])
@authorization
def activate_or_deactivate_user(request, user_id):
    """
    This method will set is_active flag to True or False, depends on the last state.
    :param request:
    :param user_id:
    :param activate_flag:
    :body_param is_active:
    :return:
    """
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
            return HttpResponse(
                json.dumps(
                    {
                        'status': f'OK',
                        'code': 200,
                        'server_time': django.utils.timezone.now().strftime("%Y-%m-%dT%H:%M:%S"),
                        'message': f'User is successfully activated!',
                    }
                ),
                content_type='application/json',
                status=200
            )
        else:
            return error_handler(error_status=400, message='Something is wrong! User is not activated!')
    else:
        if user.deactivate_user():
            return HttpResponse(
                json.dumps(
                    {
                        'status': f'OK',
                        'code': 200,
                        'server_time': django.utils.timezone.now().strftime("%Y-%m-%dT%H:%M:%S"),
                        'message': f'User is successfully deactivated!',
                    }
                ),
                content_type='application/json',
                status=200
            )
        else:
            return error_handler(error_status=400, message='Something is wrong! User is not deactivated!')


@api_view(['PATCH'])
def activate_user(request):
    """
    This method will set is_active flag to True through the login activation modal form
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
        return HttpResponse(
            json.dumps(
                {
                    'status': f'OK',
                    'code': 200,
                    'server_time': django.utils.timezone.now().strftime("%Y-%m-%dT%H:%M:%S"),
                    'message': f'User is successfully activated!',
                }
            ),
            content_type='application/json',
            status=200
        )
    else:
        return error_handler(error_status=400, message='Something is wrong! User is not activated!')


@api_view(['POST'])
def login_user(request):
    """
    Login method
    :param request:
    :param_body: email, password
    :return: user data
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
    return HttpResponse(
        json.dumps(
            {
                'status': f'OK',
                'code': 200,
                'server_time': django.utils.timezone.now().strftime("%Y-%m-%dT%H:%M:%S"),
                'message': f'User is successfully logged!',
                'result': user
            }
        ),
        content_type='application/json',
        status=200
    )


@api_view(['GET'])
@authorization
def get_children_by_parent_id(request):
    """
    This method will get all children by parent_id
    :param request:
    :return: list of children
    """
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
    return HttpResponse(
        json.dumps(
            {
                'status': f'OK',
                'code': 200,
                'server_time': django.utils.timezone.now().strftime("%Y-%m-%dT%H:%M:%S"),
                'message': f'Children',
                'results': children
            }
        ),
        content_type='application/json',
        status=200
    )


@api_view(['GET'])
@authorization
def get_all_school_subjects(request):
    """
    This method will get all school subjects
    :param request:
    :return: list of school subjects
    """
    security_token = request.headers['Authorization']
    decoded_security_token = User.check_security_token(security_token=security_token)
    requester_user = User.get_user_by_email(email=decoded_security_token['email'])
    if decoded_security_token['role'] not in ['Parent', 'Professor', 'Administrator']:
        return error_handler(error_status=403, message='Forbidden permission!')
    if not requester_user:
        return error_handler(error_status=404, message=f'Not found!')
    user = User.objects.filter(id=requester_user.id).first()
    if not user:
        return error_handler(error_status=404, message=f'Not found!')
    query_string = request.GET
    limit = query_string['limit'] if 'limit' in query_string else None
    offset = query_string['offset'] if 'offset' in query_string else None
    limit, offset = check_valid_limit_and_offset(limit=limit, offset=offset)
    school_subjects = SchoolSubject.get_all_school_subjects(limit=limit, offset=offset)
    school_subjects = SchoolSubjectSerializer(many=True, instance=school_subjects).data
    school_subjects_number = SchoolSubject.count_school_subject()
    for school_subject in school_subjects:
        school_subject['school_subjects_number'] = school_subjects_number
        school_subject = dict(school_subject)
    return HttpResponse(
        json.dumps(
            {
                'status': f'OK',
                'code': 200,
                'server_time': django.utils.timezone.now().strftime("%Y-%m-%dT%H:%M:%S"),
                'message': f'School subjects',
                'results': school_subjects
            }
        ),
        content_type='application/json',
        status=200
    )


@api_view(['POST'])
@authorization
def add_school_subject(request):
    """
    This method will add a new school subject
    :param request:
    :param_body: name, is_active
    :return: message
    """
    body = request.data
    if not Validation.add_school_subject_validation(data=body):
        return error_handler(error_status=400, message=f'Wrong data!')
    security_token = request.headers['Authorization']
    decoded_security_token = User.check_security_token(security_token=security_token)
    requester_user = User.get_user_by_email(email=decoded_security_token['email'])
    if decoded_security_token['role'] != 'Administrator':
        return error_handler(error_status=403, message='Forbidden permission!')
    if not requester_user:
        return error_handler(error_status=404, message=f'Not found!')
    if not SchoolSubject.add_new_school_subject(data=body):
        return error_handler(error_status=403, message='School subject is not added!')
    return HttpResponse(
        json.dumps(
            {
                'status': f'OK',
                'code': 201,
                'server_time': django.utils.timezone.now().strftime("%Y-%m-%dT%H:%M:%S"),
                'message': f'School subject is successfully added!',
            }
        ),
        content_type='application/json',
        status=201
    )


@api_view(['PUT'])
@authorization
def edit_school_subject(request, school_subject_id):
    """
    This method will edit an old school subject
    :param request:
    :param school_subject_id:
    :param_body: name, is_active
    :return: message
    """
    body = request.data
    if not Validation.edit_school_subject_validation(data=body):
        return error_handler(error_status=400, message=f'Wrong data!')
    security_token = request.headers['Authorization']
    decoded_security_token = User.check_security_token(security_token=security_token)
    requester_user = User.get_user_by_email(email=decoded_security_token['email'])
    if decoded_security_token['role'] != 'Administrator':
        return error_handler(error_status=403, message='Forbidden permission!')
    if not requester_user:
        return error_handler(error_status=404, message=f'Not found!')
    school_subject = SchoolSubject.get_school_subject_by_id(school_subject_id=school_subject_id)
    if not school_subject:
        return error_handler(error_status=404, message=f'Not found!')
    if not school_subject.edit_school_subject(data=body):
        return error_handler(error_status=403, message='School subject is not edited!')
    return HttpResponse(
        json.dumps(
            {
                'status': f'OK',
                'code': 200,
                'server_time': django.utils.timezone.now().strftime("%Y-%m-%dT%H:%M:%S"),
                'message': f'School subject is successfully edited!',
            }
        ),
        content_type='application/json',
        status=200
    )


@api_view(['DELETE'])
@authorization
def delete_school_subject(request, school_subject_id):
    """
    This method will delete an old school subject
    :param request:
    :param school_subject_id:
    :return: message
    """
    security_token = request.headers['Authorization']
    decoded_security_token = User.check_security_token(security_token=security_token)
    requester_user = User.get_user_by_email(email=decoded_security_token['email'])
    if decoded_security_token['role'] != 'Administrator':
        return error_handler(error_status=403, message='Forbidden permission!')
    if not requester_user:
        return error_handler(error_status=404, message=f'Not found!')
    school_subject = SchoolSubject.get_school_subject_by_id(school_subject_id=school_subject_id)
    if not school_subject:
        return error_handler(error_status=404, message=f"School subject doesn't exist!")
    school_subject.delete_school_subject()
    return HttpResponse(
        json.dumps(
            {
                'status': f'OK',
                'code': 200,
                'server_time': django.utils.timezone.now().strftime("%Y-%m-%dT%H:%M:%S"),
                'message': f'School subject is successfully deleted!',
            }
        ),
        content_type='application/json',
        status=200
    )


@api_view(['GET'])
@authorization
def get_all_school_classes(request):
    """
    This method will get all school classes
    :param request:
    :return: list of school classes
    """
    security_token = request.headers['Authorization']
    decoded_security_token = User.check_security_token(security_token=security_token)
    requester_user = User.get_user_by_email(email=decoded_security_token['email'])
    if decoded_security_token['role'] not in 'Administrator':
        return error_handler(error_status=403, message='Forbidden permission!')
    if not requester_user:
        return error_handler(error_status=404, message=f'Not found!')
    user = User.objects.filter(id=requester_user.id).first()
    if not user:
        return error_handler(error_status=404, message=f'Not found!')
    query_string = request.GET
    limit = query_string['limit'] if 'limit' in query_string else None
    offset = query_string['offset'] if 'offset' in query_string else None
    limit, offset = check_valid_limit_and_offset(limit=limit, offset=offset)
    school_classes = SchoolClass.get_all_school_classes(limit=limit, offset=offset)
    school_classes = SchoolClassSerializer(many=True, instance=school_classes).data
    school_classes_number = SchoolClass.count_school_classes()
    for school_class in school_classes:
        school_class['school_classes_number'] = school_classes_number
        school_class = dict(school_class)
    return HttpResponse(
        json.dumps(
            {
                'status': f'OK',
                'code': 200,
                'server_time': django.utils.timezone.now().strftime("%Y-%m-%dT%H:%M:%S"),
                'message': f'School classes',
                'results': school_classes,
            }
        ),
        content_type='application/json',
        status=200
    )


@api_view(['GET'])
@authorization
def get_all_school_classes_by_student_id(request, student_id):
    """
    This method will get all school classes by student id
    :param request:
    :param student_id:
    :return: list of school classes
    """
    security_token = request.headers['Authorization']
    decoded_security_token = User.check_security_token(security_token=security_token)
    requester_user = User.get_user_by_email(email=decoded_security_token['email'])
    if decoded_security_token['role'] not in ['Administrator', 'Parent']:
        return error_handler(error_status=403, message='Forbidden permission!')
    if not requester_user:
        return error_handler(error_status=404, message=f'Not found!')
    user = User.objects.filter(id=requester_user.id).first()
    if not user:
        return error_handler(error_status=404, message=f'Not found!')
    school_classes = SchoolClassStudent.get_school_classes_by_student_id(student_id=student_id)
    school_classes = SchoolClassSerializer(many=True, instance=school_classes).data
    school_classes_number = SchoolClass.count_school_classes()
    for school_class in school_classes:
        school_class['school_classes_number'] = school_classes_number
        school_class = dict(school_class)
    return HttpResponse(
        json.dumps(
            {
                'status': f'OK',
                'code': 200,
                'server_time': django.utils.timezone.now().strftime("%Y-%m-%dT%H:%M:%S"),
                'message': f'School classes',
                'results': school_classes,
            }
        ),
        content_type='application/json',
        status=200
    )


@api_view(['GET'])
@authorization
def get_all_student_grades(request, school_class_id, user_id, school_subject_id):
    """
    This method will get all student grades
    :param request:
    :param school_class_id:
    :param user_id:
    :param school_subject_id:
    :return: list of grades
    """
    security_token = request.headers['Authorization']
    decoded_security_token = User.check_security_token(security_token=security_token)
    requester_user = User.get_user_by_email(email=decoded_security_token['email'])
    if decoded_security_token['role'] not in ['Parent', 'Professor', 'Administrator']:
        return error_handler(error_status=403, message='Forbidden permission!')
    if not requester_user:
        return error_handler(error_status=404, message=f'Not found!')
    user = User.objects.filter(id=requester_user.id).first()
    if not user:
        return error_handler(error_status=404, message=f'Not found!')
    grades = Grade.get_all_grades_by_student_id_and_school_class_id_or_school_subject(
        student_id=user_id,
        school_subject_id=school_subject_id,
        school_class_id=school_class_id
    )
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
    return HttpResponse(
        json.dumps(
            {
                'status': f'OK',
                'code': 200,
                'server_time': django.utils.timezone.now().strftime("%Y-%m-%dT%H:%M:%S"),
                'message': f'Grades',
                'results': grades,
            }
        ),
        content_type='application/json',
        status=200
    )


@api_view(['GET'])
@authorization
def get_all_events_by_parent_id(request):
    """
    This method will get all the events by parent_id
    :param request:
    :return: list of events
    """
    security_token = request.headers['Authorization']
    decoded_security_token = User.check_security_token(security_token=security_token)
    requester_user = User.get_user_by_email(email=decoded_security_token['email'])
    if decoded_security_token['role'] not in ['Parent', 'Professor', 'Administrator']:
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
    return HttpResponse(
        json.dumps(
            {
                'status': f'OK',
                'code': 200,
                'server_time': django.utils.timezone.now().strftime("%Y-%m-%dT%H:%M:%S"),
                'message': f'Events',
                'results': events,
            }
        ),
        content_type='application/json',
        status=200
    )


@api_view(['GET'])
@authorization
def get_all_student_absences(request, school_class_id, user_id, school_subject_id, is_justified):
    """
    This method will get all the student absences
    :param request:
    :param school_class_id:
    :param user_id:
    :param school_subject_id:
    :param is_justified:
    :return: list of absences
    """
    security_token = request.headers['Authorization']
    decoded_security_token = User.check_security_token(security_token=security_token)
    requester_user = User.get_user_by_email(email=decoded_security_token['email'])
    if decoded_security_token['role'] not in ['Parent', 'Professor', 'Administrator']:
        return error_handler(error_status=403, message='Forbidden permission!')
    if not requester_user:
        return error_handler(error_status=404, message=f'Not found!')
    user = User.objects.filter(id=requester_user.id).first()
    if not user:
        return error_handler(error_status=404, message=f'Not found!')
    absences = Absence.get_all_absences(
        school_class_id=school_class_id,
        student_id=user_id,
        school_subject_id=school_subject_id,
        is_justified=is_justified
    )
    justified_absences, unjustified_absences = Absence.count_all_absences_by_justified(
        school_class_id=school_class_id,
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
    return HttpResponse(
        json.dumps(
            {
                'status': f'OK',
                'code': 200,
                'server_time': django.utils.timezone.now().strftime("%Y-%m-%dT%H:%M:%S"),
                'message': f'Absences',
                'results': absences,
            }
        ),
        content_type='application/json',
        status=200
    )


@api_view(['GET'])
@authorization
def get_all_student_absences_number(request, school_class_id, user_id, school_subject_id):
    """
    This method will count all the student absences
    :param request:
    :param school_class_id:
    :param user_id:
    :param school_subject_id:
    :return: number of justified and unjustified absences
    """
    security_token = request.headers['Authorization']
    decoded_security_token = User.check_security_token(security_token=security_token)
    requester_user = User.get_user_by_email(email=decoded_security_token['email'])
    if decoded_security_token['role'] not in ['Parent', 'Professor', 'Administrator']:
        return error_handler(error_status=403, message='Forbidden permission!')
    if not requester_user:
        return error_handler(error_status=404, message=f'Not found!')
    user = User.objects.filter(id=requester_user.id).first()
    if not user:
        return error_handler(error_status=404, message=f'Not found!')
    justified_absences, unjustified_absences = Absence.count_all_absences_by_justified(
        school_class_id=school_class_id,
        student_id=user_id,
        school_subject_id=school_subject_id
    )
    absences = {}
    absences['justified_absences'] = justified_absences
    absences['unjustified_absences'] = unjustified_absences
    return HttpResponse(
        json.dumps(
            {
                'status': f'OK',
                'code': 200,
                'server_time': django.utils.timezone.now().strftime("%Y-%m-%dT%H:%M:%S"),
                'message': f'Absences',
                'justified_absences': justified_absences,
                'unjustified_absences': unjustified_absences
            }
        ),
        content_type='application/json',
        status=200
    )


@api_view(['GET'])
@authorization
def get_all_roles(request):
    """
    This method will get all the roles
    :param request:
    :return: list of roles
    """
    security_token = request.headers['Authorization']
    decoded_security_token = User.check_security_token(security_token=security_token)
    requester_user = User.get_user_by_email(email=decoded_security_token['email'])
    if decoded_security_token['role'] != 'Administrator':
        return error_handler(error_status=403, message='Forbidden permission!')
    if not requester_user:
        return error_handler(error_status=404, message=f'Not found!')
    query_string = request.GET
    limit = query_string['limit'] if 'limit' in query_string else None
    offset = query_string['offset'] if 'offset' in query_string else None
    limit, offset = check_valid_limit_and_offset(limit=limit, offset=offset)
    roles = Role.get_all_roles(limit=limit, offset=offset)
    roles = RoleSerializer(many=True, instance=roles).data
    roles_number = Role.count_roles()
    for role in roles:
        role['roles_number'] = roles_number
        role = dict(role)
    return HttpResponse(
        json.dumps(
            {
                'status': f'OK',
                'code': 200,
                'server_time': django.utils.timezone.now().strftime("%Y-%m-%dT%H:%M:%S"),
                'message': f'Roles',
                'results': roles
            }
        ),
        content_type='application/json',
        status=200
    )


@api_view(['POST'])
@authorization
def add_new_role(request):
    """
    This method will add a new role
    :param request:
    :param_body: roleName
    :return: message
    """
    body = request.data
    if 'roleName' not in body:
        return error_handler(error_status=400, message=f'Wrong data!')
    security_token = request.headers['Authorization']
    decoded_security_token = User.check_security_token(security_token=security_token)
    requester_user = User.get_user_by_email(email=decoded_security_token['email'])
    if decoded_security_token['role'] != 'Administrator':
        return error_handler(error_status=403, message='Forbidden permission!')
    if not requester_user:
        return error_handler(error_status=404, message=f'Not found!')
    if not Role.add_new_role(role_name=body['roleName']):
        return error_handler(error_status=403, message=f'Role is not added!')
    return HttpResponse(
        json.dumps(
            {
                'status': f'OK',
                'code': 201,
                'server_time': django.utils.timezone.now().strftime("%Y-%m-%dT%H:%M:%S"),
                'message': f'Role is successfully added!',
            }
        ),
        content_type='application/json',
        status=201
    )


@api_view(['DELETE'])
@authorization
def delete_role(request, role_id):
    """
    This method will delete an old role
    :param request:
    :param role_id:
    :param_body: roleName
    :return: message
    """
    security_token = request.headers['Authorization']
    decoded_security_token = User.check_security_token(security_token=security_token)
    requester_user = User.get_user_by_email(email=decoded_security_token['email'])
    if decoded_security_token['role'] != 'Administrator':
        return error_handler(error_status=403, message='Forbidden permission!')
    if not requester_user:
        return error_handler(error_status=404, message=f'Not found!')
    role = Role.get_role_by_id(role_id=role_id)
    if not role:
        return error_handler(error_status=404, message=f"Role doesn't exist!")
    role.delete_role()
    return HttpResponse(
        json.dumps(
            {
                'status': f'OK',
                'code': 200,
                'server_time': django.utils.timezone.now().strftime("%Y-%m-%dT%H:%M:%S"),
                'message': f'Role is successfully deleted!',
            }
        ),
        content_type='application/json',
        status=200
    )


@api_view(['GET'])
@authorization
def get_all_genders(request):
    """
    This method will get all the genders
    :param request:
    :return: list of roles
    """
    security_token = request.headers['Authorization']
    decoded_security_token = User.check_security_token(security_token=security_token)
    requester_user = User.get_user_by_email(email=decoded_security_token['email'])
    if decoded_security_token['role'] != 'Administrator':
        return error_handler(error_status=403, message='Forbidden permission!')
    if not requester_user:
        return error_handler(error_status=404, message=f'Not found!')
    genders = Gender.get_all_genders()
    genders = GenderSerializer(many=True, instance=genders).data
    for gender in genders:
        gender = dict(gender)
    return HttpResponse(
        json.dumps(
            {
                'status': f'OK',
                'code': 200,
                'server_time': django.utils.timezone.now().strftime("%Y-%m-%dT%H:%M:%S"),
                'message': f'Genders',
                'results': genders
            }
        ),
        content_type='application/json',
        status=200
    )


@api_view(['POST'])
@authorization
def add_new_user(request):
    """
    This method will add a new user
    :param request:
    :param_body: first_name, last_name, email, roleId, genderId, address, city, password,
    phone, is_active, birth_date, parent_mother, parent_father
    :return: message
    """
    body = request.data
    if not Validation.add_user_validation(data=body):
        return error_handler(error_status=400, message=f'Wrong data!')
    security_token = request.headers['Authorization']
    decoded_security_token = User.check_security_token(security_token=security_token)
    requester_user = User.get_user_by_email(email=decoded_security_token['email'])
    if decoded_security_token['role'] != 'Administrator':
        return error_handler(error_status=403, message='Forbidden permission!')
    if not requester_user:
        return error_handler(error_status=404, message=f'Not found!')
    if not User.add_new_user(data=body):
        return error_handler(error_status=403, message=f'User is not added!')
    return HttpResponse(
        json.dumps(
            {
                'status': f'OK',
                'code': 201,
                'server_time': django.utils.timezone.now().strftime("%Y-%m-%dT%H:%M:%S"),
                'message': f'User is successfully added!',
            }
        ),
        content_type='application/json',
        status=201
    )


@api_view(['POST'])
@authorization
def edit_user(request, user_id):
    """
    This method will edit an old user
    :param request:
    :param user_id:
    :param_body: first_name, last_name, email, roleId, genderId, address, city,
    phone, is_active, birth_date, parent_mother, parent_father
    :return: message
    """
    body = request.data
    if not Validation.edit_user_validation(data=body):
        return error_handler(error_status=400, message=f'Wrong data!')
    security_token = request.headers['Authorization']
    decoded_security_token = User.check_security_token(security_token=security_token)
    requester_user = User.get_user_by_email(email=decoded_security_token['email'])
    if decoded_security_token['role'] != 'Administrator':
        return error_handler(error_status=403, message='Forbidden permission!')
    if not requester_user:
        return error_handler(error_status=404, message=f'Not found!')
    user = User.get_user_by_id(user_id=user_id, requester=requester_user.role.name)
    if not user:
        return error_handler(error_status=404, message=f'Not found!')
    if not user.edit_user(data=body):
        return error_handler(error_status=403, message=f'User is not edited!')
    return HttpResponse(
        json.dumps(
            {
                'status': f'OK',
                'code': 200,
                'server_time': django.utils.timezone.now().strftime("%Y-%m-%dT%H:%M:%S"),
                'message': f'User is successfully edited!',
            }
        ),
        content_type='application/json',
        status=200
    )


@api_view(['PATCH'])
@authorization
def change_user_password(request, user_id):
    """
    This method will change user's password through admin panel
    :param request:
    :param user_id:
    :param_body: password
    :return: message
    """
    body = request.data
    if not Validation.admin_change_user_password_validation(data=body):
        return error_handler(error_status=400, message=f'Wrong data!')
    security_token = request.headers['Authorization']
    decoded_security_token = User.check_security_token(security_token=security_token)
    requester_user = User.get_user_by_email(email=decoded_security_token['email'])
    if decoded_security_token['role'] != 'Administrator':
        return error_handler(error_status=403, message='Forbidden permission!')
    if not requester_user:
        return error_handler(error_status=404, message=f'Not found!')
    user = User.get_user_by_id(user_id=user_id, requester=requester_user.role.name)
    if not user:
        return error_handler(error_status=404, message=f'Not found!')
    if not user.change_password(password=body['password']):
        return error_handler(error_status=403, message=f'Password is not changed!')
    return HttpResponse(
        json.dumps(
            {
                'status': f'OK',
                'code': 200,
                'server_time': django.utils.timezone.now().strftime("%Y-%m-%dT%H:%M:%S"),
                'message': f'Password is successfully changed!',
            }
        ),
        content_type='application/json',
        status=200
    )


@api_view(['PATCH'])
@authorization
def edit_role(request, role_id):
    """
    This method will change a role (name)
    :param request:
    :param role_id:
    :param_body: name
    :return: message
    """
    body = request.data
    if not Validation.edit_role_validation(data=body):
        return error_handler(error_status=400, message=f'Wrong data!')
    security_token = request.headers['Authorization']
    decoded_security_token = User.check_security_token(security_token=security_token)
    requester_user = User.get_user_by_email(email=decoded_security_token['email'])
    if decoded_security_token['role'] != 'Administrator':
        return error_handler(error_status=403, message='Forbidden permission!')
    if not requester_user:
        return error_handler(error_status=404, message=f'Not found!')
    role = Role.get_role_by_id(role_id=role_id)
    if not role:
        return error_handler(error_status=404, message=f'Not found!')
    if not role.edit_role(data=body):
        return error_handler(error_status=403, message=f'Role is not changed!')
    return HttpResponse(
        json.dumps(
            {
                'status': f'OK',
                'code': 200,
                'server_time': django.utils.timezone.now().strftime("%Y-%m-%dT%H:%M:%S"),
                'message': f'Role is successfully changed!',
            }
        ),
        content_type='application/json',
        status=200
    )


@api_view(['GET'])
@authorization
def get_school_class_members(request, school_class_id):
    """
    This method will get all the users by class_id, the users are part of some class.
    :param request:
    :param school_class_id:
    :return: message, data
    """
    security_token = request.headers['Authorization']
    decoded_security_token = User.check_security_token(security_token=security_token)
    user = User.get_user_by_email(email=decoded_security_token['email'])
    if not user:
        return error_handler(error_status=404, message=f'Not found!')
    if decoded_security_token['role'] not in ['Administrator', 'Professor']:
        if decoded_security_token['role'] == 'Professor':
            if user.security_token() != security_token:
                return error_handler(error_status=403, message='Forbidden permission!')
        else:
            return error_handler(error_status=403, message='Forbidden permission!')
    query_string = request.GET
    limit = query_string['limit'] if 'limit' in query_string else None
    offset = query_string['offset'] if 'offset' in query_string else None
    limit, offset = check_valid_limit_and_offset(limit=limit, offset=offset)
    professors, students = SchoolClass.get_members_by_school_class_id(
        school_class_id=school_class_id,
        limit=limit,
        offset=offset
    )
    professors = SchoolCLassProfessorsSerializer(many=True, instance=professors).data
    students = SchoolCLassStudentsSerializer(many=True, instance=students).data
    users_number = SchoolClass.count_members_by_school_class_id(school_class_id=school_class_id)
    users_json = []
    for p in professors:
        p['users_number'] = users_number
        p = dict(p)
        p['professor'] = dict(p['professor'])
        p['professor']['role'] = dict(p['professor']['role'])
        p['professor']['gender'] = dict(p['professor']['gender'])
        p['professor']['parent_mother'] = dict(p['professor']['parent_mother']) if p['professor']['parent_mother'] else {}
        p['professor']['parent_father'] = dict(p['professor']['parent_father']) if p['professor']['parent_father'] else {}
        users_json.append(p)
    for s in students:
        s['users_number'] = users_number
        s = dict(s)
        s['student'] = dict(s['student'])
        s['student']['role'] = dict(s['student']['role'])
        s['student']['gender'] = dict(s['student']['gender'])
        s['student']['parent_mother'] = dict(s['student']['parent_mother']) if s['student']['parent_mother'] else {}
        s['student']['parent_father'] = dict(s['student']['parent_father']) if s['student']['parent_father'] else {}
        users_json.append(s)
    return HttpResponse(
        json.dumps(
            {
                'status': f'OK',
                'code': 200,
                'server_time': django.utils.timezone.now().strftime("%Y-%m-%dT%H:%M:%S"),
                'message': f'Users',
                'results': users_json
            }
        ),
        content_type='application/json',
        status=200
    )


@api_view(['DELETE'])
@authorization
def delete_school_class(request, school_class_id):
    """
    This method will delete an old school class
    :param request:
    :param school_class_id:
    :return: message
    """
    security_token = request.headers['Authorization']
    decoded_security_token = User.check_security_token(security_token=security_token)
    requester_user = User.get_user_by_email(email=decoded_security_token['email'])
    if decoded_security_token['role'] != 'Administrator':
        return error_handler(error_status=403, message='Forbidden permission!')
    if not requester_user:
        return error_handler(error_status=404, message=f'Not found!')
    school_class = SchoolClass.get_school_class_by_id(school_class_id=school_class_id)
    if not school_class:
        return error_handler(error_status=404, message=f"School class doesn't exist!")
    school_class.delete_school_class()
    return HttpResponse(
        json.dumps(
            {
                'status': f'OK',
                'code': 200,
                'server_time': django.utils.timezone.now().strftime("%Y-%m-%dT%H:%M:%S"),
                'message': f'School class is successfully deleted!',
            }
        ),
        content_type='application/json',
        status=200
    )


@api_view(['POST'])
@authorization
def add_school_class(request):
    """
    This method will add a new school class
    :param request:
    :param_body: name, school_year, is_active
    :return: message
    """
    body = request.data
    if not Validation.add_school_class_validation(data=body):
        return error_handler(error_status=400, message=f'Wrong data!')
    security_token = request.headers['Authorization']
    decoded_security_token = User.check_security_token(security_token=security_token)
    requester_user = User.get_user_by_email(email=decoded_security_token['email'])
    if decoded_security_token['role'] != 'Administrator':
        return error_handler(error_status=403, message='Forbidden permission!')
    if not requester_user:
        return error_handler(error_status=404, message=f'Not found!')
    if not SchoolClass.add_new_school_class(data=body):
        return error_handler(error_status=403, message='School class is not added!')
    return HttpResponse(
        json.dumps(
            {
                'status': f'OK',
                'code': 201,
                'server_time': django.utils.timezone.now().strftime("%Y-%m-%dT%H:%M:%S"),
                'message': f'School class is successfully added!',
            }
        ),
        content_type='application/json',
        status=201
    )


@api_view(['PUT'])
@authorization
def edit_school_class(request, school_class_id):
    """
    This method will edit a school class
    :param request:
    :param school_class_id:
    :param_body: id, name, is_active
    :return: message
    """
    body = request.data
    if not Validation.edit_school_class_validation(data=body):
        return error_handler(error_status=400, message=f'Wrong data!')
    security_token = request.headers['Authorization']
    decoded_security_token = User.check_security_token(security_token=security_token)
    requester_user = User.get_user_by_email(email=decoded_security_token['email'])
    if decoded_security_token['role'] != 'Administrator':
        return error_handler(error_status=403, message='Forbidden permission!')
    if not requester_user:
        return error_handler(error_status=404, message=f'Not found!')
    if not SchoolClass.edit_new_school_class(data=body, school_class_id=school_class_id):
        return error_handler(error_status=403, message='School class is not edited!')
    return HttpResponse(
        json.dumps(
            {
                'status': f'OK',
                'code': 200,
                'server_time': django.utils.timezone.now().strftime("%Y-%m-%dT%H:%M:%S"),
                'message': f'School class is successfully edited!',
            }
        ),
        content_type='application/json',
        status=200
    )


@api_view(['POST'])
@authorization
def add_school_class_member(request):
    """
    This method will add a member into school class
    :param request:
    :param_body: is_active, role_name, school_class_id, user_id
    :return: message
    """
    body = request.data
    if not Validation.add_member_to_school_class_validation(data=body):
        return error_handler(error_status=400, message=f'Wrong data!')
    security_token = request.headers['Authorization']
    decoded_security_token = User.check_security_token(security_token=security_token)
    requester_user = User.get_user_by_email(email=decoded_security_token['email'])
    if decoded_security_token['role'] != 'Administrator':
        return error_handler(error_status=403, message='Forbidden permission!')
    if not requester_user:
        return error_handler(error_status=404, message=f'Not found!')
    if body['role_name'] not in ['professor', 'student']:
        return error_handler(error_status=400, message=f'Wrong data!')
    if body['role_name'] == 'professor':
        if not SchoolClassProfessor.add_new_member(data=body):
            return error_handler(error_status=403, message='Member is not added to this school class!')
    else:
        if not SchoolClassStudent.add_new_member(data=body):
            return error_handler(error_status=403, message='Member is not added to this school class!')
    return HttpResponse(
        json.dumps(
            {
                'status': f'OK',
                'code': 201,
                'server_time': django.utils.timezone.now().strftime("%Y-%m-%dT%H:%M:%S"),
                'message': f'Member is successfully added to this school class!',
            }
        ),
        content_type='application/json',
        status=201
    )


@api_view(['PATCH'])
@authorization
def activate_or_deactivate_school_class_member(request, member_id):
    """
    This method will activate or deactivate school class member
    :param request:
    :param member_id:
    :param_body: is_active, role_name
    :return: message
    """
    body = request.data
    if not Validation.activate_or_deactivate_school_class_member_validation(data=body):
        return error_handler(error_status=400, message=f'Wrong data!')
    security_token = request.headers['Authorization']
    decoded_security_token = User.check_security_token(security_token=security_token)
    requester_user = User.get_user_by_email(email=decoded_security_token['email'])
    if decoded_security_token['role'] != 'Administrator':
        return error_handler(error_status=403, message='Forbidden permission!')
    if not requester_user:
        return error_handler(error_status=404, message=f'Not found!')
    if body['role_name'] not in ['Professor', 'Student']:
        return error_handler(error_status=400, message=f'Wrong data!')
    if body['role_name'] == 'Professor':
        member = SchoolClassProfessor.find_member_by_member_id(member_id=member_id)
    else:
        member = SchoolClassStudent.find_member_by_member_id(member_id=member_id)
    if not member:
        return error_handler(error_status=404, message=f'Not found!')
    member.activate_or_deactivate_member(is_active=body['is_active'])
    return HttpResponse(
        json.dumps(
            {
                'status': f'OK',
                'code': 200,
                'server_time': django.utils.timezone.now().strftime("%Y-%m-%dT%H:%M:%S"),
                'message': f'Member is successfully activated!' if body['is_active'] != False else f'Member is successfully deactivated!',
            }
        ),
        content_type='application/json',
        status=200
    )


@api_view(['DELETE'])
@authorization
def delete_school_class_member(request, role_name, member_id):
    """
    This method will delete an old school class member
    :param request:
    :param role_name:
    :param member_id:
    :return: message
    """
    security_token = request.headers['Authorization']
    decoded_security_token = User.check_security_token(security_token=security_token)
    requester_user = User.get_user_by_email(email=decoded_security_token['email'])
    if decoded_security_token['role'] != 'Administrator':
        return error_handler(error_status=403, message='Forbidden permission!')
    if not requester_user:
        return error_handler(error_status=404, message=f'Not found!')
    if role_name not in ['Professor', 'Student']:
        return error_handler(error_status=400, message=f'Wrong data!')
    if role_name == 'Professor':
        member = SchoolClassProfessor.find_member_by_member_id(member_id=member_id)
    else:
        member = SchoolClassStudent.find_member_by_member_id(member_id=member_id)
    if not member:
        return error_handler(error_status=404, message=f'Not found!')
    member.delete()
    return HttpResponse(
        json.dumps(
            {
                'status': f'OK',
                'code': 200,
                'server_time': django.utils.timezone.now().strftime("%Y-%m-%dT%H:%M:%S"),
                'message': f'School class member is successfully deleted!',
            }
        ),
        content_type='application/json',
        status=200
    )


@api_view(['GET'])
@authorization
def get_school_class_subjects(request, school_class_id):
    """
    This method will get all school class subjects
    :param request:
    :param school_class_id:
    :return: list of school class subjects
    """
    security_token = request.headers['Authorization']
    decoded_security_token = User.check_security_token(security_token=security_token)
    requester_user = User.get_user_by_email(email=decoded_security_token['email'])
    if decoded_security_token['role'] not in ['Administrator', 'Professor', 'Parent']:
        return error_handler(error_status=403, message='Forbidden permission!')
    if not requester_user:
        return error_handler(error_status=404, message=f'Not found!')
    user = User.objects.filter(id=requester_user.id).first()
    if not user:
        return error_handler(error_status=404, message=f'Not found!')
    query_string = request.GET
    limit = query_string['limit'] if 'limit' in query_string else None
    offset = query_string['offset'] if 'offset' in query_string else None
    limit, offset = check_valid_limit_and_offset(limit=limit, offset=offset)
    school_class_subjects = ClassRoomSchoolSubject.get_all_school_subjects_by_school_class_id(
        school_class_id=school_class_id,
        limit=limit,
        offset=offset
    )
    school_class_subjects_number = ClassRoomSchoolSubject.count_all_school_subjects_by_school_class_id(
        school_class_id=school_class_id
    )
    school_class_subjects = SchoolClassSubjectsSerializer(many=True, instance=school_class_subjects).data
    for school_class_subject in school_class_subjects:
        school_class_subject['school_class_subjects_number'] = school_class_subjects_number
        school_class_subject = dict(school_class_subject)
    return HttpResponse(
        json.dumps(
            {
                'status': f'OK',
                'code': 200,
                'server_time': django.utils.timezone.now().strftime("%Y-%m-%dT%H:%M:%S"),
                'message': f'School classe subjects',
                'results': school_class_subjects,
            }
        ),
        content_type='application/json',
        status=200
    )


@api_view(['DELETE'])
@authorization
def delete_school_class_subject(request, school_class_subject_id):
    """
    This method will delete an old school class subject
    :param request:
    :param school_class_subject_id:
    :return: message
    """
    security_token = request.headers['Authorization']
    decoded_security_token = User.check_security_token(security_token=security_token)
    requester_user = User.get_user_by_email(email=decoded_security_token['email'])
    if decoded_security_token['role'] != 'Administrator':
        return error_handler(error_status=403, message='Forbidden permission!')
    if not requester_user:
        return error_handler(error_status=404, message=f'Not found!')
    school_class_subject = ClassRoomSchoolSubject.get_school_school_subject_by_id(
        school_subject_id=school_class_subject_id
    )
    if not school_class_subject:
        return error_handler(error_status=404, message=f'Not found!')
    school_class_subject.delete()
    return HttpResponse(
        json.dumps(
            {
                'status': f'OK',
                'code': 200,
                'server_time': django.utils.timezone.now().strftime("%Y-%m-%dT%H:%M:%S"),
                'message': f'School class subject is successfully deleted!',
            }
        ),
        content_type='application/json',
        status=200
    )


@api_view(['PATCH'])
@authorization
def activate_or_deactivate_school_class_subject(request, school_class_subject_id):
    """
    This method will activate or deactivate school class subject
    :param request:
    :param school_class_subject_id:
    :param_body: is_active,
    :return: message
    """
    body = request.data
    if not Validation.activate_or_deactivate_school_class_subject_validation(data=body):
        return error_handler(error_status=400, message=f'Wrong data!')
    security_token = request.headers['Authorization']
    decoded_security_token = User.check_security_token(security_token=security_token)
    requester_user = User.get_user_by_email(email=decoded_security_token['email'])
    if decoded_security_token['role'] != 'Administrator':
        return error_handler(error_status=403, message='Forbidden permission!')
    if not requester_user:
        return error_handler(error_status=404, message=f'Not found!')
    school_class_subject = ClassRoomSchoolSubject.get_school_school_subject_by_id(
        school_subject_id=school_class_subject_id
    )
    if not school_class_subject:
        return error_handler(error_status=404, message=f'Not found!')
    school_class_subject.activate_or_deactivate_school_class_subject(body['is_active'])
    return HttpResponse(
        json.dumps(
            {
                'status': f'OK',
                'code': 200,
                'server_time': django.utils.timezone.now().strftime("%Y-%m-%dT%H:%M:%S"),
                'message': f'School class subject is successfully activated!' if body['is_active'] != False else f'School class subject is successfully deactivated!',
            }
        ),
        content_type='application/json',
        status=200
    )


@api_view(['POST'])
@authorization
def add_school_class_subject(request):
    """
    This method will add a school subject into school class
    :param request:
    :param_body: is_active, user_id, school_subject_id, school_class_id
    :return: message
    """
    body = request.data
    if not Validation.add_school_subject_to_school_class_validation(data=body):
        return error_handler(error_status=400, message=f'Wrong data!')
    security_token = request.headers['Authorization']
    decoded_security_token = User.check_security_token(security_token=security_token)
    requester_user = User.get_user_by_email(email=decoded_security_token['email'])
    if decoded_security_token['role'] != 'Administrator':
        return error_handler(error_status=403, message='Forbidden permission!')
    if not requester_user:
        return error_handler(error_status=404, message=f'Not found!')
    if not ClassRoomSchoolSubject.add_new_school_subject(data=body):
        return error_handler(error_status=403, message='Member is not added to this school class!')
    return HttpResponse(
        json.dumps(
            {
                'status': f'OK',
                'code': 201,
                'server_time': django.utils.timezone.now().strftime("%Y-%m-%dT%H:%M:%S"),
                'message': f'School subject is successfully added to this school class!',
            }
        ),
        content_type='application/json',
        status=201
    )


# @api_view(['GET'])
# @authorization
# def get_all_school_subjects_by_student_id(request, student_id):
#     """
#     This method will get all school subjects from last school class by student id
#     :param request:
#     :return: list of school subjects
#     """
#     security_token = request.headers['Authorization']
#     decoded_security_token = User.check_security_token(security_token=security_token)
#     requester_user = User.get_user_by_email(email=decoded_security_token['email'])
#     if decoded_security_token['role'] not in ['Parent', 'Professor', 'Administrator']:
#         return error_handler(error_status=403, message='Forbidden permission!')
#     if not requester_user:
#         return error_handler(error_status=404, message=f'Not found!')
#     user = User.objects.filter(id=requester_user.id).first()
#     if not user:
#         return error_handler(error_status=404, message=f'Not found!')
#     query_string = request.GET
#     limit = query_string['limit'] if 'limit' in query_string else None
#     offset = query_string['offset'] if 'offset' in query_string else None
#     limit, offset = check_valid_limit_and_offset(limit=limit, offset=offset)
#     school_subjects = SchoolSubject.get_all_school_subjects(limit=limit, offset=offset)
#     school_subjects = SchoolSubjectSerializer(many=True, instance=school_subjects).data
#     school_subjects_number = SchoolSubject.count_school_subject()
#     for school_subject in school_subjects:
#         school_subject['school_subjects_number'] = school_subjects_number
#         school_subject = dict(school_subject)
#     return HttpResponse(
#         json.dumps(
#             {
#                 'status': f'OK',
#                 'code': 200,
#                 'server_time': django.utils.timezone.now().strftime("%Y-%m-%dT%H:%M:%S"),
#                 'message': f'School subjects',
#                 'results': school_subjects
#             }
#         ),
#         content_type='application/json',
#         status=200
#     )
