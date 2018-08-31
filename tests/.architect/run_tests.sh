# Script called by Architect to run the tests.
#!/usr/bin/env bash

set -e -x

DIR="$(dirname "$(readlink -f "$0")")"
cd "$(dirname "$(dirname $DIR)" )"

# Sometimes the VM does not have the place to have all environments at once
# so we have to delete them before using a new one.
for ENV in "flake8" "py35"; do
    ./run tox -e "$ENV"
    rm -rf ".tox/$ENV"
done
