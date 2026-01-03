cmake_minimum_required(VERSION 3.10)
project(VeriPhysicsCore)

set(CMAKE_CXX_STANDARD 17)

# Finding OpenCV
find_package(OpenCV REQUIRED)

include_directories(${OpenCV_INCLUDE_DIRS})

# Main Library
add_library(veriphysics_core SHARED
    MotionVerifier.cpp
    MotionVerifier.h
)
target_link_libraries(veriphysics_core ${OpenCV_LIBS})

# CLI Test Executable
add_executable(vp_cli main.cpp)
target_link_libraries(vp_cli veriphysics_core ${OpenCV_LIBS})

# NOTE: For Android NDK build, we will need a separate configuration or valid toolchain file.
# This setup is primarily for local Linux development/testing.
