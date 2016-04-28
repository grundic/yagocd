#!/bin/bash
set -e

echo "Starting restore procedure..."

mkdir -p /var/lib/go-server/db/h2db
mkdir -p /var/lib/go-server/db/config.git

unzip artifacts.zip -d /tmp

unzip -o -d /var/lib/go-server/db/h2db /tmp/artifacts/serverBackups/backup_20160427-061149/db.zip
unzip -o -d /etc/go/ /tmp/artifacts/serverBackups/backup_20160427-061149/config-dir.zip
unzip -o -d /var/lib/go-server/db/config.git /tmp/artifacts/serverBackups/backup_20160427-061149/config-repo.zip

chown -R go:go /var/lib/go-server/ /etc/go/

/sbin/my_init
