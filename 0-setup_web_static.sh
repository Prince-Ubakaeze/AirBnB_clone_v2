#!/usr/bin/env bash
# Prepare an Ubuntu web server for AirBnB web_static deployments.
# The assignment requires exit status 0 even on failure; read stderr and test HTTP.
set -Eeuo pipefail

site=/etc/nginx/sites-available/default
snippet=/etc/nginx/snippets/airbnb_web_static.conf
backup_dir=
config_changed=false
snippet_existed=false
setup_succeeded=false
keep_backup=false

cleanup() {
    # Restore the previous Nginx files if validation or restart failed.
    if [[ "$setup_succeeded" != true ]]; then
        printf 'ERROR: web_static setup did not complete. See errors above.\n' >&2
        if [[ "$config_changed" == true && -n "$backup_dir" ]]; then
            restore_ok=true
            cp -p -- "$backup_dir/default" "$site" || restore_ok=false
            if [[ "$snippet_existed" == true ]]; then
                cp -p -- "$backup_dir/snippet" "$snippet" || restore_ok=false
            else
                rm -f -- "$snippet" || restore_ok=false
            fi
            if [[ "$restore_ok" == true ]]; then
                printf 'Previous Nginx files restored; inspect nginx status.\n' >&2
            else
                keep_backup=true
                printf 'ERROR: rollback failed; backups remain in %s.\n' "$backup_dir" >&2
            fi
        fi
    fi
    if [[ -n "$backup_dir" && "$keep_backup" != true ]]; then
        rm -f -- "$backup_dir/default" "$backup_dir/snippet" \
            "$backup_dir/new-default" || true
        rmdir -- "$backup_dir" || true
    fi
    # Required by task 0, including when a command above has failed.
    exit 0
}
trap cleanup EXIT
trap 'printf "ERROR: command failed at line %s.\n" "$LINENO" >&2' ERR

if [[ "$EUID" -ne 0 ]]; then
    printf 'ERROR: run this script with sudo.\n' >&2
    exit 1
fi

if ! command -v nginx >/dev/null 2>&1; then
    apt-get update
    DEBIAN_FRONTEND=noninteractive apt-get install -y nginx
fi

mkdir -p /data/web_static/releases/test /data/web_static/shared
cat > /data/web_static/releases/test/index.html <<'HTML'
<!DOCTYPE html>
<html lang="en">
  <head><meta charset="utf-8"><title>AirBnB web_static</title></head>
  <body><h1>School</h1><p>web_static setup is working.</p></body>
</html>
HTML
chmod 755 /data /data/web_static /data/web_static/releases \
    /data/web_static/releases/test /data/web_static/shared
chmod 644 /data/web_static/releases/test/index.html

if [[ -e /data/web_static/current && ! -L /data/web_static/current ]]; then
    printf 'ERROR: /data/web_static/current exists and is not a symlink.\n' >&2
    exit 1
fi
# -T prevents following an existing symlink to a directory; -f replaces it.
ln -sfnT /data/web_static/releases/test /data/web_static/current
chown -R ubuntu:ubuntu /data

if [[ ! -f "$site" || ! -e /etc/nginx/sites-enabled/default ]]; then
    printf 'ERROR: expected the standard enabled Ubuntu Nginx default site.\n' >&2
    printf 'Enable that site or adapt this script for your custom virtual host.\n' >&2
    exit 1
fi

mkdir -p /etc/nginx/snippets
backup_dir=$(mktemp -d)
cp -p -- "$site" "$backup_dir/default"
if [[ -e "$snippet" ]]; then
    snippet_existed=true
    cp -p -- "$snippet" "$backup_dir/snippet"
fi

# Preserve existing routes and settings. Add the include only once.
if grep -Eq '^[[:space:]]*include[[:space:]]+/etc/nginx/snippets/airbnb_web_static\.conf[[:space:]]*;' "$site"; then
    cp -p -- "$site" "$backup_dir/new-default"
else
    awk '
        { print }
        !added && /^[[:space:]]*server[[:space:]]*\{/ {
            print "    include /etc/nginx/snippets/airbnb_web_static.conf;"
            added = 1
        }
        END { if (!added) exit 1 }
    ' "$site" > "$backup_dir/new-default"
fi

config_changed=true
cat > "$snippet" <<'NGINX'
# Managed by 0-setup_web_static.sh.
location = /hbnb_static {
    return 301 /hbnb_static/;
}
location /hbnb_static/ {
    alias /data/web_static/current/;
    index index.html;
}
NGINX
cat "$backup_dir/new-default" > "$site"
nginx -t
service nginx restart
setup_succeeded=true
printf 'web_static setup completed. Test: curl -f http://localhost/hbnb_static/index.html\n'
exit 0
