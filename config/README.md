# ASM Scanner Configuration

This directory can be used to store configuration files for various tools.

## Subfinder Provider Config

To configure API keys for subfinder, create a `provider-config.yaml` file:

```yaml
# Example provider-config.yaml for subfinder
binaryedge:
  - YOUR_API_KEY
censys:
  - YOUR_API_KEY
certspotter: []
passivetotal:
  - YOUR_USERNAME
  - YOUR_API_KEY
securitytrails:
  - YOUR_API_KEY
shodan:
  - YOUR_API_KEY
urlscan:
  - YOUR_API_KEY
virustotal:
  - YOUR_API_KEY
chaos:
  - YOUR_API_KEY
```

Then mount this config when running the container:

```bash
docker-compose run --rm -v ./config/provider-config.yaml:/root/.config/subfinder/provider-config.yaml asm-scanner -d example.com
```

## Custom Resolvers

Place custom DNS resolver lists here and mount them to the container.

## Nmap Scripts

Custom NSE (Nmap Scripting Engine) scripts can be placed here and mounted.
