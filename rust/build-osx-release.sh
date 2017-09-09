#!/bin/bash

cargo build --all --release
mv ./target/release/libchannel_sound.dylib ../cm_channels/channel_sound.dylib
mv ./target/release/libchannel_world.dylib ../cm_channels/channel_world.dylib
