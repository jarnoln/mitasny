# Usage:
# Localhost:
# fab -f deploy_tools/fabfile.py deploy:host=username@localhost
# Live:
# fab -f deploy_tools/fabfile.py deploy:host=django@mitasny.com

from fabric.contrib.files import exists
from fabric.api import env, local, run, sudo
from fabric.network import ssh


REPO_URL = 'https://github.com/jarnoln/mitasny.git'
LOCAL_SITE_NAME = 'local.mitasny.com'  # Not yet the actual server name
ssh.util.log_to_file('fabric_ssh.log')


def get_site_name():
    if env.host == 'localhost' or env.host == '127.0.0.1':
        return LOCAL_SITE_NAME
    else:
        return env.host


def deploy():
    site_name = get_site_name()
    site_folder = '/home/%s/sites/%s' % (env.user, site_name)
    source_folder = site_folder + '/source'
    virtualenv = site_folder + '/virtualenv'
    python = virtualenv + '/bin/python'
    pip = virtualenv + '/bin/pip'
    app_list = ['tasks']
    # _run_local_unit_tests(app_list)
    _init_virtualenv(site_folder)
    _get_latest_source(source_folder)
    _update_python_libraries(source_folder, pip)
    _check_secret_key(source_folder, python)
    _update_database(source_folder, python)
    _run_remote_unit_tests(app_list, source_folder, python)
    # _restart_apache()
    _restart_nginx(site_name)


def _init_virtualenv(site_folder):
    if not exists(site_folder + '/virtualenv'):
        run('cd %s && virtualenv virtualenv' % site_folder)
    if not exists(site_folder + '/db'):
        run('cd %s && mkdir db' % site_folder)


def _run_local_unit_tests(app_list):
    print('*** Run local unit tests')
    # timestamp = time.strftime('%Y-%m-%d', time.localtime(time.time()))
    for app in app_list:
        local('python manage.py test %s --settings=mitasny.settings' % app)
        # coverage_file_name = '%s_%s_coverage.log' % (timestamp, app)
        # local('coverage run --source="./%s" manage.py test %s --settings=mitasny.settings' % (app, app))
        # local("coverage report | tee %s" % coverage_file_name)


def _get_latest_source(source_folder):
    if exists(source_folder + '/.git'):
        run('cd %s && git fetch' % source_folder)
    else:
        run('git clone %s %s' % (REPO_URL, source_folder))

    current_commit = local("git log -n 1 --format=%H", capture=True)
    run('cd %s && git reset --hard %s' % (source_folder, current_commit))


def _update_python_libraries(source_folder, pip):
    run('cd %s && %s install -r requirements.txt' % (source_folder, pip))


def _check_secret_key(source_folder, python):
    settings_folder = source_folder + '/mitasny'
    if not exists(settings_folder + '/secret_key.py'):
        run('cd %s && %s generate_secret.py > secret_key.py' % (settings_folder, python))


def _update_database(source_folder, python):
    run('cd %s && %s manage.py makemigrations' % (source_folder, python))
    run('cd %s && %s manage.py migrate' % (source_folder, python))


def _run_remote_unit_tests(app_list, source_folder, python):
    print('*** Run remote unit tests')
    for app in app_list:
        run('cd %s && %s manage.py test %s --settings=mitasny.settings' % (source_folder, python, app))


def _restart_apache():
    sudo('service apache2 restart')


def _restart_nginx(site_name):
    sudo('systemctl restart %s.gunicorn' % site_name)
    sudo('service nginx restart')
