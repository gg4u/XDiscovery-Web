# xdiscovery_web


## Development environment

Requirements:
	``pyenv``

## Python 

Pyenv (optional):

	# install pyenv
	# (see https://github.com/yyuu/pyenv#installation)
	# install python 2.7.5
	pyenv install 2.7.5
	# activate local pyenv
	pyenv local 2.7.5 && pyenv rehash
	# install old virtualenv & setuptools

Virtualenv setup:

	# create virtual environment
	virtualenv --distribute virtual
	# activate virtualenv
	source virtual/bin/activate
	# install python packages
	pip install -r requirements/dev.txt


Setup ruby environment:

    # install rvm
	curl -L get.rvm.io | bash -s stable
	# install ruby 1.9
	rvm install 1.9.3
	# select ruby package
	rvm use 1.9.3
	rvm gemset create xdiscovery_web
	rvm gemset use xdiscovery_web


### NodeJS

Nodeenv:

    # nodeenv is already installed by pip (python)
    # install nodejs
	nodeenv -n 0.10.20 virtualnode
	# activate local npm repo
	cd frontend
	export PATH=$(pwd)/node_modules/.bin:$PATH
	npm install


Install other services: ``postgresql``, ``memcache`

To start developing, activate the local develpment environment:

	source ./activate.sh


## Staging environment setup


### Setup S3 environment:
 - create a bucket named ``xdiscovery_web-staging`` with a public read access policy
 - add a IAM user with put permission on the bucket
 - setup CORS policy for bucket
 - set user access credentials and bucket name in heroku config vars (see
   below)


### Heroku environment:

Provision heroku environment:

    heroku apps:create xdiscovery-web-staging -s cedar
    heroku addons:add heroku-postgresql:dev --version=9.4 --app xdiscovery-web-staging
    heroku addons:add memcachier:dev -a xdiscovery-web-staging
    heroku addons:add sendgrid:starter -a xdiscovery-web-staging
    heroku addons:add logentries:tryit -a xdiscovery-web-staging
    # no ssl endpoint needed as we leverage heroku piggyback ssl


Define app-specific environment variables:

	heroku config:add SECRET_KEY=xxxx ADMIN_URL_HASH=secret -a xdiscovery-web_staging
    heroku config:set DJANGO_SETTINGS_MODULE=xdimension_web.settings.heroku --app xdimension-web-staging
    heroku config:set DISABLE_CSRF=1 DEPLOY_MODE=staging REST_API_DOCS_ENABLE=1 -a xdimension-web-staging


Define S3 auth stuff:

    heroku config:set AWS_ACCESS_KEY_ID=XXX AWS_SECRET_ACCESS_KEY=XXX -a xdimension-web-staging


see ``.secret/config_staging.sh`` and ``.env-staging``


## Bootstrapping the app

Create postgres db and user account (only in local mode, as heroku already 
has permissions set):

    fab create_db_local

Synchronize database:

    python manage.py syncdb
    python manage.py migrate --all
    python manage.py createsuperuser

Set default site name from the admin web console.


## Deploy

To build the frontend app and integrate it into the backend do:

    fab build

Commit all the changes (if any) made by the build process to the
auto-generated django templates.

Deploy both frontend and backend:

    fab deploy:environment=staging



## Code structure

Backend is contained in the ``xdimension_web`` python package.

Frontend is contained in the ``frontend`` directory.


## Front End Notes

To run the frontend, execute `grunt server` in the `frontend` directory
