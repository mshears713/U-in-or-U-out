# Data Alchemist - Docker Setup for Windows/WSL

This guide will help you run Data Alchemist using Docker on Windows (with WSL) or directly in WSL.

---

## Table of Contents

- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Building the Docker Image](#building-the-docker-image)
- [Running with Docker Compose](#running-with-docker-compose)
- [Running with Docker CLI](#running-with-docker-cli)
- [Common Use Cases](#common-use-cases)
- [Windows-Specific Notes](#windows-specific-notes)
- [Troubleshooting](#troubleshooting)
- [Development Mode](#development-mode)

---

## Prerequisites

### For Windows Users

1. **Windows 10/11** with WSL2 enabled
2. **Docker Desktop for Windows** installed and running
   - Download from: https://www.docker.com/products/docker-desktop
   - Ensure WSL2 backend is enabled in Docker Desktop settings
3. **WSL2** with a Linux distribution (Ubuntu recommended)
   - Install from Microsoft Store or PowerShell:
     ```powershell
     wsl --install
     ```

### For WSL/Linux Users

1. **Docker** installed in your WSL distribution
   - Follow: https://docs.docker.com/engine/install/ubuntu/
2. **Docker Compose** (usually included with Docker Desktop)

### Verify Installation

```bash
# Check Docker version
docker --version

# Check Docker Compose version
docker-compose --version

# Verify Docker is running
docker ps
```

---

## Quick Start

### 1. Clone the Repository (if not already done)

```bash
# In WSL or Windows Terminal with WSL
git clone <repository-url>
cd U-in-or-U-out
```

### 2. Create a Data Directory

```bash
# Create a directory for your input/output files
mkdir -p data
```

### 3. Build and Run with Docker Compose

```bash
# Build the image
docker-compose build

# Run the CLI (shows help)
docker-compose run --rm data-alchemist

# Example: Detect file type
docker-compose run --rm data-alchemist detect /data/sample.csv

# Example: Convert CSV to JSON
docker-compose run --rm data-alchemist convert /data/sample.csv --output /data/output.json --format json
```

---

## Building the Docker Image

### Option 1: Using Docker Compose (Recommended)

```bash
# Build the image
docker-compose build

# Build with no cache (fresh build)
docker-compose build --no-cache
```

### Option 2: Using Docker CLI

```bash
# Build the image
docker build -t data-alchemist:latest .

# Build with a specific tag
docker build -t data-alchemist:1.0.0 .
```

---

## Running with Docker Compose

Docker Compose simplifies volume mounting and configuration.

### Basic Commands

```bash
# Show help
docker-compose run --rm data-alchemist --help

# Detect file type
docker-compose run --rm data-alchemist detect /data/yourfile.csv

# List available parsers
docker-compose run --rm data-alchemist list-parsers

# List available converters
docker-compose run --rm data-alchemist list-converters

# Convert CSV to JSON
docker-compose run --rm data-alchemist convert /data/input.csv --output /data/output.json --format json

# Convert with verbose output
docker-compose run --rm data-alchemist --verbose convert /data/input.csv --output /data/output.json --format json
```

### Using Different Volume Paths

Edit `docker-compose.yml` to change the volume mappings:

```yaml
volumes:
  # Windows example (use forward slashes)
  - C:/Users/YourName/data:/data

  # WSL example
  - /home/username/data:/data

  # Relative path (recommended)
  - ./data:/data
```

---

## Running with Docker CLI

If you prefer not to use Docker Compose:

### Windows (PowerShell or CMD)

```powershell
# Create data directory in your current location
mkdir data

# Run with volume mount (use forward slashes for Windows paths)
docker run --rm -v ${PWD}/data:/data data-alchemist:latest --help

# Detect file
docker run --rm -v ${PWD}/data:/data data-alchemist:latest detect /data/sample.csv

# Convert CSV to JSON
docker run --rm -v ${PWD}/data:/data data-alchemist:latest convert /data/sample.csv --output /data/output.json --format json
```

### WSL/Linux

```bash
# Create data directory
mkdir -p data

# Run with volume mount
docker run --rm -v $(pwd)/data:/data data-alchemist:latest --help

# Detect file
docker run --rm -v $(pwd)/data:/data data-alchemist:latest detect /data/sample.csv

# Convert CSV to JSON
docker run --rm -v $(pwd)/data:/data data-alchemist:latest convert /data/sample.csv --output /data/output.json --format json
```

---

## Common Use Cases

### 1. Process CSV Files

```bash
# Place your CSV file in the ./data directory
cp /path/to/mydata.csv ./data/

# Detect the file type
docker-compose run --rm data-alchemist detect /data/mydata.csv

# Convert to JSON
docker-compose run --rm data-alchemist convert /data/mydata.csv --output /data/mydata.json --format json

# Convert to CSV (with processing)
docker-compose run --rm data-alchemist convert /data/mydata.csv --output /data/processed.csv --format csv
```

### 2. Process Image Files

```bash
# Copy image to data directory
cp /path/to/image.jpg ./data/

# Detect and extract metadata
docker-compose run --rm data-alchemist detect /data/image.jpg

# Convert to JSON (extracts EXIF and metadata)
docker-compose run --rm data-alchemist convert /data/image.jpg --output /data/image-metadata.json --format json
```

### 3. Process WAV Audio Files

```bash
# Copy WAV file to data directory
cp /path/to/audio.wav ./data/

# Extract audio metadata
docker-compose run --rm data-alchemist detect /data/audio.wav

# Convert to JSON
docker-compose run --rm data-alchemist convert /data/audio.wav --output /data/audio-info.json --format json
```

### 4. Process Log Files

```bash
# Copy log file to data directory
cp /path/to/application.log ./data/

# Detect log format
docker-compose run --rm data-alchemist detect /data/application.log

# Convert to structured JSON
docker-compose run --rm data-alchemist convert /data/application.log --output /data/structured-logs.json --format json
```

### 5. Batch Processing Multiple Files

```bash
# Create a simple bash script (in WSL)
for file in ./data/*.csv; do
  filename=$(basename "$file" .csv)
  docker-compose run --rm data-alchemist convert "/data/$filename.csv" --output "/data/$filename.json" --format json
done
```

---

## Windows-Specific Notes

### File Path Considerations

1. **Use Forward Slashes**: Even on Windows, use forward slashes in Docker volume mounts
   ```bash
   # Good
   -v C:/Users/Name/data:/data

   # Bad
   -v C:\Users\Name\data:/data
   ```

2. **WSL Path Translation**: When in WSL, Windows drives are mounted at `/mnt/`
   ```bash
   # Access Windows C: drive from WSL
   cd /mnt/c/Users/YourName/Projects/
   ```

3. **Line Endings**: Git may convert line endings. Configure Git properly:
   ```bash
   # In WSL
   git config --global core.autocrlf input
   ```

### Docker Desktop Settings

1. **Enable WSL2 Integration**:
   - Open Docker Desktop
   - Go to Settings → Resources → WSL Integration
   - Enable integration with your WSL distributions

2. **Resource Limits**:
   - Settings → Resources → Advanced
   - Adjust CPU, Memory, Swap as needed (recommended: 4GB+ RAM)

3. **File Sharing**:
   - Ensure your project directory is accessible to Docker
   - Check Settings → Resources → File Sharing

---

## Troubleshooting

### Issue: "docker: command not found"

**Solution**:
```bash
# Verify Docker is installed
which docker

# If not installed in WSL, install it:
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add user to docker group
sudo usermod -aG docker $USER

# Restart WSL or log out and back in
```

### Issue: Permission Denied

**Solution**:
```bash
# Ensure Docker daemon is running
sudo service docker start

# Or if using Docker Desktop, ensure it's running on Windows
```

### Issue: Volume Mount Not Working

**Solution**:
1. Check Docker Desktop file sharing settings
2. Use absolute paths or ensure relative paths are correct
3. Verify the data directory exists:
   ```bash
   ls -la ./data
   ```

### Issue: Image Build Fails

**Solution**:
```bash
# Clear Docker cache and rebuild
docker-compose build --no-cache

# Or with Docker CLI
docker build --no-cache -t data-alchemist:latest .
```

### Issue: "No such file or directory" in Container

**Solution**:
- Ensure files are in the `./data` directory
- Use `/data/` prefix when referencing files in the container
- Check file permissions:
  ```bash
  chmod 644 ./data/yourfile.csv
  ```

### Issue: Slow Performance on Windows

**Solution**:
1. **Use WSL2 file system**: Store project files in WSL2 filesystem (`~/projects/`) instead of Windows filesystem (`/mnt/c/`)
2. **Increase Docker resources**: Docker Desktop → Settings → Resources
3. **Disable Windows Defender real-time scanning** for WSL directories (use with caution)

---

## Development Mode

For development work with live code changes:

### 1. Run Development Container

```bash
# Start development container with bash shell
docker-compose --profile dev run --rm data-alchemist-dev

# Inside the container, you can run commands directly:
python -m data_alchemist.cli detect /data/sample.csv
python -m pytest tests/
```

### 2. Mount Project Directory

```bash
# The dev service mounts the entire project
# Changes to code are immediately reflected in the container
docker-compose --profile dev run --rm data-alchemist-dev bash

# Run tests
python -m pytest tests/

# Run linting
python -m flake8 data_alchemist/
```

### 3. Interactive Python Shell

```bash
# Start Python shell in the container
docker-compose run --rm data-alchemist-dev python

# Then import and test modules:
>>> from data_alchemist.detection.detector import FileTypeDetector
>>> detector = FileTypeDetector()
>>> # ... interactive testing
```

---

## Running Tests in Docker

```bash
# Run all tests
docker-compose run --rm data-alchemist-dev python -m pytest tests/

# Run with coverage
docker-compose run --rm data-alchemist-dev python -m pytest tests/ --cov=data_alchemist --cov-report=term-missing

# Run specific test file
docker-compose run --rm data-alchemist-dev python -m pytest tests/unit/test_parsers.py

# Run with verbose output
docker-compose run --rm data-alchemist-dev python -m pytest tests/ -v
```

---

## Performance Tips

1. **Use .dockerignore**: Already configured to exclude unnecessary files
2. **Layer Caching**: Dependencies are installed in a separate layer for faster rebuilds
3. **Multi-stage Build**: Optimizes final image size
4. **Volume Mounts**: Use named volumes for better performance on Windows
5. **WSL2 File System**: Keep project files in WSL2 for better I/O performance

---

## Summary of Commands

```bash
# Build
docker-compose build

# Run CLI help
docker-compose run --rm data-alchemist --help

# Detect file type
docker-compose run --rm data-alchemist detect /data/file.ext

# Convert file
docker-compose run --rm data-alchemist convert /data/input.ext --output /data/output.json --format json

# Development mode
docker-compose --profile dev run --rm data-alchemist-dev bash

# Run tests
docker-compose run --rm data-alchemist-dev python -m pytest tests/
```

---

## Additional Resources

- **Docker Documentation**: https://docs.docker.com/
- **WSL Documentation**: https://docs.microsoft.com/en-us/windows/wsl/
- **Docker Desktop for Windows**: https://docs.docker.com/desktop/windows/
- **Data Alchemist README**: See `README.md` for application details
- **User Guide**: See `USER_GUIDE.md` for detailed usage instructions

---

## Getting Help

If you encounter issues:

1. Check this troubleshooting guide
2. Review Docker Desktop logs (Windows)
3. Check WSL logs: `dmesg` or `sudo journalctl`
4. Verify Docker configuration: `docker info`
5. See the main `README.md` and `USER_GUIDE.md` for application-specific help

---

**Happy Data Converting with Docker!** 🐳
