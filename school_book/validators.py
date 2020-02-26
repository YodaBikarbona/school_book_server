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
            data['is_deleted']
            data['birth_date']
            data['gender_id']
            data['role_id']
            data['parent_mother']
            data['parent_father']
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
