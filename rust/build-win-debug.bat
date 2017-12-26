cargo build --all
copy target\debug\channel_sound.dll ..\cm_channels\channel_sound.pyd
copy target\debug\channel_world.dll ..\cm_channels\channel_world.pyd
::copy target\debug\cm_gen.dll ..\cm_generation\cm_gen.pyd
