
#!/usr/bin/python3
"""Pack the web_static directory into a compressed archive."""

import os
from datetime import datetime

from fabric.api import local, settings


def do_pack():
    """Create and return a compressed web_static archive."""
    if not os.path.isdir("web_static"):
        return None

    if not os.path.isdir("versions"):
        os.makedirs("versions")

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    archive_path = "versions/web_static_{}.tgz".format(timestamp)

    with settings(warn_only=True):
        result = local(
            "tar -czf {} web_static".format(archive_path),
            capture=True
        )

    if result.failed or not os.path.isfile(archive_path):
        return None

    return archive_path
