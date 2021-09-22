# Django Azure B2C Auth

Just playing a bit with [Django](https://www.djangoproject.com/) 🐍 and [Azure B2C](https://docs.microsoft.com/en-us/azure/active-directory-b2c/overview) 🆔.

## Prerequisites

- Python 3.9

- Pipenv

## Running the app

To install dependencies, run:

```bash
pipenv install
```

First, active this project's virtualenv:

```bash
pipenv shell
```

To run the migrations, type the following (only required on first run):

```bash
python manage.py migrate
```

At the root folder, type the following command to up the `server`:

```bash
python3 manage.py runserver --noreload
```

to open the `homepage`, put the following in your browser:

```bash
http://localhost:8000
```

## Samples

Articles:

- [Configure authentication in a sample Python web app by using Azure AD B2C](https://docs.microsoft.com/en-us/azure/active-directory-b2c/configure-authentication-sample-python-web-app)

Projects:

- [Python Flask webapp that signs in users with Azure AD B2C](https://github.com/Azure-Samples/ms-identity-b2c-python-flask-webapp-authentication)
- [Integrating Microsoft Identity Platform with a Python web application](https://github.com/Azure-Samples/ms-identity-python-webapp)
