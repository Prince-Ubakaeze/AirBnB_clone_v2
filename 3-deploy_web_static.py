#!/usr/bin/python3
"""Create one archive and deploy it to both configured hosts."""
from datetime import datetime
import os
from shlex import quote

from fabric.api import env, local, put, run, runs_once, settings

# Replace these placeholders with the two actual server IP addresses.
env.hosts = ["<IP web-01>", "<IP web-02>"]


@runs_once
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


def do_deploy(archive_path):
    """Deploy an archive on the current Fabric host; return success."""
    if not os.path.isfile(archive_path):
        print("Deployment failed: archive does not exist.")
        return False
    if not env.host_string or "<" in env.host_string:
        print("Deployment failed: configure both server IPs first.")
        return False

    filename = os.path.basename(archive_path)
    release_name, extension = os.path.splitext(filename)
    if extension != ".tgz" or release_name in ("", ".", ".."):
        print("Deployment failed: expected a named .tgz archive.")
        return False

    upload = "/tmp/" + filename
    release = "/data/web_static/releases/" + release_name
    current = "/data/web_static/current"
    try:
        with settings(warn_only=True, abort_exception=RuntimeError):
            # An existing release is never extracted over a live website.
            if run("test ! -e {0} && test ! -L {0}".format(
                    quote(release))).failed:
                print("Deployment failed: release exists; pack a new one.")
                return False
            if put(archive_path, upload, use_glob=False).failed:
                return False
            commands = [
                "mkdir -p {}".format(quote(release)),
                "tar -xzf {} -C {} --strip-components=1".format(
                    quote(upload), quote(release)),
                "rm -f {}".format(quote(upload)),
                "chmod -R a+rX {}".format(quote(release)),
                # rm -f refuses a real directory; never recursively delete it.
                "rm -f {}".format(quote(current)),
                "ln -s {} {}".format(quote(release), quote(current)),
            ]
            for command in commands:
                if run(command).failed:
                    print("Deployment failed on {}.".format(env.host_string))
                    return False
        print("New version deployed on {}!".format(env.host_string))
        return True
    except Exception as error:
        print("Deployment failed: {}".format(error))
        return False


def deploy():
    """Pack once per fab invocation and deploy on each configured host."""
    archive_path = do_pack()
    if archive_path is None:
        return False
    return do_deploy(archive_path)
