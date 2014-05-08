import os
from fabric.api import local, cd, run, settings, env, prefix

DEPLOYMENTS = {
    'prod': {
        'virtual_env': '/home/ubuntu/.virtualenvs/composting_prod',
        'project_dir': '/home/ubuntu/WBComposting',
        'host_string': 'ubuntu@compost.ona.io',
        'alembic_section': 'production'
    },
    'dev': {
        'virtual_env': '/home/vagrant/.virtualenvs/composting_dev',
        'project_dir': '/home/vagrant/WBComposting',
        'host_string': 'vagrant@192.168.33.15'
    }
}


def deploy(deployment="prod", branch="master"):
    env.update(DEPLOYMENTS[deployment])
    virtual_env_command = 'source {}'.format(
        os.path.join(env.virtual_env, 'bin', 'activate'))
    with cd(env.project_dir):
        run("git checkout {branch}".format(branch=branch))
        run("git pull origin {branch}".format(branch=branch))
        run('find . -name "*.pyc" -exec rm -rf {} \;')

        # run migrations
        with prefix(virtual_env_command):
            run("python setup.py test -q")
            run("pip install -r requirements.txt")
            run("python setup.py install")
            run("alembic -n {0} upgrade head".format(
                env.get('alembic_section', 'alembic')))

    # Reload uWSGI
    run("/usr/local/bin/uwsgi --reload /var/run/WBComposting.pid")
