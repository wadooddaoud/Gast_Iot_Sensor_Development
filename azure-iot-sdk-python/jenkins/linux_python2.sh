#!/bin/bash
# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for full license information.

build_root=$(cd "$(dirname "$0")/.." && pwd)
cd $build_root

# -- Python C wrapper --
./build_all/linux/build.sh $*
[ $? -eq 0 ] || exit $?

python2 ./device/tests/iothub_client_e2e.py
[ $? -eq 0 ] || exit $?

python2 ./service/tests/iothub_service_client_e2e.py
[ $? -eq 0 ] || exit $?

