class Validation:

    @classmethod
    def add_user_validation(cls, data):
        try:
            data['first_name']
            data['last_name']
            data['email']
            data['address']
            data['city']
            data['phone']
            data['is_active']
            data['birth_date']
            data['gender_id']
            data['role_id']
            data['parent_mother']
            data['parent_father']
            data['password']
            data['newsletter']
            return True
        except Exception as ex:
            print(ex)
            return False

    @classmethod
    def edit_user_validation(cls, data):
        try:
            data['first_name']
            data['last_name']
            data['email']
            data['address']
            data['city']
            data['phone']
            data['is_active']
            data['birth_date']
            data['gender_id']
            data['role_id']
            data['parent_mother']
            data['parent_father']
            data['newsletter']
            return True
        except Exception as ex:
            print(ex)
            return False

    @classmethod
    def admin_change_user_password_validation(cls, data):
        try:
            data['password']
            return True
        except Exception as ex:
            print(ex)
            return False

    @classmethod
    def edit_role_validation(cls, data):
        try:
            data['name']
            return True
        except Exception as ex:
            print(ex)
            return False

    @classmethod
    def add_school_subject_validation(cls, data):
        try:
            data['name']
            data['is_active']
            return True
        except Exception as ex:
            print(ex)
            return False

    @classmethod
    def edit_school_subject_validation(cls, data):
        try:
            data['name']
            data['is_active']
            return True
        except Exception as ex:
            print(ex)
            return False

    @classmethod
    def add_school_class_validation(cls, data):
        try:
            data['name']
            data['school_year']
            data['is_active']
            return True
        except Exception as ex:
            print(ex)
            return False

    @classmethod
    def edit_school_class_validation(cls, data):
        try:
            data['name']
            data['is_active']
            return True
        except Exception as ex:
            print(ex)
            return False

    @classmethod
    def add_member_to_school_class_validation(cls, data):
        try:
            data['is_active']
            data['role_name']
            data['school_class_id']
            data['user_id']
            return True
        except Exception as ex:
            print(ex)
            return False

    @classmethod
    def activate_or_deactivate_school_class_member_validation(cls, data):
        try:
            data['is_active']
            data['role_name']
            return True
        except Exception as ex:
            print(ex)
            return False

    @classmethod
    def activate_or_deactivate_school_class_subject_validation(cls, data):
        try:
            data['is_active']
            return True
        except Exception as ex:
            print(ex)
            return False

    @classmethod
    def add_school_subject_to_school_class_validation(cls, data):
        try:
            data['is_active']
            data['user_id']
            data['school_subject_id']
            data['school_class_id']
            return True
        except Exception as ex:
            print(ex)
            return False

    @classmethod
    def add_grade_validation(cls, data):
        try:
            data['comment']
            data['grade']
            data['grade_type']
            data['user_id']
            data['school_subject_id']
            data['school_class_id']
            return True
        except Exception as ex:
            print(ex)
            return False

    @classmethod
    def add_absence_validation(cls, data):
        try:
            data['comment']
            data['is_justified']
            data['title']
            data['student_id']
            data['school_class_id']
            data['school_subject_id']
            return True
        except Exception as ex:
            print(ex)
            return False

    @classmethod
    def edit_absence_validation(cls, data):
        try:
            data['absence_id']
            data['comment']
            data['is_justified']
            data['title']
            return True
        except Exception as ex:
            print(ex)
            return False

    @classmethod
    def add_event_validation(cls, data):
        try:
            data['comment']
            data['title']
            data['date']
            data['school_class_id']
            data['school_subject_id']
            return True
        except Exception as ex:
            print(ex)
            return False
