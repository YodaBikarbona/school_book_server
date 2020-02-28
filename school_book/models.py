from django.db import models
import django
from school_book.helper import (
    new_salt,
    new_psw,
    ok_response,
    error_handler
)
from school_book.constants import (
    OFFSET,
    LIMIT,
    LIMIT_CHOICES,
    secret_key_word
)
from django.db.models import Q
from jose import jwt
from datetime import datetime
from django.core.validators import ValidationError
import random
import string
from datetime import datetime, timedelta
from django.core.mail import send_mail
# Create your models here.


class Role(models.Model):
    created = models.DateTimeField(default=django.utils.timezone.now)
    name = models.CharField(
        max_length=50,
        unique=True,
        help_text=f'This field is required!'
    )

    def __str__(self):
        return self.name

    @classmethod
    def get_all_roles(cls, limit, offset):
        roles = Role.objects.filter().order_by('id').all()
        if limit not in LIMIT_CHOICES:
            limit = 0
        if offset and limit and limit > offset:
            roles = roles[offset*limit:(offset*limit)+limit]
        elif not offset and limit and limit > offset:
            roles = roles[:offset+limit]
        return roles

    @classmethod
    def count_roles(cls):
        return Role.objects.filter().count()

    def delete_role(self):
        self.delete()

    @classmethod
    def add_new_role(cls, role_name):
        try:
            role = Role()
            role.name = role_name
            role.created = django.utils.timezone.now().strftime("%Y-%m-%dT%H:%M:%S")
            role.save()
            return True
        except Exception as ex:
            print(ex)
            return False

    @classmethod
    def get_role_by_id(cls, role_id):
        return Role.objects.filter(id=role_id).first()

    def edit_role(self, data):
        try:
            self.name = data['name']
            self.save()
            return True
        except Exception as ex:
            print(ex)
            return False


class Gender(models.Model):
    created = models.DateTimeField(default=django.utils.timezone.now)
    name = models.CharField(
        max_length=10,
        unique=True,
        help_text='This field is required!'
    )

    def __str__(self):
        return f'{self.name}'

    @classmethod
    def get_all_genders(cls):
        return Gender.objects.filter().all()


