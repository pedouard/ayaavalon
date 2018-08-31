# /!\ THIS SCRIPT IS CALLED BY THE DEPLOYER ON THE TARGET SERVER(S) /!\
# Check out the README.md to know how to run the tests.
# Script called by the Withings deployer in order to execute tests on
# the machines hosting your project.
# To change the tests executed by Architect, check out
# tests/.architect/run_tests.sh
#!/usr/bin/env bash

set -e -x

env="$1"
hostname="$2"
DIR="$(dirname "$(readlink -f "$0")")"
cd "$(dirname $DIR)"

echo "THIS SCRIPT IS ONLY MEANT TO BE RUN BY THE DEPLOYER (see README.md)"
