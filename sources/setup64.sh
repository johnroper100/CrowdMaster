#!/bin/bash

python3 ./setup64.py build_ext --inplace

rm ../cm_nodeFunctions.cpython-35m-x86_64-linux-gnu.so
cp ./cm_nodeFunctions.cpython-35m-x86_64-linux-gnu.so ../cm_nodeFunctions.cpython-35m-x86_64-linux-gnu.so

rm ../cm_channels/cm_soundAccel.cpython-35m-x86_64-linux-gnu.so
cp ./cm_soundAccel.cpython-35m-x86_64-linux-gnu.so ../cm_channels/cm_soundAccel.cpython-35m-x86_64-linux-gnu.so
