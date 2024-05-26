# mitasny

Very simple project management tool made with Django.

Create tasks and give them estimated required work (in days) and you will get estimate of the finish date for each task,
assuming a 5 day work week.

There is a running instance here:
http://mitasny.com/project/mitasny/


Set up development environment
------------------------------

Get sources:

    git clone https://github.com/jarnoln/mitasny.git

Create virtual environment and install Python packages:

    mkvirtualenv -p /usr/bin/python3 mitasny
    pip install -r requirements.txt

Generate password:

    python mitasny/generate_passwords.py mitasny/passwords.py

Initialize DB:

    ./manage.py migrate
    ./manage.py makemigrations tasks
    ./manage.py migrate tasks

Run tests:

    ./manage.py test

If tests pass, you should be good to go.

Run development server:

    ./manage.py runserver

Now should be able to see Mitasny your browser at http://127.0.0.1:8000/
