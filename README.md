# xdiscovery_web

## Tools

Generate thumbnails:

	python manage.py xdw_core_generate_map_thumbnails

Rebuild seach engine:

	python manage.py xdw_core_restore_topics


## Development environment


### setup virtualbox and vagrant


- install virtualbox
- install vagrant
- install sourcetree
- clone repo
- copy `package.box` into local directory (the one with Vagrantfile)
- cd `dir_with_Vagrantfile`
- vagrant up
- `vagrant ssh` to enter the vagrant machine
- copy `.env-staging` and `.env-production`

inside the vagrant machine do:
 - `cd /vagarant`
 - `npm install -g grunt-cli`
 - `npm install -g bower`
 - `cd frontend && npm install`
 - `gem install compass`
 - `cd frontend && bower install`

### working on the vm
- cd `dir_with_Vagrantfile`
- `vagrant up`
- `vagrant ssh` to login
- `cd /vagrant`
- to build the app: `fab build`
- to run the app `python manage.py runserver 0.0.0.0:8000` (also in other terminal)
- to deploy: `fab deploy:staging,backend=0`
- control-d do exit the machine
- `vagrant halt` to stop the machine



### Python

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
    gem install compass


### NodeJS


Nvm:

    curl https://raw.githubusercontent.com/creationix/nvm/v0.10.0/install.sh | bash
    nvm install 1.10.20
    cd frontend
    npm install -g grunt-cli
    npm install -g bower
    npm install

When all the above is done, to start developing, activate the local develpment
environment:

	source ./activate.sh


### Local develpment environment for frontend testing

A stripped-down version of the backend environment, using sqlite.

Bootstrapping:

    pip install -r requirements/test.txt
    python manage.py syncdb --settings=xdimension_web.settings.test --noinput
    python manage.py migrate --all --settings=xdimension_web.settings.test --noinput

Load initial data

    python manage.py loaddata xdimension_web/fixtures/test_data.json --settings=xdimension_web.settings.test

Download bower dependencies and apply local patches (must be run only once):

    fab dep


Build the app:

    fab build:test

Now the views are in ``xdimension_web/xdw_web/templates/frontend``

Run the app:

    python manage.py runserver --settings=xdimension_web.settings.test


For the admin go to ``http://localhost:8000/en/admin/`` (username: admin, password: admin)


### Local full development environment

Install other services and libraries: ``postgresql``, ``memcache``, ``libmemcached-dev``, ``libevent``, ...

Create postgres db and user account:

    fab create_db_local

Bootstrapping:

    pip install -r requirements/dev.txt
    python manage.py syncdb
    python manage.py migrate --all
    fab dep

Run the app:

    fab build
    python manage.py runserver



## Random notes

Set default site name from the admin web console.

AngularJS html views are served by the django backend as and rendered as
django templates. The `fab build` task integrates the fontend views into the django project as templates. All angular variables syntax (`{`) is escaped by the
build sstem using `{% verbatim %}`; if you really want to use django template
variables in angular vies, use this supernice syntax: `{dj{ variable_name }dj}`.


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
    heroku addons:add heroku-postgresql:dev --version=9.3 --app xdiscovery-web-staging
    heroku addons:add memcachier:dev -a xdiscovery-web-staging
    heroku addons:add sendgrid:starter -a xdiscovery-web-staging
    heroku addons:add logentries:tryit -a xdiscovery-web-staging
    # (optional ssl protection)
    heroku addons:add ssl -a xdiscovery-web-staging
    heroku certs:add 28056cc8200751.crt gd_bundle-g2.crt host.key -a xdiscovery-web-staging

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

To run the frontend standalone, execute `grunt server` in the `frontend`
directory
