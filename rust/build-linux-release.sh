#!/bin/bash

cargo build --all --release
mv ./target/release/libchannel_sound.so ../cm_channels/channel_sound.so
mv ./target/release/libchannel_world.so ../cm_channels/channel_world.so
mv ./target/release/libcm_gen.so ../cm_generation/cm_gen.so
