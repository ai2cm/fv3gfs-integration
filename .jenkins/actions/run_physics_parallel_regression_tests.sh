#!/bin/bash
set -e -x
BACKEND=$1
EXPNAME=$2
export TEST_ARGS="-v -s -rsx --backend=${BACKEND} "

export TEST_DATA_HOST="${TEST_DATA_HOST}/physics/"
if [ ${python_env} == "virtualenv" ]; then
    CONTAINER_CMD="" make physics_savepoint_tests_mpi
else
    make physics_savepoint_tests_mpi
fi
