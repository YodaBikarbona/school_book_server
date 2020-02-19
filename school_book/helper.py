from django.utils import timezone
from random import choice, random
from hashlib import sha512
import django
from django.http import HttpResponse
import json
import string


def now():
    return timezone.now()


def new_salt():
    source = [chr(x) for x in range(32, 127)]
    salt = u''.join(choice(source) for x in range(0, 32))
    return salt


def new_psw(salt, password):
    password = str(sha512(u'{0}{1}'.format(password, salt).encode('utf-8', 'ignore')).hexdigest())
    return password


def ok_response(message, additional_data=None):
    data = {
        'status': 'OK',
        'code': 200,
        'server_time': django.utils.timezone.now().strftime("%Y-%m-%dT%H:%M:%S"),
        'message': message,
    }
    results = []
    result = {}
    if additional_data:
        if type(additional_data) == dict:
            result = additional_data
        else:
            for d in additional_data:
                results.append(d)
    if results:
        data['results'] = results
    else:
        data = result
        data['status'] = 'OK'
        data['code'] = 200
        data['server_time'] = django.utils.timezone.now().strftime("%Y-%m-%dT%H:%M:%S")
        data['message'] = message
    response = HttpResponse(
        json.dumps(data),
        content_type='application/json',
        status=200
    )
    return response


def error_handler(error_status, message):
    data = {
            'status': 'ERROR',
            'server_time': django.utils.timezone.now().strftime("%Y-%m-%dT%H:%M:%S"),
            'code': error_status,
            'message': message
    }
    response = HttpResponse(
        json.dumps(data),
        content_type='application/json',
        status=error_status
    )
    return response


def activation_code(size):
    return ''.join([random.choice(string.ascii_letters + string.digits) for n in range(size)])
