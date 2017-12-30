cargo build --all --release
copy target\release\channel_path.dll ..\cm_channels\channel_path.pyd
copy target\release\channel_world.dll ..\cm_channels\channel_world.pyd