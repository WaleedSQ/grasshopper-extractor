cmake_minimum_required(VERSION 3.15)

# Try to find a C compiler, but don't fail if none is found yet
project(gh_components_c_tests C)

set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)

# Add include directories
include_directories(${CMAKE_CURRENT_SOURCE_DIR}/c_components)
include_directories(${CMAKE_CURRENT_SOURCE_DIR}/wiring)

# Collect component sources
file(GLOB COMPONENT_SRCS "${CMAKE_CURRENT_SOURCE_DIR}/c_components/*.c")

# Collect test sources
file(GLOB TEST_SRCS "${CMAKE_CURRENT_SOURCE_DIR}/tests/*.c")

# Collect wiring sources (excluding demo_main.c as it's the entry point)
file(GLOB WIRING_SRCS 
    "${CMAKE_CURRENT_SOURCE_DIR}/wiring/*.c"
)
# Remove demo_main.c from the glob, we'll add it explicitly to the executable
list(REMOVE_ITEM WIRING_SRCS "${CMAKE_CURRENT_SOURCE_DIR}/wiring/demo_main.c")

# Define the test executable
add_executable(run_tests
    ${COMPONENT_SRCS}
    ${TEST_SRCS}
)

# Define the wiring demo executable
add_executable(demo_main
    ${COMPONENT_SRCS}
    ${WIRING_SRCS}
    ${CMAKE_CURRENT_SOURCE_DIR}/wiring/demo_main.c
)

# Link math library on non-MSVC compilers (for fabsf, etc.)
if(NOT MSVC)
    target_link_libraries(run_tests m)
    target_link_libraries(demo_main m)
endif()

# Provide helpful message if no compiler is found
if(NOT CMAKE_C_COMPILER)
    message(WARNING "No C compiler found. Please install one of:")
    message(WARNING "  - MinGW-w64 (gcc)")
    message(WARNING "  - LLVM (clang)")
    message(WARNING "  - Microsoft Visual C++ Build Tools (cl)")
    message(WARNING "")
    message(WARNING "Or specify a compiler when running cmake:")
    message(WARNING "  cmake -DCMAKE_C_COMPILER=gcc ..")
    message(WARNING "  cmake -DCMAKE_C_COMPILER=clang ..")
endif()

