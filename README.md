# AEM CDN Log Analysis Tool

A Python script for analyzing Adobe Experience Manager (AEM) as a Cloud Service CDN logs. This tool filters out bot traffic, system requests, and errors to provide meaningful insights into your CDN performance and usage patterns.

## Features

- Filters out bot traffic (Google, Bing, Facebook, etc.)
- Excludes system requests, health checks, and DDoS attacks
- Analyzes traffic patterns by hour, IP, URL, and country
- Calculates cache hit ratios and average TTFB
- Generates detailed CSV reports with URL counts and top user agents
- Supports both HTML and JSON content type analysis

## Prerequisites

- Python 3.x (comes pre-installed on macOS)
- CDN log files from Adobe Cloud Manager in JSON format

## Installation

### 1. Clone or download this repository

```bash
git clone https://github.com/ericvangeem/aem-cdn-usage.git
cd aem-cdn-usage
```

### 2. Create a virtual environment

```bash
python3 -m venv venv
```

### 3. Activate the virtual environment

```bash
source venv/bin/activate
```

You should see `(venv)` appear at the beginning of your terminal prompt.

### 4. Install dependencies

```bash
pip install pandas
```

## Usage

### Basic usage

```bash
python analyze_logs.py <path-to-log-file>
```

### Example

```bash
python analyze_logs.py cdn-logs-2024-11-17.log
```

## Output

The script generates two types of output:

### 1. Terminal Output
Displays comprehensive analytics including:
- Total requests (after filtering)
- Requests per hour
- Top 50 IP addresses
- Top 100 URLs
- Top 50 User Agents
- HTTP status code distribution
- Average Time to First Byte (TTFB)
- Cache hit ratio (HIT/MISS/PASS)
- Country distribution
- Content type distribution

### 2. CSV File
Generates a file named `requested_urls_<input-filename>.csv` containing:
- Each unique URL
- Request count for each URL
- Top 5 user agents accessing each URL
- Count for each user agent

## Log File Format

The script expects CDN log files in JSON format with one JSON object per line. Each log entry should contain fields like:
- `url` - The requested URL
- `status` - HTTP status code
- `res_ctype` - Response content type
- `cli_ip` - Client IP address
- `cli_country` - Client country
- `cache` - Cache status (HIT/MISS/PASS)
- `ttfb` - Time to First Byte
- `req_ua` - User agent string
- `ddos` - DDoS flag
- `timestamp` - Request timestamp

## Filtering Logic

The script automatically excludes:
- Non-HTML/JSON content types
- HTTP status codes ≥ 300 (redirects, errors)
- Requests to `/libs/*` paths
- DDoS flagged requests
- Health check requests (`/system/probes/health`)
- Skyline service warmup requests
- Known bot traffic (Google, Bing, Facebook, etc.)
- `manifest.json` and `favicon.ico` requests

## Deactivating the Virtual Environment

When you're done analyzing logs:

```bash
deactivate
```

## Next Time You Use the Script

```bash
cd ~/path/to/aem-cdn-usage
source venv/bin/activate
python analyze_logs.py your-log-file.log
```

## Troubleshooting

### "ModuleNotFoundError: No module named 'pandas'"
Make sure you've activated the virtual environment:
```bash
source venv/bin/activate
```

### "No such file or directory"
Check that your log file path is correct. Use the full path if needed:
```bash
python analyze_logs.py /full/path/to/your/logfile.log
```

### "Usage: python analyze_logs.py <input_log_file>"
You must provide a log file as an argument:
```bash
python analyze_logs.py cdn-logs.log
```

## Getting CDN Logs from Cloud Manager

1. Log in to Adobe Cloud Manager
2. Navigate to your environment
3. Go to the "Logs" section
4. Select "CDN" as the log type
5. Download the log files (they typically come as `.log.gz` files)
6. Unzip the files: `gunzip cdn-logs.log.gz`
7. Run the analysis script on the unzipped `.log` file

## License

MIT

## Author

Eric Van Geem
