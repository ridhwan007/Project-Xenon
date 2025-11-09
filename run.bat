@echo off
REM ASM Scanner - Quick Run Script for Windows

setlocal enabledelayedexpansion

set DOMAIN=
set THREADS=10
set DEBUG=

:parse_args
if "%~1"=="" goto check_domain
if /i "%~1"=="-d" (
    set DOMAIN=%~2
    shift
    shift
    goto parse_args
)
if /i "%~1"=="--domain" (
    set DOMAIN=%~2
    shift
    shift
    goto parse_args
)
if /i "%~1"=="-t" (
    set THREADS=%~2
    shift
    shift
    goto parse_args
)
if /i "%~1"=="--threads" (
    set THREADS=%~2
    shift
    shift
    goto parse_args
)
if /i "%~1"=="--debug" (
    set DEBUG=--debug
    shift
    goto parse_args
)
if /i "%~1"=="-h" goto show_help
if /i "%~1"=="--help" goto show_help

echo Unknown option: %~1
goto show_help

:check_domain
if "%DOMAIN%"=="" (
    echo Error: Domain is required
    echo.
    goto show_help
)

echo Building ASM Scanner Docker image...
docker-compose build

echo.
echo Starting ASM scan for domain: %DOMAIN%
echo Threads: %THREADS%
echo.

docker-compose run --rm asm-scanner -d %DOMAIN% -t %THREADS% %DEBUG%

echo.
echo Scan complete! Results are in .\results\%DOMAIN%\
goto end

:show_help
echo Usage: run.bat -d ^<domain^> [-t threads] [--debug]
echo.
echo Options:
echo   -d, --domain    Target domain (required)
echo   -t, --threads   Number of threads (default: 10)
echo   --debug         Enable debug logging
echo   -h, --help      Show this help message
exit /b 1

:end
endlocal
