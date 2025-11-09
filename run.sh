#!/bin/bash
# ASM Scanner - Quick Run Script for Linux/Mac

set -e

DOMAIN=""
THREADS=10
DEBUG=""

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -d|--domain)
            DOMAIN="$2"
            shift 2
            ;;
        -t|--threads)
            THREADS="$2"
            shift 2
            ;;
        --debug)
            DEBUG="--debug"
            shift
            ;;
        -h|--help)
            echo "Usage: ./run.sh -d <domain> [-t threads] [--debug]"
            echo ""
            echo "Options:"
            echo "  -d, --domain    Target domain (required)"
            echo "  -t, --threads   Number of threads (default: 10)"
            echo "  --debug         Enable debug logging"
            echo "  -h, --help      Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

if [ -z "$DOMAIN" ]; then
    echo "Error: Domain is required"
    echo "Usage: ./run.sh -d <domain> [-t threads] [--debug]"
    exit 1
fi

echo "Building ASM Scanner Docker image..."
docker-compose build

echo ""
echo "Starting ASM scan for domain: $DOMAIN"
echo "Threads: $THREADS"
echo ""

docker-compose run --rm asm-scanner -d "$DOMAIN" -t "$THREADS" $DEBUG

echo ""
echo "Scan complete! Results are in ./results/$DOMAIN/"
