# Script called by the Withings deployer after the project has been built
# by architect.
#!/usr/bin/env bash

set -e -x

ENV=$1
SRV=$2

DIR="$(dirname "$(readlink -f "$0")")"
RUN=${DIR}/run

cd $DIR

WORKERS=$(find ${DIR}/scripts/ -name 'worker*' -type f -exec basename {} \; | tr '\n' ' ' )

if test -n "$WORKERS"
then
	echo "• Killing workers: $WORKERS"
	$RUN dsci-kill-workers $WORKERS
	echo "✓ Done."
fi

if test -n "$(find $DIR/alembic/versions -name '*.py')"
then
	echo "• Checking for database upgrades…"
	$RUN alembic upgrade head
	echo "✓ Done."
fi

for file in `find $DIR -name '*.wsgi'`
# -> reload_webservice
do
	echo "• Touching $file"
	touch $file;
done
