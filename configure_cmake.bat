@echo off
setlocal

REM Add CMake to PATH if it exists in common location
if exist "C:\Program Files\CMake\bin" (
    set "PATH=%PATH%;C:\Program Files\CMake\bin"
)

REM This script helps configure CMake with the right generator and compiler

echo Configuring CMake build...

REM Try to detect available compiler and set appropriate generator
set CMAKE_GENERATOR=
set CMAKE_CC=

REM Check for MinGW (gcc)
where gcc >nul 2>&1
if %errorlevel% == 0 (
    echo Found GCC compiler
    set CMAKE_CC=gcc
    set CMAKE_GENERATOR=MinGW Makefiles
    goto :configure
)

REM Check for Clang
where clang >nul 2>&1
if %errorlevel% == 0 (
    echo Found Clang compiler
    set CMAKE_CC=clang
    set CMAKE_GENERATOR=MinGW Makefiles
    goto :configure
)

REM Check for MSVC (cl)
where cl >nul 2>&1
if %errorlevel% == 0 (
    echo Found MSVC compiler
    set CMAKE_CC=cl
    set CMAKE_GENERATOR=NMake Makefiles
    goto :configure
)

REM No compiler found
echo.
echo ========================================
echo WARNING: No C compiler found in PATH
echo ========================================
echo.
echo Please install one of the following:
echo.
echo   1. MinGW-w64 (Recommended for Windows)
echo      Download: https://www.mingw-w64.org/downloads/
echo      - Install and add bin folder to PATH
echo      - Example: C:\mingw-w64\mingw64\bin
echo.
echo   2. LLVM/Clang
echo      Download: https://github.com/llvm/llvm-project/releases
echo      - Install Windows installer
echo      - Add to PATH: C:\Program Files\LLVM\bin
echo.
echo   3. Visual Studio Build Tools
echo      Download: https://visualstudio.microsoft.com/downloads/
echo      - Install "Desktop development with C++" workload
echo      - Run from "Developer Command Prompt"
echo.
echo After installing, close and reopen this terminal, then run this script again.
echo.
echo Alternatively, you can use the batch script which may find compilers
echo in non-standard locations: .\build_tests.bat
echo.
pause
exit /b 1

:configure
REM Create build directory
if not exist build mkdir build
cd build

REM Configure CMake
if defined CMAKE_CC (
    echo Running: cmake -G "%CMAKE_GENERATOR%" -DCMAKE_C_COMPILER=%CMAKE_CC% ..
    cmake -G "%CMAKE_GENERATOR%" -DCMAKE_C_COMPILER=%CMAKE_CC% ..
) else (
    echo Running: cmake -G "%CMAKE_GENERATOR%" ..
    cmake -G "%CMAKE_GENERATOR%" ..
)

if errorlevel 1 (
    echo.
    echo CMake configuration failed.
    echo.
    echo Please install one of:
    echo   - MinGW-w64 (gcc) - https://www.mingw-w64.org/
    echo   - LLVM (clang) - https://llvm.org/
    echo   - Microsoft Visual C++ Build Tools (cl)
    echo.
    echo After installing, add the compiler to your PATH and run this script again.
    exit /b 1
)

echo.
echo CMake configuration successful!
echo.
echo To build, run:
echo   cmake --build . --config Debug
echo.
echo Or from the project root:
echo   cmake --build build --config Debug
endlocal

