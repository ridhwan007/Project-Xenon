# ASM Scanner - Project Structure

```
ASM/
│
├── asm_scanner.py          # Main Python orchestration script
├── Dockerfile              # Docker image definition (Kali Linux base)
├── docker-compose.yml      # Docker Compose configuration
├── requirements.txt        # Python dependencies
├── Makefile               # Build automation (Linux/Mac)
├── run.sh                 # Quick run script (Linux/Mac)
├── run.bat                # Quick run script (Windows)
│
├── README.md              # Full documentation
├── QUICKSTART.md          # Quick start guide
├── PROJECT_STRUCTURE.md   # This file
│
├── .env.example           # Example environment variables
├── .gitignore            # Git ignore rules
├── .dockerignore         # Docker ignore rules
│
├── config/               # Configuration directory
│   └── README.md         # Config documentation
│
├── results/              # Scan results (created at runtime)
│   └── [domain]/
│       └── [timestamp]/
│           ├── 00_summary.json
│           ├── 01_subfinder.txt
│           ├── 02_alterx.txt
│           ├── 03_massdns_resolved.txt
│           ├── 04_dnsx_recon.json
│           ├── 05_nmap_scan.xml
│           ├── 05_nmap_scan.txt
│           ├── 06_httpx_probe.json
│           ├── live_urls.txt
│           └── screenshots/
│
└── tools.csv             # Tool reference list
```

## File Descriptions

### Core Files

- **asm_scanner.py**: Main Python script that orchestrates the entire workflow
  - Handles subdomain discovery (subfinder)
  - Generates permutations (alterx)
  - Resolves domains (massdns)
  - Performs DNS recon (dnsx)
  - Scans ports (nmap)
  - Probes HTTP (httpx)
  - Captures screenshots (gowitness)
  - Generates summary reports

- **Dockerfile**: Builds the scanning environment
  - Base: Kali Linux Rolling
  - Installs all Go-based tools from ProjectDiscovery
  - Compiles MassDNS from source
  - Sets up Python environment
  - Configures networking and permissions

- **docker-compose.yml**: Simplified container management
  - Handles volume mounts
  - Configures network mode (host)
  - Manages environment variables
  - Enables privileged mode for raw sockets

### Configuration

- **requirements.txt**: Python dependencies (minimal, mostly stdlib)
- **.env.example**: Template for API keys (Chaos, Shodan, etc.)
- **config/**: Directory for tool-specific configurations
  - Subfinder provider configs
  - Custom DNS resolvers
  - Nmap custom scripts

### Automation Scripts

- **run.sh**: Bash script for Linux/Mac users
  - Simplified command-line interface
  - Builds image and runs scan
  - Argument parsing

- **run.bat**: Batch script for Windows users
  - Same functionality as run.sh
  - Windows-compatible syntax

- **Makefile**: Build automation for Linux/Mac
  - `make build`: Build Docker image
  - `make run DOMAIN=x`: Run scan
  - `make shell`: Open container shell
  - `make clean`: Clean up results

### Documentation

- **README.md**: Comprehensive documentation
  - Installation instructions
  - Usage examples
  - Configuration guide
  - Troubleshooting

- **QUICKSTART.md**: Get started quickly
  - 3-step setup
  - Common commands
  - Result interpretation

- **PROJECT_STRUCTURE.md**: This file
  - Project organization
  - File descriptions

## Workflow Architecture

```
User Input (Domain)
        ↓
┌───────────────────┐
│  asm_scanner.py   │ ← Main orchestrator
└───────────────────┘
        ↓
┌───────────────────┐
│   Subfinder       │ → 01_subfinder.txt
└───────────────────┘
        ↓
┌───────────────────┐
│   Alterx          │ → 02_alterx.txt
└───────────────────┘
        ↓
┌───────────────────┐
│   MassDNS         │ → 03_massdns_resolved.txt
└───────────────────┘
        ↓
┌───────────────────┐
│   DNSX            │ → 04_dnsx_recon.json
└───────────────────┘
        ↓
┌───────────────────┐
│   Nmap            │ → 05_nmap_scan.xml/txt
└───────────────────┘
        ↓
┌───────────────────┐
│   HTTPx           │ → 06_httpx_probe.json
└───────────────────┘
        ↓
┌───────────────────┐
│   Gowitness       │ → screenshots/*.png
└───────────────────┘
        ↓
┌───────────────────┐
│   Summary Report  │ → 00_summary.json
└───────────────────┘
```

## Data Flow

1. **Input**: Domain name via CLI
2. **Discovery**: Passive subdomain enumeration
3. **Expansion**: Generate subdomain variations
4. **Validation**: Mass DNS resolution
5. **Reconnaissance**: DNS record collection
6. **Scanning**: Port and service detection
7. **Probing**: HTTP fingerprinting
8. **Capture**: Visual documentation
9. **Output**: Structured results in multiple formats

## Tool Integration

### External Tools (in Docker)
- subfinder (Go)
- alterx (Go)
- massdns (C)
- dnsx (Go)
- nmap (C/C++)
- httpx (Go)
- gowitness (Go)

### Python Script
- Orchestrates tool execution
- Manages data flow between tools
- Handles error recovery
- Generates reports
- Provides logging

## Extension Points

To add new functionality:

1. Add tool to `Dockerfile` (install step)
2. Create new step method in `asm_scanner.py`
3. Call method in `run()` workflow
4. Update documentation

Example: Adding nuclei scanning
```python
def step8_nuclei(self):
    """Step 8: Vulnerability scanning using nuclei"""
    cmd = ["nuclei", "-list", str(self.live_urls_file), ...]
    return self.run_command(cmd, "Nuclei vulnerability scan")
```

## Security Considerations

- **Privileged mode**: Required for nmap SYN scans
- **Network access**: Host network mode for better performance
- **Data storage**: Results may contain sensitive information
- **API keys**: Store in .env, never commit to version control

## Performance Tuning

Adjust these parameters for better performance:

1. **Threads**: `-t 20` for faster parallel processing
2. **Network mode**: `host` mode reduces network overhead
3. **Resource limits**: Allocate more RAM to Docker
4. **Resolvers**: Use fast, reliable DNS resolvers for massdns

## Maintenance

Regular updates:
```bash
# Rebuild with latest tool versions
make rebuild

# Update base image
docker pull kalilinux/kali-rolling:latest
```
