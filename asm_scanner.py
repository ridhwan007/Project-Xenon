#!/usr/bin/env python3
"""
ASM (Attack Surface Management) Tool
Simplified workflow: Live subdomains only with comprehensive info per subdomain
Output: IP, TechStack, Open Ports, SSL Cert Info in JSON format
"""

import subprocess
import json
import os
import sys
import argparse
import logging
import socket
import ssl
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Set, Optional
import tempfile

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


class ASMScanner:
    """Main ASM Scanner orchestrator - focused on live subdomains with comprehensive data"""
    
    def __init__(self, domain: str, output_dir: str = "results", threads: int = 20):
        self.domain = domain
        self.output_dir = Path(output_dir) / domain / datetime.now().strftime("%Y%m%d_%H%M%S")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.threads = threads
        
        # Output files
        self.results_file = self.output_dir / "scan_results.json"
        self.summary_file = self.output_dir / "summary.json"
        
        # Management and common ports
        self.ports = "21,22,23,25,53,80,110,143,389,443,445,465,587,993,995,1433,1521,3306,3389,5432,5900,8080,8443,8888,9090"
        
        logger.info(f"Target domain: {self.domain}")
        logger.info(f"Output directory: {self.output_dir}")
    
    def run_command(self, cmd: List[str], description: str) -> Optional[str]:
        """Execute a shell command and return output"""
        logger.debug(f"Running: {description}")
        logger.debug(f"Command: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            if result.returncode != 0:
                logger.warning(f"Command failed: {description} - {result.stderr}")
                return None
            return result.stdout
        except subprocess.TimeoutExpired:
            logger.error(f"Command timeout: {description}")
            return None
        except Exception as e:
            logger.error(f"Exception in {description}: {str(e)}")
            return None
    
    def discover_subdomains(self) -> Set[str]:
        """Step 1: Discover subdomains using subfinder"""
        logger.info("=== Step 1: Discovering Subdomains ===")
        
        subdomains = set()
        
        # Add parent domain
        subdomains.add(self.domain)
        
        cmd = [
            "subfinder",
            "-d", self.domain,
            "-all",
            "-silent"
        ]
        
        output = self.run_command(cmd, "Subfinder discovery")
        if output:
            for line in output.strip().split('\n'):
                subdomain = line.strip()
                if subdomain:
                    subdomains.add(subdomain)
        
        logger.info(f"Discovered {len(subdomains)} subdomains (including parent domain)")
        return subdomains
    
    def resolve_subdomain(self, subdomain: str) -> Optional[Dict]:
        """Resolve a subdomain to IP using dnsx with detailed info"""
        cmd = [
            "dnsx",
            "-silent",
            "-json",
            "-a",  # A records
            "-aaaa",  # AAAA records
            "-cname",  # CNAME records
            "-resp"  # Include response
        ]
        
        try:
            result = subprocess.run(
                cmd,
                input=subdomain,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.stdout:
                data = json.loads(result.stdout.strip())
                if 'a' in data and data['a']:
                    return {
                        'subdomain': subdomain,
                        'ips': data.get('a', []),
                        'aaaa': data.get('aaaa', []),
                        'cname': data.get('cname', [])
                    }
        except Exception as e:
            logger.debug(f"Resolution failed for {subdomain}: {str(e)}")
        
        return None
    
    def resolve_subdomains(self, subdomains: Set[str]) -> List[Dict]:
        """Step 2: Resolve all subdomains to IPs using dnsx"""
        logger.info("=== Step 2: Resolving Live Subdomains ===")
        
        resolved = []
        
        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            future_to_subdomain = {
                executor.submit(self.resolve_subdomain, sub): sub 
                for sub in subdomains
            }
            
            for future in as_completed(future_to_subdomain):
                result = future.result()
                if result:
                    resolved.append(result)
                    logger.info(f"✓ Resolved: {result['subdomain']} -> {', '.join(result['ips'])}")
        
        logger.info(f"Resolved {len(resolved)} live subdomains")
        return resolved
    
    def scan_ports_nmap(self, ip: str) -> Dict[str, Dict]:
        """Scan ports on an IP using nmap"""
        cmd = [
            "nmap",
            "-p", self.ports,
            "-sV",  # Service version
            "-sS",  # SYN scan
            "-T4",  # Aggressive timing
            "--open",  # Only open ports
            "-oX", "-",  # XML output to stdout
            ip
        ]
        
        output = self.run_command(cmd, f"Scanning {ip}")
        if not output:
            return {}
        
        # Parse XML output
        import xml.etree.ElementTree as ET
        try:
            root = ET.fromstring(output)
            ports_info = {}
            
            for port in root.findall('.//port'):
                port_id = port.get('portid')
                protocol = port.get('protocol')
                state = port.find('state')
                service = port.find('service')
                
                if state is not None and state.get('state') == 'open':
                    port_key = f"{port_id}/{protocol}"
                    ports_info[port_key] = {
                        'port': int(port_id),
                        'protocol': protocol,
                        'state': state.get('state'),
                        'service': service.get('name') if service is not None else 'unknown',
                        'product': service.get('product', '') if service is not None else '',
                        'version': service.get('version', '') if service is not None else ''
                    }
            
            return ports_info
        except Exception as e:
            logger.error(f"Error parsing nmap output for {ip}: {str(e)}")
            return {}
    
    def get_http_info(self, subdomain: str) -> Dict:
        """Get HTTP/HTTPS info using httpx"""
        cmd = [
            "httpx",
            "-silent",
            "-json",
            "-server",
            "-td",  # Tech detect
            "-title",
            "-sc",  # Status code
            "-cl",  # Content length
            "-location",
            "-web-server",
            "-method",
            "-ip",
            "-cname",
            "-cdn",
            "-probe"
        ]
        
        http_info = {}
        
        # Try both HTTP and HTTPS
        for protocol in ['https', 'http']:
            url = f"{protocol}://{subdomain}"
            try:
                result = subprocess.run(
                    cmd,
                    input=url,
                    capture_output=True,
                    text=True,
                    timeout=15
                )
                
                if result.stdout:
                    data = json.loads(result.stdout.strip())
                    http_info[protocol] = {
                        'url': data.get('url', ''),
                        'status_code': data.get('status_code', 0),
                        'title': data.get('title', ''),
                        'server': data.get('webserver', data.get('server', '')),
                        'tech': data.get('tech', []),
                        'content_length': data.get('content_length', 0),
                        'cdn': data.get('cdn', ''),
                        'ip': data.get('host', '')
                    }
            except Exception as e:
                logger.debug(f"HTTP probing failed for {url}: {str(e)}")
        
        return http_info
    
    def get_ssl_cert_info(self, subdomain: str, ip: str) -> Optional[Dict]:
        """Get SSL certificate information"""
        try:
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            
            with socket.create_connection((ip, 443), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=subdomain) as ssock:
                    cert = ssock.getpeercert()
                    
                    return {
                        'subject': dict(x[0] for x in cert.get('subject', ())),
                        'issuer': dict(x[0] for x in cert.get('issuer', ())),
                        'version': cert.get('version'),
                        'serial_number': cert.get('serialNumber'),
                        'not_before': cert.get('notBefore'),
                        'not_after': cert.get('notAfter'),
                        'san': [x[1] for x in cert.get('subjectAltName', ())]
                    }
        except Exception as e:
            logger.debug(f"SSL cert retrieval failed for {subdomain}: {str(e)}")
            return None
    
    def scan_subdomain(self, resolved_data: Dict) -> Dict:
        """Comprehensive scan of a single subdomain"""
        subdomain = resolved_data['subdomain']
        ips = resolved_data['ips']
        
        logger.info(f"Scanning: {subdomain}")
        
        result = {
            'subdomain': subdomain,
            'ips': ips,
            'ipv6': resolved_data.get('aaaa', []),
            'cname': resolved_data.get('cname', []),
            'open_ports': {},
            'http_info': {},
            'ssl_cert': None,
            'scan_time': datetime.now().isoformat()
        }
        
        # Scan first IP for ports
        if ips:
            primary_ip = ips[0]
            result['open_ports'] = self.scan_ports_nmap(primary_ip)
            
            # Get SSL cert info if port 443 is open
            if any('443' in port for port in result['open_ports'].keys()):
                result['ssl_cert'] = self.get_ssl_cert_info(subdomain, primary_ip)
        
        # Get HTTP/HTTPS info
        result['http_info'] = self.get_http_info(subdomain)
        
        return result
    
    def run(self):
        """Execute the complete ASM workflow"""
        logger.info(f"Starting ASM scan for domain: {self.domain}")
        logger.info("=" * 70)
        
        try:
            # Step 1: Discover subdomains
            subdomains = self.discover_subdomains()
            if not subdomains:
                logger.error("No subdomains discovered")
                return False
            
            # Step 2: Resolve to live subdomains only
            resolved = self.resolve_subdomains(subdomains)
            if not resolved:
                logger.error("No live subdomains found")
                return False
            
            # Step 3: Comprehensive scan of each live subdomain
            logger.info(f"=== Step 3: Scanning {len(resolved)} Live Subdomains ===")
            
            all_results = []
            
            with ThreadPoolExecutor(max_workers=min(5, self.threads)) as executor:
                future_to_subdomain = {
                    executor.submit(self.scan_subdomain, data): data['subdomain']
                    for data in resolved
                }
                
                for future in as_completed(future_to_subdomain):
                    result = future.result()
                    all_results.append(result)
            
            # Save results
            with open(self.results_file, 'w') as f:
                json.dump(all_results, f, indent=2)
            
            # Generate summary
            summary = {
                "domain": self.domain,
                "scan_time": datetime.now().isoformat(),
                "total_subdomains_discovered": len(subdomains),
                "live_subdomains": len(resolved),
                "total_unique_ips": len(set(ip for r in all_results for ip in r['ips'])),
                "subdomains_with_open_ports": sum(1 for r in all_results if r['open_ports']),
                "subdomains_with_ssl": sum(1 for r in all_results if r['ssl_cert']),
                "output_file": str(self.results_file)
            }
            
            with open(self.summary_file, 'w') as f:
                json.dump(summary, f, indent=2)
            
            logger.info("=" * 70)
            logger.info(f"✓ Scan completed successfully!")
            logger.info(f"  Live subdomains: {len(resolved)}")
            logger.info(f"  Unique IPs: {summary['total_unique_ips']}")
            logger.info(f"  With open ports: {summary['subdomains_with_open_ports']}")
            logger.info(f"  With SSL certs: {summary['subdomains_with_ssl']}")
            logger.info(f"\nResults: {self.results_file}")
            logger.info(f"Summary: {self.summary_file}")
            
            return True
            
        except Exception as e:
            logger.error(f"Fatal error during scan: {str(e)}")
            import traceback
            traceback.print_exc()
            return False


def main():
    parser = argparse.ArgumentParser(
        description="ASM Tool - Automated Attack Surface Management Scanner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s -d example.com
  %(prog)s -d example.com -o /tmp/results -t 20
  %(prog)s -d example.com --debug
        """
    )
    
    parser.add_argument(
        '-d', '--domain',
        required=True,
        help='Target domain to scan'
    )
    
    parser.add_argument(
        '-o', '--output',
        default='results',
        help='Output directory (default: results)'
    )
    
    parser.add_argument(
        '-t', '--threads',
        type=int,
        default=10,
        help='Number of threads for parallel operations (default: 10)'
    )
    
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug logging'
    )
    
    args = parser.parse_args()
    
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Run the scanner
    scanner = ASMScanner(args.domain, args.output, args.threads)
    success = scanner.run()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