class User(models.Model):
    created = models.DateTimeField(default=django.utils.timezone.now)
    first_login = models.DateTimeField(
        null=True,
        blank=True,
        help_text=f'This field will fill automatically after first login! Non-required!'
    )
    last_login = models.DateTimeField(
        null=True,
        blank=True,
        help_text=f'This field will fill automatically after every login! Non-required!'
    )
    first_name = models.CharField(
        max_length=50,
        null=False,
        help_text=f'This field is required!'
    )
    last_name = models.CharField(
        max_length=50,
        null=False,
        help_text=f'This field is required!'
    )
    email = models.EmailField(
        max_length=50,
        null=True,
        blank=True,
        help_text=f'This field is required only if role is not a Student!'
    )
    address = models.CharField(
        max_length=100,
        null=False,
        help_text=f'This field is required!'
    )
    city = models.CharField(
        max_length=50,
        null=False,
        help_text=f'This field is required!'
    )
    phone = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        help_text=f'This field is required only if role is not a Student!'
    )
    salt = models.CharField(
        max_length=255,
        default=new_salt(),
        null=True,
        blank=True,
        help_text=f'This field is self generated! Do not change it through Django Admin. Required!'
    )
    admin_password = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text=f'This password will be encrypted through Django Admin! This field is required!'
    )
    password = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text=f"This field shouldn't be used through Django Admin! Non-required!")
    is_active = models.BooleanField(default=False)
    is_delete = models.BooleanField(default=False)
    birth_date = models.DateField(
        null=False,
        help_text=f'This field is required!'
    )
    activation_code = models.CharField(
        max_length=10,
        null=True,
        blank=True,
        help_text=f'This field will fill automatically when user become deactivated! Field will be deleted when '
        f'user become activated! Non-required!'
    )
    expired_activation_code = models.DateTimeField(
        null=True,
        blank=True,
        help_text=f'This field will fill automatically! Activation code will not be valid if user uses activation '
        f'code after one hour! Non-required!'
    )

    # Relationships
    gender = models.ForeignKey(
        Gender,
        null=True,
        on_delete=models.SET_NULL
    )
    role = models.ForeignKey(
        Role,
        null=True,
        on_delete=models.SET_NULL
    )
    parent_mother = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        related_name='User.parent_mother+',
        null=True,
        blank=True,
        help_text=f'This field is required if role is a Student! Optional if parent_father is filled!'
    )
    parent_father = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        related_name='User.parent_father+',
        null=True,
        blank=True,
        help_text=f'This field is required if role is a Student! Optional if parent_mother is filled!'
    )

    def __str__(self):
        return f"{self.first_name} {self.last_name} {self.email if self.email else None} {self.role.name if self.role else ''}"

    @staticmethod
    def set_password(salt, password):
        return new_psw(salt, password)

    def password_strength(self):
        is_lower = False
        is_upper = False
        is_digit = False
        is_special_character = False
        spec = "@#$%^&+=.!/?*-"
        if self.admin_password:
            if (len(self.admin_password) < 8) and (len(self.admin_password) > 25):
                return False
            for let in self.admin_password:
                try:
                    let = int(let)
                    is_digit = True
                except Exception as ex:
                    # print(ex)
                    if let in spec:
                        is_special_character = True
                    else:
                        if let.isalpha():
                            if let == let.upper():
                                is_upper = True
                            if let == let.lower():
                                is_lower = True
            if is_upper and is_lower and is_special_character and is_digit:
                return True
            else:
                return False
        return False

    def save(self, *args, **kwargs):
        """
        This method is override of main method!
        """
        existing_id = False
        changing_password = False
        if self.role.name == 'Student':
            self.admin_password = None
            self.password = None
            self.email = None
            self.phone = None
            self.salt = None
            if not self.parent_mother or not self.parent_father:
                raise ValidationError(f'One of parent fields is required!')
        elif self.role.name in ['Administrator', 'Parent', 'Professor', 'test']:
            if not self.admin_password and not self.password and not self.email and not self.phone and not self.salt:
                raise ValidationError(f'Fields admin_password, password, email, phone and salt are required!')
            if not self.id:
                if not self.is_active:
                    self.activation_code = self.create_activation_code(10)
                    self.expired_activation_code = django.utils.timezone.now() + timedelta(hours=2)
                if self.check_user_unique_email(email=self.email):
                    raise ValidationError(f'User with {self.email} already exists!')
                if not self.password_strength():
                    raise ValueError(f'Password is not valid!')
                self.password = new_psw(self.salt, self.admin_password)
            else:
                existing_id = True
                edit_user = User.objects.filter(id=self.id).first()
                if edit_user.email != self.email:
                    if self.check_user_unique_email(email=self.email):
                        raise ValidationError(f'User with {self.email} already exists!')
                if self.admin_password and edit_user.password != new_psw(self.salt, self.admin_password):
                    changing_password = True
                    if not self.password_strength():
                        raise ValueError(f'Password is not valid!')
                    self.password = new_psw(self.salt, self.admin_password)
                    self.admin_password = ''
                    self.is_active = False
                    self.activation_code = self.create_activation_code(10)
                    self.expired_activation_code = django.utils.timezone.now() + timedelta(hours=2)
            self.parent_mother = None
            self.parent_father = None
            self.admin_password = None
        else:
            return f"Error! This role doesn't exist inside roles constant!"
        super().save(*args, **kwargs)
        if not existing_id or (existing_id and changing_password):
            if self.send_activation_code_on_email():
                return ok_response(message=f'Mail sent successfully!')
            else:
                return error_handler(error_status=502, message=f"Mail didn't send!")

    @staticmethod
    def check_user_unique_email(email):
        if User.objects.filter(
                email=email,
                is_delete=False
        ):
            return True
        return False

    def change_password(self, password):
        try:
            self.admin_password = password
            self.save()
            return True
        except Exception as ex:
            print(ex)
            return False

    @classmethod
    def add_new_user(cls, data):
        try:
            user = User()
            user.first_name = data['first_name']
            user.last_name = data['last_name']
            user.email = data['email']
            user.address = data['address']
            user.city = data['city']
            user.phone = data['phone']
            user.is_active = data['is_active']
            user.birth_date = data['birth_date']
            user.gender_id = data['gender_id']
            user.role_id = data['role_id']
            user.parent_mother_id = data['parent_mother']
            user.parent_father_id = data['parent_father']
            user.admin_password = data['password']
            user.created = django.utils.timezone.now().strftime("%Y-%m-%dT%H:%M:%S")
            user.save()
            return True
        except Exception as ex:
            print(ex)
            return False

    def edit_user(self, data):
        try:
            self.first_name = data['first_name']
            self.last_name = data['last_name']
            self.email = data['email']
            self.address = data['address']
            self.city = data['city']
            self.phone = data['phone']
            self.is_active = data['is_active']
            self.is_delete = data['is_deleted']
            self.birth_date = data['birth_date']
            self.gender_id = data['gender_id']
            self.role_id = data['role_id']
            self.parent_mother_id = data['parent_mother']
            self.parent_father_id = data['parent_father']
            self.save()
            return True
        except Exception as ex:
            print(ex)
            return False

    @classmethod
    def get_user_by_id(cls, user_id, requester, parent_id=None):
        user = User.objects.filter(id=user_id)
        if requester not in ['Administrator', 'Professor', 'Parent']:
            return None
        if requester == 'Professor':
            user = user.filter(role__name__in=['Professor', 'Student', 'Parent'])
        if requester == 'Parent' and parent_id:
            user = user.filter(Q(parent_mother=parent_id) | Q(parent_father=parent_id))
        return user.first()

    @classmethod
    def get_all_users(cls, data, requester):
        """
        This method will get all users depends on filters, is user is deleted, deactivated etc.
        :return: user_list
        """
        filters = []
        offset = OFFSET
        limit = LIMIT
        if data:
            for k, v in data.items():
                filters.append(k)
        users = User.objects.filter()
        if 'is_deleted' in filters:
            try:
                int(data['is_deleted'])
                if int(data['is_deleted']) in [0, 1]:
                    users = users.filter(is_delete=data['is_deleted'])
            except ValueError as ex:
                print(ex)
        if 'is_active' in filters:
            try:
                int(data['is_active'])
                if int(data['is_active']) in [0, 1]:
                    users = users.filter(is_active=data['is_active'])
            except ValueError as ex:
                print(ex)
        if 'roleId' in filters:
            try:
                int(data['roleId'])
                if int(data['roleId']) > 0:
                    users = users.filter(role=data['roleId'])
            except ValueError as ex:
                print(ex)
        if 'genderId' in filters:
            try:
                int(data['genderId'])
                if int(data['genderId']) > 0:
                    users = users.filter(gender=data['genderId'])
            except ValueError as ex:
                print(ex)
        if 'birthDate' in filters and data['birthDate'] != '':
            try:
                datetime.strptime(data['birthDate'], "%Y-%m-%d").strftime("%Y-%m-%d")
                users = users.filter(birth_date=data['birthDate'])
            except ValueError as ex:
                print(ex)
        if requester not in ['Administrator', 'Professor']:
            return []
        if requester == 'Professor':
            users = users.filter(role__name__in=['Professor', 'Student', 'Parent'])
        if 'offset' in filters:
            try:
                offset = int(data['offset'])
            except ValueError as ex:
                print(ex)
        if 'limit' in filters:
            try:
                limit = int(data['limit'])
                if limit not in LIMIT_CHOICES:
                    limit = 0
            except ValueError as ex:
                print(ex)
        if 'search' in filters:
            search = data['search']
            users = users.filter(
                Q(phone__icontains=search) |
                Q(address__icontains=search) |
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(email__icontains=search)
            )
        users = users.order_by('id')
        if offset and limit and limit > offset:
            users = users[offset*limit:(offset*limit)+limit]
        elif not offset and limit and limit > offset:
            users = users[:offset+limit]
        return users.all()

    @classmethod
    def count_all_users(cls, data, requester):
        filters = []
        search = ''
        if data:
            for k, v in data.items():
                filters.append(k)
        users = User.objects.filter()
        if 'is_deleted' in filters:
            try:
                int(data['is_deleted'])
                if int(data['is_deleted']) in [0, 1]:
                    users = users.filter(is_delete=data['is_deleted'])
            except ValueError as ex:
                print(ex)
        if 'is_active' in filters:
            try:
                int(data['is_active'])
                if int(data['is_active']) in [0, 1]:
                    users = users.filter(is_active=data['is_active'])
            except ValueError as ex:
                print(ex)
        if 'roleId' in filters:
            try:
                int(data['roleId'])
                if int(data['roleId']) > 0:
                    users = users.filter(role=data['roleId'])
            except ValueError as ex:
                print(ex)
        if 'genderId' in filters:
            try:
                int(data['genderId'])
                if int(data['genderId']) > 0:
                    users = users.filter(gender=data['genderId'])
            except ValueError as ex:
                print(ex)
        if 'birthDate' in filters and data['birthDate'] != '':
            try:
                datetime.strptime(data['birthDate'], "%Y-%m-%d").strftime("%Y-%m-%d")
                users = users.filter(birth_date=data['birthDate'])
            except ValueError as ex:
                print(ex)
        if requester not in ['Administrator', 'Professor']:
            return []
        if requester == 'Professor':
            users = users.filter(role__name__in=['Professor', 'Student', 'Parent'])
        if 'search' in filters:
            search = data['search']
            users = users.filter(
                Q(phone__icontains=search) |
                Q(address__icontains=search) |
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(email__icontains=search)
            )
        return users.count()

    def delete(self, using=None, keep_parents=False):
        """
        Overrated original delete method, this method will set is_delete method to True, and user will never be deleted
        from database
        :param using:
        :param keep_parents:
        :return:
        """
        self.is_delete = True
        self.save()

    def activate_user(self):
        """
        This method will activate user
        :return:
        """
        if (django.utils.timezone.now() + timedelta(hours=1)) <= self.expired_activation_code:
            self.is_active = True
            self.activation_code = None
            self.expired_activation_code = None
        else:
            return False
        try:
            self.save()
            return True
        except Exception as ex:
            print(ex)
            return False

    def deactivate_user(self):
        """
        This method will deactivate user
        :return:
        """
        self.is_active = False
        self.activation_code = self.create_activation_code(10)
        self.expired_activation_code = django.utils.timezone.now() + timedelta(hours=2)
        try:
            self.save()
            return True
        except Exception as ex:
            print(ex)
            return False

    @classmethod
    def get_user_by_email(cls, email):
        user = User.objects.filter(email=email).first()
        return user

    def security_token(self):
        signed = jwt.encode(
            {'email': '{0}'.format(self.email),
             'role': '{0}'.format(self.role.name),
             'user_id': self.id
             }, secret_key_word, algorithm='HS256')
        return signed

    @classmethod
    def check_security_token(cls, security_token):
        try:
            decode = jwt.decode(security_token, secret_key_word, algorithms='HS256')
        except Exception as ex:
            print(ex)
            return False
        if 'email' not in decode or 'role' not in decode or 'user_id' not in decode:
            return False
        return decode

    @classmethod
    def check_user_login_password(cls, user, password):
        if user.password != cls.set_password(salt=user.salt, password=password):
            return False
        return True

    @staticmethod
    def create_activation_code(size):
        return ''.join([random.choice(string.ascii_letters + string.digits) for n in range(size)])

    def send_activation_code_on_email(self):
        """
        This method will (try) send activation code on user email, activation code will expire in 1 hour.
        If user didn't activate an account, user need ask another activation code.
        :return: True if mail has sent False if mail has not sent
        """
        subject = f'Activation code'
        activation_code = self.activation_code
        message = f'Activation code: {activation_code}. This code will expire in 1 hour!'
        from_email = f'mihael.peric@hotmail.com'
        to_email = f'{self.email}'
        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=from_email,
                recipient_list=[to_email],
                fail_silently=False
            )
            return True
        except Exception as ex:
            print(ex)
            return False

    def get_children_by_parent_id(self):
        children = User.objects.filter(Q(parent_mother=self.id) | Q(parent_father=self.id))
        return children.all()


