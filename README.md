# School Book
This project will help the professors to make their work easier (adding the grades, the absences, the school events etc.)
and the parents to see their children grades, school events (like the exams, this could help the parents to motivate
their children to learn harder and get the better results), absences etc.

## Instalation
After cloning git repository open terminal and go into project
```bash
cd your_path_to_project/school_book_server
```

Then set up the enviroment for python 3
```bash
python3 -m venv
```

After that activate the enviroment
```bash
source venv/bin/activate
```

After you activated the enviroment install the packages from requirements.txt file using [pip](https://pip.pypa.io/en/stable/)
```bash
pip3 install -r requirements.txt
```

## Database settings
After instalation you need configure a postgres database

Open settings.py through some editor
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'mydatabase', # Database name
        'USER': 'mydatabaseuser', # Database user
        'PASSWORD': 'mypassword', # Database password
        'HOST': 'databasehost', # Database host e.g. for test this local you use 'localhost'
        'POST': 'databaseport' # Database port e.g. 5050 if you test this local you don't need port it could be empty ''
    }
}
```
