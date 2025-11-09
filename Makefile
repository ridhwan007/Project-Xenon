# Makefile for ASM Scanner
.PHONY: help build run clean test shell

# Default target
help:
	@echo "ASM Scanner - Available commands:"
	@echo ""
	@echo "  make build         Build the Docker image"
	@echo "  make run DOMAIN=x  Run a scan against domain"
	@echo "  make shell         Open a shell in the container"
	@echo "  make clean         Remove results and Docker images"
	@echo "  make test          Run a test scan"
	@echo ""
	@echo "Examples:"
	@echo "  make run DOMAIN=example.com"
	@echo "  make run DOMAIN=example.com THREADS=20"
	@echo "  make run DOMAIN=example.com DEBUG=--debug"

# Build Docker image
build:
	docker-compose build

# Run scan
run:
	@if [ -z "$(DOMAIN)" ]; then \
		echo "Error: DOMAIN is required"; \
		echo "Usage: make run DOMAIN=example.com [THREADS=10] [DEBUG=--debug]"; \
		exit 1; \
	fi
	docker-compose run --rm asm-scanner -d $(DOMAIN) -t $(or $(THREADS),10) $(DEBUG)

# Open shell in container
shell:
	docker-compose run --rm --entrypoint /bin/bash asm-scanner

# Clean results and images
clean:
	@echo "Removing results..."
	rm -rf results/*
	@echo "Removing Docker images..."
	docker-compose down --rmi all
	@echo "Clean complete!"

# Test with a safe domain
test:
	@echo "Running test scan on example.com..."
	$(MAKE) run DOMAIN=example.com THREADS=5

# Quick rebuild without cache
rebuild:
	docker-compose build --no-cache

# View logs from last scan
logs:
	@if [ -d "results" ]; then \
		find results -name "*.log" -type f -exec tail -f {} + ; \
	else \
		echo "No results directory found"; \
	fi