class SchoolClass(models.Model):
    created = models.DateTimeField(default=django.utils.timezone.now)
    school_year = models.CharField(
        max_length=9,
        null=False,
        help_text=f'This field is required!'
    )
    name = models.CharField(
        max_length=50,
        unique=True,
        help_text=f'This field is required!'
    )
    is_active = models.BooleanField(
        default=False,
        help_text=f'If class room is deactivated, professors can only read class room and all related with class room!'
    )

    def __str__(self):
        return f'{self.name} {self.school_year}'

    @classmethod
    def get_all_school_classes(cls, limit, offset):
        school_classes = SchoolClass.objects.filter().order_by('-id').all()
        if limit not in LIMIT_CHOICES:
            limit = 0
        if offset and limit and limit > offset:
            school_classes = school_classes[offset * limit:(offset * limit) + limit]
        elif not offset and limit and limit > offset:
            school_classes = school_classes[:offset + limit]
        return school_classes

    @classmethod
    def count_school_classes(cls):
        return SchoolClass.objects.filter().count()

    @classmethod
    def get_members_by_school_class_id(cls, school_class_id, limit, offset):
        professors = SchoolClassProfessor.objects.prefetch_related('professor').filter(
            school_class_id=school_class_id
        ).all()
        students = SchoolClassStudent.objects.prefetch_related('student').filter(
            school_class_id=school_class_id
        ).all()
        # professors = [m.professor for m in professors]
        # students = [m.student for m in students]
        # members = professors + students
        # if limit not in LIMIT_CHOICES:
        #     limit = 0
        # if offset and limit and limit > offset:
        #     members = members[offset*limit:(offset*limit)+limit]
        # elif not offset and limit and limit > offset:
        #     members = members[:offset+limit]
        return professors, students

    @classmethod
    def count_members_by_school_class_id(cls, school_class_id):
        professors_number = SchoolClassProfessor.objects.filter(school_class_id=school_class_id).count()
        students_number = SchoolClassStudent.objects.filter(school_class_id=school_class_id).count()
        return professors_number + students_number


