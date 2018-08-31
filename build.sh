# Build the environment used on the servers.
#!/usr/bin/env bash

set -e -x

DIR="$(dirname "$(readlink -f "$0")")"
DIR_VENV="$DIR/venv"
CMD_INSTALL="pip install -i https://devpi.corp.withings.com/root/prod/+simple/ --upgrade"

rm -rf $DIR_VENV
virtualenv -p python3 $DIR_VENV
. $DIR_VENV/bin/activate
$CMD_INSTALL pip wheel virtualenv virtualenv-relocate setuptools

cd $DIR
$CMD_INSTALL -e .

virtualenv --relocatable $DIR_VENV
virtualenv-relocate $DIR_VENV
