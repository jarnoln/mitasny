# Usage:
# Localhost:
# fab -f deploy_tools/fabfile.py provision:host=jln@localhost
# fab -f deploy_tools/fabfile.py deploy:host=jln@localhost

import time
from fabric.contrib.files import append, exists, sed
from fabric.api import env, local, run, settings, abort


REPO_URL = 'https://github.com/jarnoln/mitasny.git'
SITE_NAME = 'mitasny.com'  # Not yet the actual server name


def deploy():
    # site_folder = '/home/%s/sites/%s' % (env.user, env.host)
    site_folder = '/home/%s/sites/%s' % (env.user, SITE_NAME)
    source_folder = site_folder + '/source'
    virtualenv = site_folder + '/virtualenv'
    python = virtualenv + '/bin/python'
    pip = virtualenv + '/bin/pip'
    app_list = ['tasks']
    _run_local_unit_tests(app_list)
    _init_virtualenv(site_folder)
    _get_latest_source(source_folder)
    _update_python_libraries(source_folder, pip)
    _run_remote_unit_tests(app_list, source_folder, python)


def _init_virtualenv(site_folder):
    if not exists(site_folder + '/virtualenv'):
        run('cd %s && virtualenv virtualenv' % site_folder)


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


def _run_remote_unit_tests(app_list, source_folder, python):
    print('*** Run remote unit tests')
    for app in app_list:
        run('cd %s && %s manage.py test %s --settings=mitasny.settings' % (source_folder, python, app))
