
#!/usr/bin/env bash
set -e

if ! command -v nginx >/dev/null 2>&1; then
    apt-get update
    DEBIAN_FRONTEND=noninteractive apt-get install -y nginx
fi

mkdir -p /data/web_static/releases/test
mkdir -p /data/web_static/shared

cat > /data/web_static/releases/test/index.html <<'HTML'
<html>
  <head></head>
  <body>School</body>
</html>
HTML

if [ -e /data/web_static/current ] &&
   [ ! -L /data/web_static/current ]; then
    echo "current exists but is not a symbolic link" >&2
    exit 1
fi

rm -f /data/web_static/current
ln -s /data/web_static/releases/test /data/web_static/current

chown -R ubuntu:ubuntu /data
chmod 755 /data /data/web_static
chmod 755 /data/web_static/releases

python3 - <<'PY'
from pathlib import Path
import re

path = Path("/etc/nginx/sites-available/default")
config = path.read_text()

# Remove an existing simple hbnb_static location block.
config = re.sub(
    r"(?ms)^[ \t]*location[ \t]+/hbnb_static/?"
    r"[ \t]*\{[^{}]*\}[ \t]*\n?",
    "",
    config
)

match = re.search(r"(?m)^[ \t]*server[ \t]*\{", config)
if match is None:
    raise RuntimeError("No Nginx server block found")

location = """
    location /hbnb_static/ {
        alias /data/web_static/current/;
    }
"""

config = (
    config[:match.end()]
    + location
    + config[match.end():]
)
path.write_text(config)
PY

nginx -t
systemctl restart nginx || service nginx restart

exit 0
