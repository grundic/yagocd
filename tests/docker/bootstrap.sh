#!/bin/bash
set -e

echo "Starting restore procedure..."

mkdir -p /var/lib/go-server/db/h2db
mkdir -p /var/lib/go-server/db/config.git

cp *.zip /tmp

unzip -o -d /var/lib/go-server/db/h2db /tmp/db.zip
unzip -o -d /etc/go/ /tmp/config-dir.zip
unzip -o -d /var/lib/go-server/db/config.git /tmp/config-repo.zip
unzip -o -d /var/lib/go-server/artifacts /tmp/artifacts.zip

cp passwd /var/lib/go-server/

chown -R go:go /var/lib/go-server/ /etc/go/

/sbin/my_init
