
#!/usr/bin/python3
"""Deploy a web_static archive to the web servers."""

import os
import re

from fabric.api import env, put, run, settings

env.hosts = [
    "YOUR_WEB01_PUBLIC_IP",
    "YOUR_WEB02_PUBLIC_IP"
]


def do_deploy(archive_path):
    """Deploy archive and return whether deployment succeeded."""
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
