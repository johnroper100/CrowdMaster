#!/bin/bash

cd ./channel_world
cargo rustc --features "cpython/python3-sys" -- -C link-arg="-undefined" -C link-arg="dynamic_lookup"
cd ../channel_sound
cargo rustc --features "cpython/python3-sys" -- -C link-arg="-undefined" -C link-arg="dynamic_lookup"
cd ../cm_gen
cargo rustc --features "cpython/python3-sys" -- -C link-arg="-undefined" -C link-arg="dynamic_lookup"
cd ..

mv ./target/debug/libchannel_sound.dylib ../cm_channels/channel_sound.so
mv ./target/debug/libchannel_world.dylib ../cm_channels/channel_world.so
mv ./target/debug/libcm_gen.dylib ../cm_generation/cm_gen.so
