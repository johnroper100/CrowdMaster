#!/bin/bash

cargo build --all
mv ./target/debug/libchannel_path.so ../cm_channels/channel_path.so
