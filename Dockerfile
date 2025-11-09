# ASM Tool - Dockerfile
# Based on Kali Linux with required security tools

FROM kalilinux/kali-rolling:latest

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV PATH="/root/go/bin:${PATH}"
ENV GOPATH="/root/go"

# Update and install base dependencies
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    git \
    python3 \
    python3-pip \
    golang-go \
    nmap \
    dnsutils \
    bind9-dnsutils \
    ca-certificates \
    chromium \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*

# Install Go-based tools from ProjectDiscovery (only what we need)
RUN go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest && \
    go install -v github.com/projectdiscovery/dnsx/cmd/dnsx@latest && \
    go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest && \
    go install -v github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest && \
    go install -v github.com/sensepost/gowitness@latest

# Copy Go binaries to /usr/local/bin for easier access
RUN cp /root/go/bin/* /usr/local/bin/ || true

# Create working directory
WORKDIR /asm

# Copy Python requirements and install
COPY requirements.txt .
RUN pip3 install --no-cache-dir --break-system-packages -r requirements.txt

# Copy the main scanner script
COPY asm_scanner.py .
RUN chmod +x asm_scanner.py

# Create results directory
RUN mkdir -p /asm/results

# Set up volume for results
VOLUME ["/asm/results"]

# Default command
ENTRYPOINT ["python3", "asm_scanner.py"]
CMD ["--help"]
