@echo off
setlocal
echo =======================================
echo Compiling Tiny C Web Server
echo =======================================

REM Überprüfen, ob gcc verfügbar ist
where gcc >nul 2>nul
if %errorlevel%==0 (
    echo [FOUND] GCC Compiler
    echo Compiling with gcc...
    gcc server.c -o server.exe -lws2_32 -O3 -Wall
    if %errorlevel%==0 (
        echo [SUCCESS] server.exe created successfully!
        exit /b 0
    ) else (
        echo [ERROR] GCC build failed.
        exit /b 1
    )
)

REM Überprüfen, ob clang verfügbar ist
where clang >nul 2>nul
if %errorlevel%==0 (
    echo [FOUND] Clang Compiler
    echo Compiling with clang...
    clang server.c -o server.exe -lws2_32 -O3
    if %errorlevel%==0 (
        echo [SUCCESS] server.exe created successfully!
        exit /b 0
    ) else (
        echo [ERROR] Clang build failed.
        exit /b 1
    )
)

REM Überprüfen, ob cl.exe schon im PATH ist
where cl >nul 2>nul
if %errorlevel%==0 goto :compile_msvc

REM Try to find vcvars64.bat and set up environment if cl is not in path
echo [SEARCH] Looking for Visual Studio installation...
set "VS_PATH="
if exist "%ProgramFiles(x86)%\Microsoft Visual Studio\Installer\vswhere.exe" (
    for /f "usebackq tokens=*" %%i in (`"%ProgramFiles(x86)%\Microsoft Visual Studio\Installer\vswhere.exe" -latest -property installationPath`) do (
      set "VS_PATH=%%i"
    )
)

if defined VS_PATH (
    if exist "%VS_PATH%\VC\Auxiliary\Build\vcvars64.bat" (
        echo [FOUND] Visual Studio at %VS_PATH%
        echo Setting up VS Environment...
        call "%VS_PATH%\VC\Auxiliary\Build\vcvars64.bat" >nul
        goto :compile_msvc
    )
)

echo [ERROR] No suitable C compiler (gcc, clang, cl) found in PATH.
echo Please install one or open the "Developer Command Prompt" for Visual Studio to use cl.exe.
exit /b 1

:compile_msvc
echo [FOUND] MSVC Compiler
echo Compiling with cl.exe...
cl /nologo /W3 /O2 /MD server.c ws2_32.lib /link /out:server.exe
if %errorlevel%==0 (
    echo [SUCCESS] server.exe created successfully!
    del server.obj >nul 2>nul
    exit /b 0
) else (
    echo [ERROR] MSVC build failed.
    exit /b 1
)