class SchoolClassProfessor(models.Model):
    created = models.DateTimeField(default=django.utils.timezone.now)
    is_active = models.BooleanField(
        default=False,
        help_text=f'If professor is deactivated then professor can only read student information!'
    )

    # Relationships
    professor = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text=f'This field is required!'
    )
    school_class = models.ForeignKey(
        SchoolClass,
        on_delete=models.CASCADE,
        null=False,
        help_text=f'This field is required!'
    )

    class Meta:
        unique_together = ('professor', 'school_class')

    def __str__(self):
        return f'{self.professor.first_name} {self.professor.last_name}'

    def save(self, *args, **kwargs):
        if not self.professor or not self.school_class:
            raise ValueError(f'Fields required professor, school_subject, school_class')
        if self.professor.role.name != 'Professor':
            raise ValueError(f"Professor hasn't Professor role, role is {self.professor.role.name}!")
        super().save(*args, **kwargs)


class SchoolClassStudent(models.Model):
    created = models.DateTimeField(default=django.utils.timezone.now)
    is_active = models.BooleanField(
        default=False,
        help_text=f'If student is deactivated then professor can see only read student information!'
    )

    # Relationships
    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=False,
        help_text=f'This field is required!'
    )
    school_class = models.ForeignKey(
        SchoolClass,
        on_delete=models.CASCADE,
        null=False,
        help_text=f'This field is required!'
    )

    class Meta:
        unique_together = ('student', 'school_class')

    def __str__(self):
        return f'{self.student.first_name} {self.student.last_name}'

    def save(self, *args, **kwargs):
        if not self.student or not self.school_class:
            raise ValueError(f'Fields required professor, school_subject, school_class')
        if self.student.role.name != 'Student':
            raise ValueError(f"Student hasn't Student role, role is {self.student.role.name}!")
        super().save(*args, **kwargs)


