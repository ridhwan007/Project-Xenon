# Quick Start Guide

Get started with the ASM Scanner in 3 simple steps!

## Prerequisites

- Docker Desktop installed and running
- 4GB+ RAM available
- Internet connection

## Quick Start

### Windows Users

1. **Build the image:**
   ```powershell
   docker-compose build
   ```

2. **Run a scan:**
   ```powershell
   .\run.bat -d example.com
   ```

3. **View results:**
   ```powershell
   cd results\example.com
   dir
   ```

### Linux/Mac Users

1. **Build the image:**
   ```bash
   docker-compose build
   ```

2. **Run a scan:**
   ```bash
   chmod +x run.sh
   ./run.sh -d example.com
   ```

3. **View results:**
   ```bash
   cd results/example.com
   ls -la
   ```

### Using Make (Linux/Mac)

```bash
# Build
make build

# Run scan
make run DOMAIN=example.com

# Run with custom threads
make run DOMAIN=example.com THREADS=20

# Open shell in container
make shell
```

## Understanding the Output

After a scan completes, you'll find organized results:

```
results/
└── example.com/
    └── 20250109_143022/
        ├── 00_summary.json          # Scan statistics
        ├── 01_subfinder.txt         # Discovered subdomains
        ├── 03_massdns_resolved.txt  # Valid subdomains
        ├── 04_dnsx_recon.json       # DNS details
        ├── 05_nmap_scan.xml         # Port scan results
        ├── 06_httpx_probe.json      # HTTP fingerprints
        └── screenshots/             # Website screenshots
```

## Common Commands

### Basic Scan
```bash
docker-compose run --rm asm-scanner -d target.com
```

### Fast Scan (More Threads)
```bash
docker-compose run --rm asm-scanner -d target.com -t 20
```

### Debug Mode
```bash
docker-compose run --rm asm-scanner -d target.com --debug
```

### Custom Output Directory
```bash
docker-compose run --rm asm-scanner -d target.com -o /asm/results/custom
```

## Analyzing Results

### View Summary
```bash
# Windows
type results\example.com\[timestamp]\00_summary.json

# Linux/Mac
cat results/example.com/[timestamp]/00_summary.json
```

### Count Subdomains
```bash
# Windows
type results\example.com\[timestamp]\03_massdns_resolved.txt | Measure-Object -Line

# Linux/Mac
wc -l results/example.com/[timestamp]/03_massdns_resolved.txt
```

### View Live URLs
```bash
# Windows
type results\example.com\[timestamp]\live_urls.txt

# Linux/Mac
cat results/example.com/[timestamp]/live_urls.txt
```

## Troubleshooting

### Build fails?
```bash
docker-compose build --no-cache
```

### Permission denied on run.sh?
```bash
chmod +x run.sh
```

### Container exits immediately?
Check that you provided a domain:
```bash
docker-compose run --rm asm-scanner --help
```

## Next Steps

1. Review the full [README.md](README.md) for advanced usage
2. Configure API keys in `.env` for better results
3. Customize the workflow in `asm_scanner.py`
4. Set up automated scans with cron/Task Scheduler

## Legal Notice

⚠️ **Important**: Only scan domains you own or have explicit permission to test. Unauthorized scanning may be illegal in your jurisdiction.

## Need Help?

- Check the full documentation: [README.md](README.md)
- Review the configuration: [config/README.md](config/README.md)
- Open an issue if you find bugs
