# xdiscovery_web

## Tools

Generate thumbnails:

	python manage.py xdw_core_generate_map_thumbnails

Rebuild seach engine:

	python manage.py xdw_core_restore_topics


## Development environment


### Setup virtualbox+vagrant developer environment

- install virtualbox
- install vagrant
- install sourcetree
- clone repo
- cd `dir_with_Vagrantfile`
- copy `.env-staging` and `.env-production` secret files to this folder
- vagrant up

Now access the vagrant machine:

    vagrant ssh


And configure heroku client:

    heroku login


## Common operations:

- make sure vagrant is up and you are in the dir with the Vagrantfile (see above)
- `vagrant ssh` to enter the Vagrant mahine
- make sure you are in the `/vagrant` dir (use `pwd` to find out)

To build the frontend app: `fab build`

To backup and restore db from heroku:

    fab backup:production
    fab restore_local

To run the backend and the frontend do:

    python manage.py runserver 0.0.0.0:8000

Then access it from a browser pointing to `http://127.0.0.1:8000


To deploy the frontend do:

    fab deploy:staging,backend=0

To deploy the frontend and backend do:

    fab deploy:staging

Hit control-d do exit the machine

Type `vagrant halt` to stop the machine


## Special management operations

To Rebuild the topic search tables do:

    python manage.py xdw_core_restore_topics

To generate (or ri-generate) map thumbnails run:

    python manage.py xdw_core_generate_map_thumbnails

Prefix the commands with `heroku run -a xdiscovery_web` to run on heroku.
Use `--help` flag for more details.


## Random notes

Set default site name from the admin web console.

AngularJS html views are served by the django backend as and rendered as
django templates. The `fab build` task integrates the fontend views into the django project as templates. All angular variables syntax (`{`) is escaped by the
build sstem using `{% verbatim %}`; if you really want to use django template
variables in angular vies, use this supernice syntax: `{dj{ variable_name }dj}`.


## Staging environment setup (only ever needed once)


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