class SchoolSubject(models.Model):
    created = models.DateTimeField(default=django.utils.timezone.now)
    is_active = models.BooleanField(
        default=False,
        help_text=f"If school subject is deactivated then that school subject can't be chosen in school class subjects!"
    )
    name = models.CharField(
        max_length=50,
        unique=True,
        help_text=f'This field is required!'
    )

    def __str__(self):
        return f"{self.name} {'(Activated)' if self.is_active else '(Deactivated)'}"

    @classmethod
    def get_all_school_subjects(cls, limit, offset):
        school_subjects = SchoolSubject.objects.filter().order_by('id').all()
        if limit not in LIMIT_CHOICES:
            limit = 0
        if offset and limit and limit > offset:
            school_subjects = school_subjects[offset*limit:(offset*limit)+limit]
        elif not offset and limit and limit > offset:
            school_subjects = school_subjects[:offset+limit]
        return school_subjects

    @classmethod
    def count_school_subject(cls):
        return SchoolSubject.objects.filter().count()

    @classmethod
    def add_new_school_subject(cls, data):
        try:
            school_subject = SchoolSubject()
            school_subject.name = data['name']
            school_subject.is_active = data['is_active']
            school_subject.created = django.utils.timezone.now().strftime("%Y-%m-%dT%H:%M:%S")
            school_subject.save()
            return True
        except Exception as ex:
            print(ex)
            return False

    def delete_school_subject(self):
        self.delete()

    @classmethod
    def get_school_subject_by_id(cls, school_subject_id):
        return SchoolSubject.objects.filter(id=school_subject_id).first()

    def edit_school_subject(self, data):
        try:
            self.name = data['name']
            self.is_active = data['is_active']
            self.save()
            return True
        except Exception as ex:
            print(ex)
            return False


