# Data Directory

This directory is used for storing input and output files when running Data Alchemist with Docker.

## Usage

### Docker Setup

When running Data Alchemist in Docker, this directory is automatically mounted to `/data` inside the container.

**Example:**

1. Place your input files here:
   ```
   data/
   ├── sample.csv
   ├── image.jpg
   ├── audio.wav
   └── application.log
   ```

2. Run Data Alchemist:
   ```bash
   # Detect file type
   docker-compose run --rm data-alchemist detect /data/sample.csv

   # Convert CSV to JSON
   docker-compose run --rm data-alchemist convert /data/sample.csv --output /data/output.json --format json
   ```

3. Your output files will appear in this directory:
   ```
   data/
   ├── sample.csv        (input)
   ├── output.json       (output)
   ├── image.jpg
   ├── audio.wav
   └── application.log
   ```

## Path Reference

- **Host (Windows/WSL):** `./data/yourfile.csv`
- **Inside Container:** `/data/yourfile.csv`

## Supported File Types

Place any of these file types in this directory:

- **CSV/TSV files** (`.csv`, `.tsv`)
- **Image files** (`.png`, `.jpg`, `.jpeg`)
- **Audio files** (`.wav`)
- **Log files** (`.log`, `.txt`)

## Tips

1. **Windows Users:** Use forward slashes in paths even on Windows
2. **File Permissions:** Ensure files are readable (chmod 644)
3. **Large Files:** Docker handles large files efficiently with volume mounts
4. **Subdirectories:** You can create subdirectories for better organization

## Security Note

This directory is mounted as a volume. Do not place sensitive data here unless you understand the security implications of Docker volume mounts.

## See Also

- [DOCKER_SETUP.md](../DOCKER_SETUP.md) - Complete Docker documentation
- [USER_GUIDE.md](../USER_GUIDE.md) - Application usage guide
- [README.md](../README.md) - Main project documentation
