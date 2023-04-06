from fabric.api import env, run, put
from os.path import exists
from datetime import datetime

env.hosts = ['<IP web-01>', '<IP web-02>']
env.user = 'ubuntu'  # Replace with your username
env.key_filename = 'my_ssh_private_key'  # Replace with the path to your SSH private key

def do_pack():
    """Generates a compressed archive of the web_static folder."""
    try:
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        local('mkdir -p versions')
        local('tar -czf versions/web_static_{}.tgz web_static'.format(timestamp))
        return 'versions/web_static_{}.tgz'.format(timestamp)
    except Exception as e:
        return None

def do_deploy(archive_path):
    """Distributes an archive to the web servers."""
    if not exists(archive_path):
        return False

    try:
        archive_filename = archive_path.split('/')[-1]
        archive_no_ext = archive_filename.split('.')[0]
        releases_path = '/data/web_static/releases'
        current_path = '/data/web_static/current'
        put(archive_path, '/tmp/{}'.format(archive_filename))
        run('mkdir -p {}/{}'.format(releases_path, archive_no_ext))
        run('tar -xzf /tmp/{} -C {}/{}'.format(archive_filename, releases_path, archive_no_ext))
        run('rm /tmp/{}'.format(archive_filename))
        run('mv {}/{}/web_static/* {}/{}'.format(releases_path, archive_no_ext, releases_path, archive_no_ext))
        run('rm -rf {}/{}/web_static'.format(releases_path, archive_no_ext))
        run('rm -rf {}'.format(current_path))
        run('ln -s {}/{}/ {}'.format(releases_path, archive_no_ext, current_path))
        return True
    except Exception as e:
        return False

def deploy():
    """Deploys an archive to the web servers."""
    archive_path = do_pack()
    if archive_path is None:
        return False
    return do_deploy(archive_path)