class ClassRoomSchoolSubject(models.Model):
    created = models.DateTimeField(default=django.utils.timezone.now)
    is_active = models.BooleanField(
        default=False,
        help_text=f"If school subject is deactivated then that school subject can be readable only!"
    )

    # Relationships
    professor = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        help_text=f'This field is required!'
    )

    school_subject = models.ForeignKey(
        SchoolSubject,
        on_delete=models.SET_NULL,
        null=True,
        help_text=f'This field is required!'
    )

    school_class = models.ForeignKey(
        SchoolClass,
        on_delete=models.SET_NULL,
        null=True,
        help_text=f'This field is required!'
    )

    class Meta:
        unique_together = ('professor', 'school_subject', 'school_class')

    def __str__(self):
        return f"{self.school_subject.name} {'(Activated)' if self.is_active else '(Deactivated)'}"

    def save(self, *args, **kwargs):
        if not self.professor or not self.school_subject or not self.school_class:
            raise ValueError(f'Fields required professor, school_subject, school_class')
        if self.professor.role.name != 'Professor':
            raise ValueError(f"Professor hasn't Professor role, role is {self.professor.role.name}!")
        if not self.school_subject.is_active:
            raise ValueError(f'This school subject is deactivated!')
        if not self.school_class.is_active:
            raise ValueError(f'This school class is deactivated!')
        super().save(*args, **kwargs)


