
#!/usr/bin/python3
"""Pack and deploy web_static to both servers."""

import os
import re
from datetime import datetime

from fabric.api import env, local, put, run, settings

env.hosts = [
    "YOUR_WEB01_PUBLIC_IP",
    "YOUR_WEB02_PUBLIC_IP"
]


def do_pack():
    """Create a compressed archive of web_static."""
    if not os.path.isdir("web_static"):
        return None

    if not os.path.isdir("versions"):
        os.makedirs("versions")

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    archive_path = "versions/web_static_{}.tgz".format(
        timestamp
    )

    with settings(warn_only=True):
        result = local(
            "tar -czf {} web_static".format(archive_path),
            capture=True
        )

    if result.failed or not os.path.isfile(archive_path):
        return None

    return archive_path


def do_deploy(archive_path):
    """Deploy the given archive to the current server."""
    if not os.path.isfile(archive_path):
        return False

    archive_name = os.path.basename(archive_path)

    if not archive_name.endswith(".tgz"):
        return False

    release_name = archive_name[:-4]

    if not re.fullmatch(r"[A-Za-z0-9_.-]+", release_name):
        return False

    remote_archive = "/tmp/{}".format(archive_name)
    release_dir = "/data/web_static/releases/{}".format(
        release_name
    )

    commands = [
        "mkdir -p {}".format(release_dir),
        "tar -xzf {} --strip-components=1 -C {}".format(
            remote_archive, release_dir
        ),
        "rm -f {}".format(remote_archive),
        "rm -f /data/web_static/current",
        "ln -s {} /data/web_static/current".format(
            release_dir
        )
    ]

    try:
        with settings(warn_only=True):
            upload = put(archive_path, remote_archive)
            if upload.failed:
                return False

            for command in commands:
                result = run(command)
                if result.failed:
                    return False

        return True

    except Exception:
        return False


def deploy():
    """Pack the application and deploy the archive."""
    archive_path = do_pack()

    if archive_path is None:
        return False

    return do_deploy(archive_path)
