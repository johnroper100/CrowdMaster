#!/bin/bash

cargo build --all
mv ./target/debug/libchannel_sound.so ../cm_channels/channel_sound.so
mv ./target/debug/libchannel_world.so ../cm_channels/channel_world.so