class Grade(models.Model):
    created = models.DateTimeField(default=django.utils.timezone.now)
    grade = models.IntegerField(
        null=False,
        blank=False,
        help_text=f'Professor can enter grades in range 1-5. Required!'
    )
    grade_type = models.CharField(
        max_length=50,
        null=False,
        blank=False,
        help_text=f'Professor can enter some type e.g exam. Required!'
    )
    comment = models.CharField(
        max_length=128,
        null=True,
        blank=True,
        help_text=f"This is additional field to set some notes e.g Student didn't learn last lesion! Not required!"
    )

    # Relationships
    professor = models.ForeignKey(
        User,
        related_name='User.professor+',
        on_delete=models.SET_NULL,
        null=True,
        help_text=f'This field is required!'
    )

    student = models.ForeignKey(
        User,
        related_name='User.student+',
        on_delete=models.SET_NULL,
        null=True,
        help_text=f'This field is required!'
    )

    school_subject = models.ForeignKey(
        SchoolSubject,
        on_delete=models.SET_NULL,
        null=True,
        help_text=f'This field is required!'
    )

    school_class = models.ForeignKey(
        SchoolClass,
        on_delete=models.SET_NULL,
        null=True,
        help_text=f'This field is required!'
    )

    class Meta:
        unique_together = ('professor', 'school_subject')

    def __str__(self):
        return f"{self.school_subject.name} {self.grade} {self.student.first_name} {self.student.last_name}"

    def save(self, *args, **kwargs):
        if not self.professor or not self.student or not self.school_subject or not self.school_class:
            raise ValueError(f'Fields required professor, student, school_subject, school_class')
        if self.professor.role.name != 'Professor':
            raise ValueError(f"Professor hasn't Professor role, role is {self.professor.role.name}!")
        if self.student.role.name != 'Student':
            raise ValueError(f"Student hasn't Student role, role is {self.student.role.name}!")
        if self.grade < 0 or self.grade > 5:
            raise ValueError(f'The grade is not in range 1-5, grade is {self.grade}!')
        if not self.school_subject.is_active:
            raise ValueError(f'This school subject is deactivated!')
        if not self.professor.is_active:
            raise ValueError(f'This professor is deactivated!')
        if not self.student.is_active:
            raise ValueError(f'This student is deactivated!')
        if not self.school_class.is_active:
            raise ValueError(f'The school class is deactivated!')
        super().save(*args, **kwargs)

    @classmethod
    def get_all_grades_by_student_id_or_school_subject_id(cls, student_id, school_subject_id):
        grades = Grade.objects.filter(student_id=student_id)
        if school_subject_id > 0:
            grades = grades.filter(school_subject_id=school_subject_id)
        return grades.all()


class Event(models.Model):
    created = models.DateTimeField(default=django.utils.timezone.now)
    title = models.CharField(
        max_length=64,
        null=False,
        blank=False,
        help_text=f'Professor will use this field to set title of event, e.g exam, excursion etc. '
        f'This field is required!'
    )
    comment = models.CharField(
        max_length=128,
        null=False,
        blank=False,
        help_text=f"Here professors add new events that parents could see and motivate their "
        f"children to get better results! E.g. Math exam in 13.02.2020 in 13:00:00 or Math exam will be"
        f"next friday or this field could be as some school events like excursion etc. This field is required!"
    )
    date = models.DateTimeField(
        null=False,
        blank=False,
        help_text=f'This field is required!'
    )

    # Relationships
    professor = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        help_text=f'This field is required!'
    )

    school_class = models.ForeignKey(
        SchoolClass,
        on_delete=models.SET_NULL,
        null=True,
        help_text=f'This field is required!'
    )

    school_subject = models.ForeignKey(
        SchoolSubject,
        on_delete=models.SET_NULL,
        null=True,
        help_text=f'This field is optional! This field will help parents to know if event is exam and'
        f'which school subject is about.'
    )

    def __str__(self):
        return f"{self.title} {self.date}"

    def save(self, *args, **kwargs):
        if not self.professor or not self.school_class:
            raise ValueError(f'Fields required professor, school_class')
        if self.professor.role.name not in ['Professor', 'Administrator']:
            raise ValueError(f"Professor hasn't Professor role, role is {self.professor.role.name}!")
        if not self.professor.is_active:
            raise ValueError(f'This professor is deactivated!')
        if not self.school_class.is_active:
            raise ValueError(f'The school class is deactivated!')
        super().save(*args, **kwargs)

    @classmethod
    def get_all_events_by_parent_id(cls, parent_id):
        children = User.objects.filter(Q(parent_father=parent_id) | Q(parent_mother=parent_id)).all()
        if not children:
            return []
        children_ids = [child.id for child in children]
        children_school_classes = SchoolClassStudent.objects.filter(
            student_id__in=children_ids,
            is_active=True
        ).all()
        school_class_ids = list(set([school_class.id for school_class in children_school_classes]))
        events = Event.objects.filter(school_class_id__in=school_class_ids).all()
        return events


