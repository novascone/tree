
cmake_minimum_required(VERSION 3.28)
project(TREE)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)
if (NOT DEFINED ENV{BLENDER_PATH})
   message(FATAL_ERROR "BLENDER_PATH not set")
endif()
file(GLOB _python_bins "$ENV{BLENDER_PATH}/*/python/bin/python3*")
list(FILTER _python_bins EXCLUDE REGEX "\\.py$")
list(GET _python_bins 0 _python_exe)
set(Python3_EXECUTABLE ${_python_exe} CACHE STRING "Blender Python")
include(FetchContent)
FetchContent_Declare(
   pybind11
   GIT_REPOSITORY https://github.com/pybind/pybind11
   GIT_TAG v3.0.4
)
FetchContent_MakeAvailable(pybind11)
find_package(HDF5 REQUIRED COMPONENTS C)
find_package(netCDF REQUIRED)
set(CMAKE_BUILD_TYPE Debug)
pybind11_add_module(tree_core core/bindings.cpp core/build_mesh.cpp core/read.cpp core/interp.cpp core/driver.cpp)
target_include_directories(tree_core PRIVATE core/integration)
target_link_libraries(tree_core PRIVATE HDF5::HDF5 netCDF::netcdf)
target_compile_options(tree_core PRIVATE -Wall -Wextra -g)
