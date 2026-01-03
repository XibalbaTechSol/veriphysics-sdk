#!/bin/bash
# VeriPhysics Dependency Installer
# Installs CMake, build tools, and OpenCV development libraries.

set -e

echo "[VeriPhysics] Updating package lists..."
sudo apt-get update

echo "[VeriPhysics] Installing build dependencies (CMake, g++, OpenCV)..."
# libopencv-dev includes headers and libraries needed for the C++ Core
sudo apt-get install -y build-essential cmake libopencv-dev

echo "[VeriPhysics] Installation complete."
echo "You can now build the C++ core by running:"
echo "  cd cpp_core && mkdir -p build && cd build && cmake .. && make"
