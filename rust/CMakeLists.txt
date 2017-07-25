cmake_minimum_required(VERSION 3.7)
project(rust)

set(CMAKE_CXX_STANDARD 11)

set(SOURCE_FILES
        include/libcm.h
        libcm/__init__.py
        src/ksum.rs
        src/lib.rs
        build.py
        Cargo.toml
        LICENSE
        setup.py)

add_executable(rust ${SOURCE_FILES})