#!/bin/bash

cargo build --all --release
mv ./target/release/libchannel_path.so ../cm_channels/channel_path.so
