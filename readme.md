
# UP Tap

An attendance management system built for UP System. Uses facial recognition and RFID scanning for fast and efficient attendance recording.

## Table of Contents
1. [About](#about)
2. [Features](#features)
3. [Technologies Used](#technologies-used)
4. [Installation](#installation)
5. [Setting Up Locally](#setting-up-locally)
6. [Contributing](#contributing)
7. [License](#license)

## About

(..to be updated..)

## Features

- Fast and accurate facial recognition based on the Facenet model.
- Utilizes the newly released UP RFID card, and together with facial recognition, forms a 2-step validation process to identify a student accurately.

## Technologies Used

- **Python**: `3.12.X`
- **[Django](https://www.djangoproject.com/)**: `5.1.X` - the web framework for perfectionists with deadlines
- **[Django-Ninja](https://django-ninja.dev/)**: `1.3.X` - production-grade and fast to setup REST framework on top of Django
- **[PostgreSQL](https://www.postgresql.org/)**: `17.2` - The World's Most Advanced Open Source Relational Database
- **[Nuxt 3](https://nuxt.com/)**:  - The Intuitive Vue Framework
- **[deepface](https://github.com/serengil/deepface)** - For wrapping popular face detection and recognition models into an easy to use library

## Setting up locally

### PostgreSQL
- Please see the database setup **[here](https://www.djangoproject.com/)**. You should have the following environment variables saved in the .env file after properly setting up Postgre.
  ```env
  DATABASE_NAME=<your_database_name>
  DATABASE_USER=<your_database_username> #defaults to 'postgre'
  DATABASE_PASSWORD=<your_database_password>
  DATABASE_HOST=<your_database_hostname> #defaults to 'localhost'
  DATABASE_PORT=<your_database_port>
  ```

### Django backend

- Ensure you have **Python** and **pip** installed on your machine.
- Install **virtualenv** if not already installed: 
  ```bash
  pip install virtualenv
  ```
- Create and start virtual environment in the project directory, then install needed packages:
  ```bash
  # For Python 3 
  py -m venv venv
  
  # in cmd, activate virtual environment
  .\venv\Scripts\activate
  
  # install packages
  pip install -r requirements.txt
  ```
- Write necessary environment variables in .env file
  ```
  #see https://djecrety.ir/
  DJANGO_SECRETKEY=<your_generated_django_secret_key> 

  #default="localhost:3000"
  DOMAIN=<your_nuxt_dev_server"

  #setup 2-Factor Authentication and generate your app password
  EMAIL_HOST_USER=<your_email>
  EMAIL_HOST_PASSWORD=<your_account_app_password>
  ```
- Run database migrations
  ```bash
  # For Python 3 
  py manage.py makemigrations
  py manage.py migrate
  ```
 - Create a superuser (basically a supercharged Teacher account) account for managing Django
   ```bash
   # For Python 3 
   py manage.py createsuperuser 
   ```
 - Run Django server
	 ```bash
	 py manage.py runserver
	 ```
- Open the Django Ninja Automated API documentation http://127.0.0.1:8000/api/docs and the Django admin http://127.0.0.1:8000/admin

### Nuxt frontend
- After running the Django server, run Nuxt server using:
  ```bash
  npm run dev
  ```
- Open the link provided by the dev server, usually http://localhost:3000


## Contributing
  We are currently not accepting pull requests as this is our final project for the degree of BS Computer Science. Issues are open however. Thank you.

### License
Distributed under the GNU GENERAL PUBLIC LICENSE. See LICENSE.txt for more information.