# Project Xenon - Attack Surface Management Scanner

A comprehensive, automated Attack Surface Management tool that performs subdomain discovery, DNS reconnaissance, port scanning, and HTTP probing. Built with Docker for easy deployment and uses industry-standard security tools.

## Features

- **Live Subdomains Only**: Focuses on actually resolved, live subdomains (no dead/invalid domains)
- **Comprehensive Data Per Subdomain**: Each subdomain gets complete information in one place
- **Management Port Scanning**: Targets critical ports (SSH, RDP, FTP, databases, etc.)
- **Tech Stack Detection**: Identifies technologies, servers, and frameworks
- **SSL Certificate Analysis**: Extracts full certificate details including SANs
- **Clean JSON Output**: Single file with all results, easy to parse and analyze
- **Parallel Processing**: Multi-threaded for faster scanning
- **Reliable DNS Resolution**: Uses dnsx for accurate A/AAAA/CNAME resolution

## Workflow

```
Domain Input
    ↓
1. Subfinder (discover subdomains + parent domain)
    ↓
2. DNSX (resolve live subdomains only with A/AAAA/CNAME records)
    ↓
3. For each live subdomain in parallel:
   ├── Nmap (scan management ports: 21,22,25,3389,3306,5432,etc.)
   ├── HTTPx (get tech stack, server info, title, status)
   └── SSL Cert Info (extract certificate details)
    ↓
Single JSON Output (all data per subdomain)
```

## Output Format

For each live subdomain, you get comprehensive information in a single JSON file:

```json
{
  "subdomain": "www.example.com",
  "ips": ["1.2.3.4"],
  "ipv6": [],
  "cname": [],
  "open_ports": {
    "80/tcp": {
      "port": 80,
      "protocol": "tcp",
      "state": "open",
      "service": "http",
      "product": "nginx",
      "version": "1.18.0"
    },
    "443/tcp": {
      "port": 443,
      "protocol": "tcp",
      "state": "open",
      "service": "https",
      "product": "nginx",
      "version": "1.18.0"
    }
  },
  "http_info": {
    "https": {
      "url": "https://www.example.com",
      "status_code": 200,
      "title": "Example Domain",
      "server": "nginx/1.18.0",
      "tech": ["Nginx", "Ubuntu"],
      "content_length": 1256,
      "cdn": "cloudflare"
    }
  },
  "ssl_cert": {
    "subject": {"CN": "www.example.com"},
    "issuer": {"CN": "Let's Encrypt Authority"},
    "not_before": "Jan 1 00:00:00 2025 GMT",
    "not_after": "Apr 1 23:59:59 2025 GMT",
    "san": ["www.example.com", "example.com"]
  },
  "scan_time": "2025-11-09T14:30:22.123456"
}
```

## Prerequisites

- Docker
- Docker Compose (optional, but recommended)
- 4GB+ RAM recommended
- Disk space for results

## Installation

### Option 1: Using Docker Compose (Recommended)

1. Clone or download this repository:
```bash
cd c:\ASM
```

2. Build the Docker image:
```bash
docker-compose build
```

### Option 2: Using Docker directly

```bash
docker build -t asm-scanner:latest .
```

## Usage

### Using Docker Compose

```bash
# Basic scan
docker-compose run --rm asm-scanner -d example.com

# With custom threads
docker-compose run --rm asm-scanner -d example.com -t 20

# With debug logging
docker-compose run --rm asm-scanner -d example.com --debug

# Specify custom output directory
docker-compose run --rm asm-scanner -d example.com -o /asm/results/custom
```

### Using Docker directly

```bash
# Basic scan
docker run --rm -v ${PWD}/results:/asm/results --privileged --network host asm-scanner:latest -d example.com

# With options
docker run --rm -v ${PWD}/results:/asm/results --privileged --network host asm-scanner:latest -d example.com -t 20 --debug
```

### Command Line Arguments

