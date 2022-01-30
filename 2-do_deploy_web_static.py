#!/usr/bin/python3
'''fabric script for task 2 0X03'''

from fabric.api import local, put, run, env
from fabric.decorators import runs_once
from datetime import datetime
import re
from os import path


env.hosts = [
    '35.196.185.163',
    '34.75.166.190'
]


@runs_once
def do_pack():
    '''generates a .tgz archive from the contents of the web_static folder'''
    local("mkdir -p versions")
    result = local("tar -cvzf versions/web_static_{}.tgz web_static"
                   .format(datetime.strftime(datetime.now(), "%Y%m%d%H%M%S")),
                   capture=True)

    if result.failed:
        return None
    return result


def do_deploy(archive_path):
    '''distributes an archive to my web servers'''
    if not path.exists(archive_path):
        return False

    file_name = re.search(r'versions/(\S+).tgz', archive_path)
    if file_name is None:
        return False
    file_name = file_name.group(1)
    res = put(local_path=archive_path, remote_path="/tmp/{}.tgz"
              .format(file_name))
    if res.failed:
        return False

    res = run("mkdir -p /data/web_static/releases/{}".format(file_name))
    if res.failed:
        return False

    res = run("tar -xzf /tmp/{}.tgz -C /data/web_static/releases/{}/"
              .format(file_name, file_name))
    if res.failed:
        return False

    res = run('rm -rf /tmp/{}.tgz'.format(file_name))
    if res.failed:
        return False

    res = run(('mv /data/web_static/releases/{}/web_static/* ' +
              '/data/web_static/releases/{}/')
              .format(file_name, file_name))
    if res.failed:
        return False

    res = run('rm -rf /data/web_static/releases/{}/web_static'
              .format(file_name))
    if res.failed:
        return False

    res = run('rm -rf /data/web_static/current')
    if res.failed:
        return False

    res = run('ln -s /data/web_static/releases/{}/ /data/web_static/current'
              .format(file_name))
    if res.failed:
        return False

    print('New version deployed!')
    return True
