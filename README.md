# YummyAPI

[![Build Status](https://travis-ci.org/shakirandagire/YummyAPI.svg?branch=develop)](https://travis-ci.org/shakirandagire/YummyAPI) [![Coverage Status](https://coveralls.io/repos/github/shakirandagire/YummyAPI/badge.svg?branch=develop)](https://coveralls.io/github/shakirandagire/YummyAPI?branch=develop)

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
    

YummyApi endpoints
/register	 POST	Registers new user	FALSE
/login	POST	Handles POST request for /auth/login	TRUE
/logout	GET	Logs out a user	TRUE
/reset-password	POST	Reset user password	TRUE
/category	GET	Get every category of logged in user	TRUE
/category/{_id}	GET	Get category with {id} of logged in user	TRUE
/category	POST	Create a new category	TRUE
/category/{_id}	PUT	Update a category with {id} of logged in user	TRUE
/category/{_id}	DELETE	Delete category with {id} of logged in user	TRUE
/recipe	POST	Creates a recipe	TRUE
/recipes/{id}	GET	Gets a single recipe	TRUE
/recipe/{id}	PUT	Updates a single recipe	TRUE
/recipe/{id}	DELETE	Deletes a single recipe	TRUE
    

 


