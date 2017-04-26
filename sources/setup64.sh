#!/bin/bash

python3 ./setup64.py build_ext --inplace

rm ../libs/cm_accelerate.cpython-35m-x86_64-linux-gnu.so
cp ./cm_accelerate.cpython-35m-x86_64-linux-gnu.so ../libs/cm_accelerate.cpython-35m-x86_64-linux-gnu.so

rm ../cm_compileBrain.cpython-35m-x86_64-linux-gnu.so
cp ./cm_compileBrain.cpython-35m-x86_64-linux-gnu.so ../cm_compileBrain.cpython-35m-x86_64-linux-gnu.so
