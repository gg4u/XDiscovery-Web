import os
import subprocess
import re

from fabric.api import local, task, abort, puts
from fabric.contrib import django

django.project('xdimension_web')

YES_VALUES = ('1', 'true', 'yes')

BACKUP_DIR = './backups'
BACKUP_PATH = os.path.join(BACKUP_DIR, 'pgdump.db')

# Needed for Ubuntu multi-tenant setup.
# NOTE: this has to match with the db specified in local settings.
DB_CLUSTER = '9.2/main'


def run_sql(sql):
    '''Used for admin commands locally.'''
    return subprocess.check_call(
        ['bash', '-c', 'sudo -u postgres psql --cluster {cluster} -c '
         '"{sql}"'.format(cluster=DB_CLUSTER, sql=sql)])


def get_db_config():
    from django.conf import settings
    return settings.DATABASES['default']


@task
def deploy(env='staging', frontend='True', backend='True'):
    local('python manage.py xdw_web_build')

    if env == 'local':
        local('python manage.py collectstatic --noinput '
              '--settings=xdimension_web.settings.local')
    elif env == 'staging':
        if frontend.lower() in YES_VALUES:
            local('./run_in_env .env python manage.py collectstatic --noinput '
                  '--settings=xdimension_web.settings.local_s3"')
        if backend.lower() in YES_VALUES:
            # XXX this is not good for production:
            #  - Push of backend code into production API host should happen
            #  *after* db migration.
            #  - Db migration should happen in a separate utility heroku app
            local('git push xdimension_web-staging master')
            local('heroku run python manage.py migrate --all --noinput')
    else:
        assert False


@task
def test():
    local('python manage.py test  ')


@task
def backup(app='xdimension_web-staging'):
    if not os.path.exists(BACKUP_DIR):
        puts('Creating default backup dir {}'.format(BACKUP_DIR))
        os.mkdir(BACKUP_DIR)
    puts('Capturing heroku backup...')
    out = subprocess.check_output(
        ['heroku', 'pgbackups:capture', '-e', '--app', app])
    backup_no = re.search('backup--->\s*(\w+)', out, re.MULTILINE)
    if not backup_no:
        abort('can\'t find backup number from heroku pgbackups:capture output')
    backup_no = backup_no.group(1)
    puts('Getting backup url from heroku...')
    out = subprocess.check_output(['heroku', 'pgbackups:url', backup_no,
                                   '--app', app])
    backup_url = out.strip()
    if not backup_url:
        abort('can\'t find backup url from heroku pgbackups:url output')
    puts('Downloading postgres backup...')
    subprocess.check_call(['wget', '-q', '-O', BACKUP_PATH, backup_url],
                          stdout=subprocess.PIPE)
    puts('Backup OK in {}'.format(BACKUP_PATH))


@task
def backup_local():
    if not os.path.exists(BACKUP_DIR):
        puts('Creating default backup dir {}'.format(BACKUP_DIR))
        os.mkdir(BACKUP_DIR)
    puts('Capturing local backup...')
    db_config = get_db_config()
    subprocess.check_call(['bash', '-c',
                           'PGPASSWORD={PASSWORD} pg_dump -n public '
                           '--cluster {cluster} '
                           '-O -x -U {USER} -h localhost -p {PORT} '
                           '-f {path} {NAME}'.format(path=BACKUP_PATH,
                                                     cluster=DB_CLUSTER,
                                                     **db_config)])


@task
def create_db_local(drop=False, create_role=False, test=False):
    db_config = get_db_config()
    if drop:
        answer = raw_input('Dropping db. Are you sure? (yes/no) ')
        if answer.lower() != 'yes':
            puts('Abandoning')
            return
        puts('Dropping database...')
        run_sql("drop database {NAME};".format(**db_config))
    if create_role:
        puts('Creating role...')
        run_sql("create role {USER} {createdb};".format(
                createdb='with createdb' if test else '',
                **db_config))
    run_sql("create database {NAME} with ENCODING 'UTF8' "
            "LC_COLLATE='it_IT.UTF8' LC_CTYPE='it_IT.UTF8' "
            "template=template0 owner={USER};".format(**db_config))


@task
def restore_local():
    '''Tested on an ubuntu machine.'''
    create_db_local(drop=True, test=True)
    db_config = get_db_config()
    subprocess.check_call(['bash', '-c',
                           'PGPASSWORD={PASSWORD} pg_restore -n public '
                           '--cluster {cluster} -d {NAME} '
                           '-O -x -U {USER} -h localhost -p {PORT} '
                           '{path}'.format(path=BACKUP_PATH,
                                           cluster=DB_CLUSTER,
                                           **db_config)])


@task
def restore(app='xdimension_web-staging'):
    '''Tested on an ubuntu machine.'''
    puts('To restore the heroku db:')
    puts(' 1) make the db dump accessible from an https url <url>')
    puts(' 2) heroku pgbackups:restore DATABASE_URL <url> -a <app_name>')


@task
def setup_python():
    # install python
    #local('pyenv install 2.7.5')
    # activate local pyenv
    #local('pyenv local 2.7.5 && pyenv rehash')
    # install virtualenv & setuptools
    #local('pip install "virtualenv<1.10"')
    # create virtual environment (old-school like heroku's)
    local('virtualenv --distribute virtual')
    # activate virtualenv
    local('source virtual/bin/activate')
    # install python packages
    local('pip install -r requirements/dev.txt')


@task
def setup_environment(what='all'):
    if what in ('python', 'all'):
        setup_python()


@task
def env_to_heroku(fname='.env'):
    chunks = []
    with open(fname) as f:
        for l in f.readlines():
            if re.match('^\s*[a-zA-Z0-9]*.*=', l):
                chunks.append(l.strip())
    print u' '.join(chunks)