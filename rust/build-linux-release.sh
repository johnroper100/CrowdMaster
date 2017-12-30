#!/bin/bash

cargo build --all --release
cp ./target/release/libchannel_path.so ../cm_channels/channel_path.so
cp ./target/release/libchannel_world.so ../cm_channels/channel_world.so