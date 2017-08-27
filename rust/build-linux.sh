#!/bin/bash

cargo build --all
mv ./target/debug/libchannel_sound.so ./target/debug/channel_sound.so
mv ./target/debug/libchannel_world.so ./target/debug/channel_world.so