class Absence(models.Model):
    created = models.DateTimeField(default=django.utils.timezone.now)
    title = models.CharField(
        max_length=64,
        null=True,
        blank=True,
        help_text=f'This filed will help parents to have a better view. Not required!'
    )
    comment = models.CharField(
        max_length=128,
        null=False,
        blank=False,
        help_text=f'Professor needs enter a reason of absence. E.g. student did not show up. Required!'
    )
    is_justified = models.BooleanField(
        default=False,
        help_text=f'This field will help professors and parents to see is some absence justified. Not required!'
    )

    # Relationships
    professor = models.ForeignKey(
        User,
        related_name='User.professor+',
        on_delete=models.SET_NULL,
        null=True,
        help_text=f'This field is required!'
    )

    student = models.ForeignKey(
        User,
        related_name='User.student+',
        on_delete=models.SET_NULL,
        null=True,
        help_text=f'This field is required!'
    )

    school_subject = models.ForeignKey(
        SchoolSubject,
        on_delete=models.SET_NULL,
        null=True,
        help_text=f'This field is required!'
    )

    school_class = models.ForeignKey(
        SchoolClass,
        on_delete=models.SET_NULL,
        null=True,
        help_text=f'This field is required!'
    )

    def __str__(self):
        return f"{self.title} {self.student.first_name} {self.student.last_name} " \
            f"{'(Justified)' if self.is_justified else '(Unjustified)'}"

    def save(self, *args, **kwargs):
        if not self.professor or not self.student or not self.school_subject or not self.school_class:
            raise ValueError(f'Fields required professor, student, school_subject, school_class')
        if self.professor.role.name != 'Professor':
            raise ValueError(f"Professor hasn't Professor role, role is {self.professor.role.name}!")
        if self.student.role.name != 'Student':
            raise ValueError(f"Student hasn't Student role, role is {self.student.role.name}!")
        if not self.school_subject.is_active:
            raise ValueError(f'This school subject is deactivated!')
        if not self.professor.is_active:
            raise ValueError(f'This professor is deactivated!')
        if not self.student.is_active:
            raise ValueError(f'This student is deactivated!')
        if not self.school_class.is_active:
            raise ValueError(f'The school class is deactivated!')
        super().save(*args, **kwargs)

    @classmethod
    def get_all_absences(cls, student_id, school_subject_id, is_justified):
        absences = Absence.objects.filter(
            student_id=student_id,
            student__is_active=True
        )
        if school_subject_id > 0:
            absences = absences.filter(
                school_subject_id=school_subject_id,
                school_subject__is_active=True
            )
        if is_justified == 'true':
            absences = absences.filter(is_justified=True)
        if is_justified == 'false':
            absences = absences.filter(is_justified=False)
        return absences.all()

    @classmethod
    def count_all_absences_by_justified(cls, student_id, school_subject_id):
        justified_absences = Absence.objects.filter(
            student_id=student_id,
            student__is_active=True,
            is_justified=True
        )
        unjustified_absences = Absence.objects.filter(
            student_id=student_id,
            student__is_active=True,
            is_justified=False
        )
        if school_subject_id > 0:
            justified_absences = justified_absences.filter(
                school_subject_id=school_subject_id,
                school_subject__is_active=True
            )
            unjustified_absences = unjustified_absences.filter(
                school_subject_id=school_subject_id,
                school_subject__is_active=True
            )
        return justified_absences.count(), unjustified_absences.count()
