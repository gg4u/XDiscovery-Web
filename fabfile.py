import os
import subprocess
import re
import shutil
import sys

from fabric.api import local, task, abort, puts, lcd
from fabric.contrib import django


# Configuration
APP_NAME = 'xdiscovery-web'
# Needed for Ubuntu multi-tenant setup.
# NOTE: this has to match with the db specified in local settings.
DB_CLUSTER = '9.1/main'

sys.path.insert(0, '.')
django.project('xdimension_web')

YES_VALUES = ('1', 'true', 'yes')

BACKUP_DIR = './backups'
BACKUP_PATH = os.path.join(BACKUP_DIR, 'pgdump.db')



def run_sql(sql):
    '''Used for admin commands locally.'''
    return subprocess.check_call(
        ['bash', '-c', 'sudo -u postgres psql --cluster {cluster} -c '
         '"{sql}"'.format(cluster=DB_CLUSTER, sql=sql)])


def get_db_config():
    from django.conf import settings
    return settings.DATABASES['default']


def get_app_name(environment):
    return '{}-{}'.format(APP_NAME, environment) if environment != 'production' \
        else APP_NAME

@task
def build(dest='dist'):
    with lcd('frontend'):
        local('grunt build{}'.format('test' if dest == 'test' else ''))
    # Remove useless files
    if dest == 'test':
        for d in ['bootstrap-sass/examples',
                  'foundation/docs',
                  'json3/vendor']:
            shutil.rmtree(os.path.join('frontend/dist/bower_components', d))
    integrate_assets()


@task
def deploy(env='staging', frontend='True', backend='True'):
    if env == 'local':
        pass
    elif env == 'staging':
        if frontend.lower() in YES_VALUES:
            local('{}/run_in_env.sh .env-staging python manage.py '
                  'collectstatic --noinput '
                  '--settings=xdimension_web.settings.local_s3'
                  .format(os.getcwd()))
        if backend.lower() in YES_VALUES:
            # XXX this is not good for production:
            #  - Push of backend code into production API host should happen
            #  *after* db migration.
            #  - Db migration should happen in a separate utility heroku app
            app = get_app_name(env)
            local('git push {} master'.format(app))
            local('heroku run python manage.py migrate --all --noinput --app {}'
                  .format(app))
    else:
        assert False


@task
def test():
    local('python manage.py test xdw_web xdw_core')


@task
def backup(env='staging'):
    app = get_app_name(env)
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
    # If this fails try
    #    sudo locale-gen it_IT.UTF-8
    # ... and restart db server
    run_sql("create database {NAME} with ENCODING 'UTF-8' "
            "LC_COLLATE='it_IT.UTF-8' LC_CTYPE='it_IT.UTF-8' "
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
def restore(env='staging'):
    app = get_app_name(env)
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


@task
def integrate_assets():
    ''' Puts some of the frontend html assets in django project.

    There they will be served directly by the application layer with the
    usual django templating system.
    '''
    dst_dir = os.path.abspath(
        os.path.join('xdimension_web', 'xdw_web', 'templates', 'frontend') )
    src_dir = os.path.join('.', 'frontend', 'dist')
    if not os.path.exists(os.path.join(dst_dir, 'views')):
        os.makedirs(os.path.join(dst_dir, 'views'))
    # Store source_file, dest_file in this list
    files = [('index.html', os.path.join(dst_dir, 'index.html'))]
    prev_cwd = os.getcwd()
    try:
        os.chdir(src_dir)
        for path in os.listdir('views'):
            if (os.path.isfile(os.path.join('views', path)) and
                path.endswith('.html')):
                files.append((os.path.join('views', path),
                              os.path.join(dst_dir, 'views', path)))
        for src_path, dst_path in files:
            with open(src_path, 'rb') as src_f, open(dst_path, 'wb') as dst_f:
                data = src_f.read()
                # Protect angular vars from django template machinery
                data, n = re.subn(r'({{.*?}})',
                                  r'{% verbatim %}\1{% endverbatim %}',
                                  data)
                # Decode *real* django vars
                data, n = re.subn(r'{dj{(.*?)}dj}',
                                  r'{{\1}}',
                                  data)
                # Prepend django static url logic to all assets
                data, n = re.subn(
                    r'(href="|src=")/(bower_components|scripts|styles|images)',
                    r'\1{{ STATIC_URL }}frontend/\2', data)
                dst_f.write(data)
    finally:
        os.chdir(prev_cwd)
    puts('Integrated {} files into django app'.format(len(files)))
