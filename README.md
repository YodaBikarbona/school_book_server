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

## Database configuration
After the instalation you need configure a postgres database

Open settings.py through some editor and make some changes
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

## Email configuration
After the database configuration you need make an email configuration

Open settings.py through some editor and make some changes
```python
EMAIL_HOST = 'emailhost' # E.g. for gmail it should be 'smtp.gmail.com', for the other domains you should find the host on google.
EMAIL_HOST_USER = 'email' # This should be an email (account) that will send the emails to the users
EMAIL_HOST_PASSWORD = 'password' # The email's (account's) password
EMAIL_PORT = 'emailport' # The email's port e.g for gmail it should be '587', for the other domains you should find the ports on google.
```

## Make the database migrations and create the superuser
After you configure the database and email configurations you need make the database migrations

Go to the terminal and type this command
```bash
python3 manage.py migrate
```

After that you should create the superuser (for django admin) typing this command
```bash
python3 manage.py createsuperuser
```
Username: Your django admin username

Email address: Your django admin email

Password: Your django admin password

Password (again): Confirm your password

If you created successfully the superuser your will get this message

Superuser created successfully.

## Run the server
After all previously steps you can run server using terminal command
```bash
python manage.py runserver
```

Or you can make the configuration in your IDE/Editor (I recommend PyCharm Professional)

After running the server you should see this in the terminal

Starting development server at http://127.0.0.1:8000/ (this is in my case)

Just click on the link or copy link and paste it in your browser

To see django admin you need add this in your url admin/ and use your data that you use to create the superuser.

