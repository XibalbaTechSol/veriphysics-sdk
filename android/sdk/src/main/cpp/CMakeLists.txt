cmake_minimum_required(VERSION 3.18.1)

project("veriphysics_sdk")

find_package(OpenCV REQUIRED)

add_library( # Sets the name of the library.
             veriphysics_sdk

             # Sets the library as a shared library.
             SHARED

             # Provides a relative path to your source file(s).
             native-lib.cpp
             MotionVerifier.cpp )

target_link_libraries( # Specifies the target library.
                       veriphysics_sdk
                       
                       # Links OpenCV
                       ${OpenCV_LIBS}

                       # Links the target library to the log library
                       # included in the NDK.
                       log )