```
usage: asm_scanner.py [-h] -d DOMAIN [-o OUTPUT] [-t THREADS] [--debug]

ASM Tool - Automated Attack Surface Management Scanner

options:
  -h, --help            show this help message and exit
  -d DOMAIN, --domain DOMAIN
                        Target domain to scan
  -o OUTPUT, --output OUTPUT
                        Output directory (default: results)
  -t THREADS, --threads THREADS
                        Number of threads for parallel operations (default: 10)
  --debug               Enable debug logging

Examples:
  asm_scanner.py -d example.com
  asm_scanner.py -d example.com -o /tmp/results -t 20
  asm_scanner.py -d example.com --debug
```

## Output Structure

Results are organized in a timestamped directory with simplified output:

```
results/
└── example.com/
    └── 20250109_143022/
        ├── scan_results.json    # Complete data for all live subdomains
        └── summary.json         # Scan statistics
```

### scan_results.json
Contains an array of subdomain objects, each with:
- **subdomain**: The domain/subdomain name
- **ips**: IPv4 addresses (A records)
- **ipv6**: IPv6 addresses (AAAA records)  
- **cname**: CNAME records
- **open_ports**: Nmap scan results with service versions
- **http_info**: HTTP/HTTPS probing results with tech stack
- **ssl_cert**: SSL certificate details (if HTTPS available)
- **scan_time**: Timestamp of the scan

### summary.json
Provides scan statistics:
- Total subdomains discovered
- Live subdomains count
- Unique IPs found
- Subdomains with open ports
- Subdomains with SSL certificates

## Configuration

### API Keys (Optional)

For enhanced subdomain discovery, you can configure API keys:

1. Create a `.env` file:
```bash
CHAOS_API_KEY=your_chaos_api_key_here
SHODAN_API_KEY=your_shodan_api_key_here
```

2. Subfinder will automatically use configured API keys from the container.

### Custom Resolver List

To use a custom resolver list for MassDNS, mount your resolvers file:

```bash
docker run -v ./resolvers.txt:/usr/share/massdns/lists/resolvers.txt -v ./results:/asm/results --privileged --network host asm-scanner:latest -d example.com
```

## Tools Included

| Tool | Version | Purpose |
|------|---------|---------|
| Subfinder | Latest | Passive subdomain discovery |
| DNSX | Latest | DNS resolution and reconnaissance |
| Nmap | Latest | Port scanning and service detection |
| HTTPx | Latest | HTTP probing and fingerprinting |
| Nuclei | Latest | Template-based vulnerability scanning (for future use) |
| Gowitness | Latest | Screenshot capture (for future use) |

## Performance Tips

1. **Adjust threads**: Use `-t 20` or higher for faster scanning on powerful systems
2. **Network mode**: The container uses `host` network mode for better performance
3. **Resource limits**: Ensure Docker has sufficient memory allocated (4GB+ recommended)
4. **Disk space**: Large scans can generate significant data; ensure adequate storage

## Security Considerations

- **Privileged mode**: Required for raw socket operations (nmap SYN scan)
- **Legal compliance**: Only scan domains you own or have explicit permission to test
- **Rate limiting**: Be mindful of rate limits on third-party APIs and services
- **Network impact**: Scanning generates significant network traffic

## Troubleshooting

### Container build fails
```bash
# Clean build with no cache
docker-compose build --no-cache
```

### Permission issues with results
```bash
# On Linux/Mac
sudo chown -R $USER:$USER results/

# On Windows (PowerShell)
takeown /f results /r /d y
```

### Nmap requires privileged mode
```bash
# Ensure --privileged flag is used
docker run --privileged ...
```

## Advanced Usage

### Running specific workflow steps

You can modify `asm_scanner.py` to run only specific steps by commenting out unwanted steps in the `run()` method.

### Integrating with CI/CD

```yaml
# Example GitHub Actions workflow
- name: Run ASM Scan
  run: |
    docker-compose run --rm asm-scanner -d ${{ secrets.TARGET_DOMAIN }}
    
- name: Upload Results
  uses: actions/upload-artifact@v3
  with:
    name: asm-results
    path: results/
```

## Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.

## License

This tool is provided as-is for educational and authorized security testing purposes only.

## Acknowledgments

- [ProjectDiscovery](https://github.com/projectdiscovery) for subfinder, dnsx, and httpx
- [Nmap](https://nmap.org/) for network scanning
