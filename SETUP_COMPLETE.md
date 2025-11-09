# ASM Tool - Setup Complete! 🎉

Your Attack Surface Management (ASM) tool is ready to use!

## What Has Been Created

✅ **Core Components**
- `asm_scanner.py` - Main Python orchestration script (500+ lines)
- `Dockerfile` - Kali Linux-based container with all tools
- `docker-compose.yml` - Easy container management
- `requirements.txt` - Python dependencies

✅ **Automation Scripts**
- `run.sh` - Linux/Mac quick start script
- `run.bat` - Windows quick start script  
- `Makefile` - Build automation for Linux/Mac

✅ **Documentation**
- `README.md` - Complete documentation
- `QUICKSTART.md` - Fast setup guide
- `PROJECT_STRUCTURE.md` - Architecture overview
- `config/README.md` - Configuration guide

✅ **Configuration**
- `.env.example` - API key template
- `.gitignore` - Git ignore rules
- `.dockerignore` - Docker ignore rules
- `config/` - Configuration directory

## Workflow Overview

The tool implements this workflow:

1. **Subfinder** → Discover subdomains passively
2. **Alterx** → Generate subdomain permutations  
3. **MassDNS** → Resolve valid subdomains
4. **DNSX** → DNS reconnaissance with -recon flag
5. **Nmap** → Port scan web/sensitive ports with -sV
6. **HTTPx** → HTTP probing (-server, -td, -title, -sc, -cl)
7. **Gowitness** → Screenshot capture

## Quick Start

### Windows
```powershell
# Build the image
docker-compose build

# Run a scan
.\run.bat -d example.com

# View results
dir results\example.com
```

### Linux/Mac
```bash
# Build the image
docker-compose build

# Run a scan
chmod +x run.sh
./run.sh -d example.com

# View results
ls -la results/example.com
```

### Using Make (Linux/Mac)
```bash
make build
make run DOMAIN=example.com
```

## Features Implemented

✅ **Performance**
- Multi-threaded execution
- Parallel processing where possible
- Efficient data flow between tools

✅ **Output Management**
- Timestamped result directories
- JSON output for easy parsing
- XML output for Nmap
- Screenshot capture
- Summary statistics

✅ **Docker Integration**
- Kali Linux base image
- All tools pre-installed
- Host network mode
- Volume mounts for results
- Privileged mode for raw sockets

✅ **Tools Included**
- Subfinder (ProjectDiscovery)
- Alterx (ProjectDiscovery)
- MassDNS
- DNSX (ProjectDiscovery)
- Nmap
- HTTPx (ProjectDiscovery)
- Gowitness
- Nuclei (ProjectDiscovery) - bonus!

## Result Structure

After a scan, you'll get:
```
results/
└── example.com/
    └── 20250109_143022/
        ├── 00_summary.json          # Statistics
        ├── 01_subfinder.txt         # Discovered subdomains
        ├── 02_alterx.txt            # Permutations
        ├── 03_massdns_resolved.txt  # Valid domains
        ├── 04_dnsx_recon.json       # DNS details
        ├── 05_nmap_scan.xml         # Port scans
        ├── 06_httpx_probe.json      # HTTP info
        ├── live_urls.txt            # Live URLs
        └── screenshots/             # Screenshots
```

## Next Steps

1. **Build the image:**
   ```bash
   docker-compose build
   ```

2. **Run your first scan:**
   ```bash
   docker-compose run --rm asm-scanner -d example.com
   ```

3. **Configure API keys** (optional but recommended):
   - Copy `.env.example` to `.env`
   - Add your API keys for better subdomain discovery
   - Chaos API: https://chaos.projectdiscovery.io/
   - Shodan API: https://account.shodan.io/

4. **Review documentation:**
   - `QUICKSTART.md` - Get started quickly
   - `README.md` - Full documentation
   - `PROJECT_STRUCTURE.md` - Architecture details

## Command Examples

```bash
# Basic scan
docker-compose run --rm asm-scanner -d target.com

# Fast scan with 20 threads
docker-compose run --rm asm-scanner -d target.com -t 20

# Debug mode
docker-compose run --rm asm-scanner -d target.com --debug

# Custom output directory
docker-compose run --rm asm-scanner -d target.com -o /asm/results/custom

# Open shell in container
docker-compose run --rm --entrypoint /bin/bash asm-scanner
```

## Important Notes

⚠️ **Legal Notice**: Only scan domains you own or have explicit permission to test!

⚠️ **Performance**: First build takes 10-15 minutes (downloads and compiles tools)

⚠️ **Resources**: Ensure Docker has 4GB+ RAM allocated

⚠️ **Privileged Mode**: Required for nmap SYN scans (raw sockets)

## Troubleshooting

**Build fails?**
```bash
docker-compose build --no-cache
```

**Permission errors?**
```bash
# Linux/Mac
sudo chown -R $USER:$USER results/

# Windows PowerShell
takeown /f results /r /d y
```

**Need help?**
- Check `README.md` for detailed documentation
- Review `QUICKSTART.md` for common issues
- Verify Docker is running and has sufficient resources

## File Summary

| File | Purpose |
|------|---------|
| asm_scanner.py | Main orchestration script |
| Dockerfile | Container image definition |
| docker-compose.yml | Container management |
| run.sh / run.bat | Quick start scripts |
| Makefile | Build automation |
| README.md | Full documentation |
| QUICKSTART.md | Quick start guide |

## Tool Versions

All tools are installed at their latest versions:
- Subfinder: Latest from GitHub
- Alterx: Latest from GitHub
- MassDNS: Latest from source
- DNSX: Latest from GitHub
- Nmap: From Kali repos
- HTTPx: Latest from GitHub
- Gowitness: Latest from GitHub

## Happy Scanning! 🚀

Your ASM tool is production-ready. Start discovering your attack surface!

```bash
docker-compose build
docker-compose run --rm asm-scanner -d yourdomain.com
```

Good luck with your reconnaissance! 🔍
