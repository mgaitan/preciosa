from deployer.node import Node
from deployer.host import SSHHost


class PhasetyVPS(SSHHost):
    slug = 'phasetyvps'
    address = 'preciosdeargentina.com.ar'
    username = 'root'


class Preciosa(Node):

    class Hosts:
        host = PhasetyVPS

    # Location of the virtual env
    ip = '162.243.67.151'
    virtual_env_location = '/virtualenvs/preciosa'
    python = virtual_env_location + '/bin/python'
    pip = virtual_env_location + '/bin/pip'

    preciosa_project = '/projects/preciosa'
    project_logs = '/projects/preciosa/logs'

    def apt(self, packages, command='install'):
        self.hosts.run('sudo apt-get %s %s' % (command, packages))

    def get_log(self):
        with self.hosts.cd(self.project_logs):
            self.hosts.run('tail preciosa.log')

    def restart(self):
        self.hosts.run('sudo supervisorctl restart preciosa')
        self.hosts.run('sudo service nginx restart')

    def run_in_preciosa(self, command):
        with self.hosts.cd(self.preciosa_project):
            self.hosts.run(command)

    def shell_plus(self):
        self.django_command('shell_plus')

    def django_command(self, command):
        with self.hosts.cd(self.preciosa_project):
            self.hosts.run('%s manage.py %s' % (self.python, command))

    def pip_install(self, package, upgrade=False):
        command = "install --upgrade" if upgrade else "install"
        self.hosts.run('%s %s %s' % (self.pip, command, package))

    def pip_update(self):
        """update requirements.txt"""
        with self.hosts.cd(self.preciosa_project):
            self.hosts.run('%s install -r requirements/production.txt' % self.pip)

    def edit_local_settings(self):
        with self.hosts.cd(self.preciosa_project):
            self.hosts.run('vim preciosa/local_settings.py')
        self.restart()

    def debug(self, port='8000'):
        self.hosts.run('sudo supervisorctl stop preciosa')
        self.hosts.run('sudo service nginx stop')
        self.django_command('runserver %s:%s' % (self.ip, port))
        self.hosts.run('sudo service nginx start')
        self.hosts.run('sudo supervisorctl start preciosa')

    def dbbackup(self):
        self.django_command('dbbackup -z')

    def update(self, branch='develop'):
        with self.hosts.cd(self.preciosa_project):
            self.hosts.run('git fetch')
            self.hosts.run('git reset --hard origin/%s' % branch)

    def deploy(self, dbbackup=False, branch='develop'):
        self.update(branch)
        self.pip_update()
        if dbbackup:
            self.dbbackup()
        self.django_command('syncdb')
        self.django_command('migrate')
        self.django_command('collectstatic --noinput')
        self.restart()

if __name__ == '__main__':
    from deployer.client import start
    start(Preciosa)
