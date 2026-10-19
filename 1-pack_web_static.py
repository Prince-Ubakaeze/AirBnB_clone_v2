#!/usr/bin/python3
"""Create a compressed archive of web_static."""
from datetime import datetime
import os
from shlex import quote

from fabric.api import local, settings


def do_pack():
    """Return a timestamped web_static archive path, or None on failure."""
    if not os.path.isdir("web_static"):
        print("Packing failed: run from the repo containing web_static/.")
        return None

    archive_path = "versions/web_static_{}.tgz".format(
        datetime.now().strftime("%Y%m%d%H%M%S"))
    if os.path.exists(archive_path):
        print("Packing failed: timestamp exists; retry in one second.")
        return None

    try:
        with settings(warn_only=True, abort_exception=RuntimeError):
            if local("mkdir -p versions").failed:
                return None
            print("Packing web_static to {}".format(archive_path))
            result = local("tar -czf {} web_static".format(
                quote(archive_path)))
            if result.failed:
                if os.path.isfile(archive_path):
                    os.remove(archive_path)
                return None
        if not os.path.isfile(archive_path):
            return None
        print("web_static packed: {} -> {} Bytes".format(
            archive_path, os.path.getsize(archive_path)))
        return archive_path
    except Exception as error:
        print("Packing failed: {}".format(error))
        return None
