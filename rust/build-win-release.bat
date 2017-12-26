cargo build --all --release
copy target\release\channel_sound.dll ..\cm_channels\channel_sound.pyd
copy target\release\channel_world.dll ..\cm_channels\channel_world.pyd
::copy target\release\cm_gen.dll ..\cm_generation\cm_gen.pyc
