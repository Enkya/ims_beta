# Bucketlist API

[![Build Status](https://travis-ci.org/Enkya/ims_beta.svg?branch=master)](https://travis-ci.org/Enkya/ims_beta)
[![Coverage Status](https://coveralls.io/repos/github/Elbertbiggs360/buckelist-api/badge.svg?branch=master)](https://coveralls.io/github/Elbertbiggs360/buckelist-api?branch=master)
[![Code Climate](https://codeclimate.com/github/Elbertbiggs360/buckelist-api/badges/gpa.svg)](https://codeclimate.com/github/Elbertbiggs360/buckelist-api)
![MIT License](https://github.com/Enkya/ims_beta/blob/master/mit.png)

## Demo

You can test the API demo hosted at https://ims-api.herokuapp.com in Postman

##Usage

| EndPoint | Functionality | Public Access |
| -------- | ------------- | ------------- |
| `POST /auth/login`| Logs a user in | TRUE |
| `POST /auth/register`| Register a user | TRUE |
| `POST /companies/`| Create a new company | TRUE |
| `GET /companies/`| List all the created companies | TRUE |
| `GET /users/`| List all the created users | FALSE |
| `GET /users/\<id>`| Get a specific user | FALSE |
| `GET /companies/\<id>`| Get single company | TRUE |
| `DELETE /companies/\<id>`| Delete this single company | TRUE |
| `GET /companies?q=\<company_name>`| Search for companies with the same name as that passed in company_name | TRUE |

---

## Features
- Signup and login User
- Create companies

## Prerequisites:
* Python 3.3^
* Flask
* PostGres

## API Engine

#### How to run the engine
* Clone the application: *git clone git@github.com:Enkya/ims_beta.git*
* cd into the bucketlist-api: `cd ims_beta`
* Run `python install -r requirements.txt`
* Create database
* Initialize, migrate, and upgrade the database:
    ```
    python manage.py db init
    python manage.py db migrate
    python manage.py db upgrade
    ```
* The above command downloads all the dependencies needed for the project
* Run the server `python run.py`
* You can now access the api from 127.0.0.1:5000/api/v1

---

## Testing
- To test, run the following command: ```coverage run --source app run_tests.py```
- View the test coverage with: ``` coverage report ```

---

This project is licensed under the terms of the **MIT** license.