#!/bin/bash

cd ./channel_world
cargo rustc --features "cpython/python3-sys" --release -- -C link-arg="-undefined" -C link-arg="dynamic_lookup"
cd ../channel_sound
cargo rustc --features "cpython/python3-sys" --release -- -C link-arg="-undefined" -C link-arg="dynamic_lookup"
cd ..

mv ./target/release/libchannel_sound.dylib ../cm_channels/channel_sound.so
mv ./target/release/libchannel_world.dylib ../cm_channels/channel_world.so
