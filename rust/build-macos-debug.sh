#!/bin/bash

cargo build --all
mv ./target/debug/libchannel_sound.dylib ../cm_channels/channel_sound.dylib
mv ./target/debug/libchannel_world.dylib ../cm_channels/channel_world.dylib
