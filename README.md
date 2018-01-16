# YummyAPI

[![Build Status](https://travis-ci.org/shakirandagire/YummyAPI.svg?branch=develop)](https://travis-ci.org/shakirandagire/YummyAPI) [![Coverage Status](https://coveralls.io/repos/github/shakirandagire/YummyAPI/badge.svg?branch=develop)](https://coveralls.io/github/shakirandagire/YummyAPI?branch=develop) [![Maintainability](https://api.codeclimate.com/v1/badges/377e45ff09bf8bbf1d0b/maintainability)](https://codeclimate.com/github/shakirandagire/YummyAPI/maintainability)

The YummyAPI is an api that allows users register and login, and perform functions like creating, viewing, editing and deleting of categories and recipes.

# Basic installations for the project
Python 3 - The language used in the development of the application.

Flask - Python framework used in the application

Virtualenv - A virtual environment to help separate the project dependencies from ther projects

PostgreSQL – Postgres database used by the application.

Psycopg2 – This is a python addon from Python.

# Procedures to setup the API
1. Clone the repository

    $ git clone https://github.com/shakirandagire/YummyAPI.git
    
2. Create and activate the virtual environment.

    $ cd YummyAPI
    
    $ virtualenv apienv
    
    For MacOS 
    $ source /apienv/bin/activate
    
    For Windows
    apienv\Scripts\activate.bat
    
3. Installing all tools required by the API

    pip install -r requirements.
    
4. Running the tests

    To set up unit testing environment:
    
    $ pip install nose

    To execute a test 
    
    $ nosetests

5. To initialize the database so that you can create the tables.

    python manager.py db init
    
    python manager.py db migrate
    
    python manager.py db upgrade

6. Start The Server in the terminal

    export FLASK_CONFIG="development"
    
    python run.py
    

### YummyApi endpoints

Registers new user

| Endpoints | Method | Description |
| ----------| ------ | ----------- |
| [/api/v1/auth/login](#)	        | POST | Logs in user                |
| [/api/v1/auth/logout](#)	        | POST | Logs out a user	         |
| [/api/v1/auth/change_password](#)	| POST | Changes the user's password |
| [/api/v1/categories/](#)	        | POST | Posting categories          |
| [/api/v1/categories/](#)	        | GET  | Getting all categories      |
| [/api/v1/categories/](#)	        | POST | Logs in user                |
| [/api/v1/auth/logout](#)	        | POST | Logs out a user	         |
| [/api/v1/auth/change_password](#)	| POST | Changes the user's password |
| [/api/v1/categories/](#)	        | POST | Posting categories          |
| [/api/v1/categories/](#)	        | GET  | Getting all categories      |






/api/v1/categories/\<category_id> GET     Getting category by id

/api/v1/categories/{category_id} PUT     Editing category by id

/api/v1/categories/{category_id} DELETE  Deleting category by id

/api/v1/categories/{category_id}/recipes  POST    Posting recipes

/api/v1/categories/{category_id}/recipes  GET     Getting all recipes

/api/v1/categories/{category_id}/recipes/{recipe_id} GET     Getting recipe by id

/api/v1/categories/{category_id}/recipes/{recipe_id} PUT     Editing recipe by id

/api/v1/categories/{category_id}/recipes/{recipe_id} DELETE  Deleting recipe by id


