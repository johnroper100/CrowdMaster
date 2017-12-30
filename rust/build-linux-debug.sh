#!/bin/bash

cargo build --all
cp ./target/debug/libchannel_path.so ../cm_channels/channel_path.so
cp ./target/debug/libchannel_world.so ../cm_channels/channel_world.so
