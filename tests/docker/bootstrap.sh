#!/bin/bash
set -e

echo "Starting restore procedure..."

# this is hardcoded in `cruise-config.xml`.
PASSWORD_PATH=/var/lib/go-server/

if [ -f "/sbin/my_init" ]
then
    INIT_SCRIPT=/sbin/my_init

    WORKING_PATH=/var/lib/go-server/
    CONFIG_PATH=/etc/go/
    ARTIFACTS_PATH=${WORKING_PATH}/artifacts/
    CONFIG_REPO_PATH=${WORKING_PATH}/db/config.git/
    H2DB_PATH=${WORKING_PATH}/db/h2db/
    PLUGINS_PATH=${WORKING_PATH}/plugins/external/
elif [ -f "/docker-entrypoint.sh" ]
then
    INIT_SCRIPT=/docker-entrypoint.sh

    WORKING_PATH=/go-working-dir/
    CONFIG_PATH=${WORKING_PATH}/config/
    ARTIFACTS_PATH=${WORKING_PATH}/artifacts/
    CONFIG_REPO_PATH=${WORKING_PATH}/db/config.git/
    H2DB_PATH=${WORKING_PATH}/db/h2db/
    PLUGINS_PATH=${WORKING_PATH}/plugins/external/
else
  echo "Unknown docker image!"
  exit 1
fi

mkdir -p ${WORKING_PATH} ${CONFIG_PATH} ${ARTIFACTS_PATH} ${CONFIG_REPO_PATH} ${H2DB_PATH} ${PLUGINS_PATH} ${PASSWORD_PATH}
cp *.zip /tmp

cp passwd ${PASSWORD_PATH}
unzip -o -d ${CONFIG_PATH} /tmp/config-dir.zip
unzip -o -d ${ARTIFACTS_PATH} /tmp/artifacts.zip
unzip -o -d ${CONFIG_REPO_PATH} /tmp/config-repo.zip
unzip -o -d ${H2DB_PATH} /tmp/db.zip

# install some plugin, required for some API calls
cp github-pr-poller-1.2.4.jar ${PLUGINS_PATH}
cp docker-elastic-agents-0.6.1.jar ${PLUGINS_PATH}

chown -R go:go ${WORKING_PATH} ${CONFIG_PATH} ${ARTIFACTS_PATH} ${CONFIG_REPO_PATH} ${H2DB_PATH} ${PLUGINS_PATH}

# run init script
${INIT_SCRIPT}
