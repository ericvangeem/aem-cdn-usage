import pandas as pd
import json
from collections import Counter
import re

# Read the log file
def read_log_file(file_path):
    with open(file_path, 'r') as f:
        return [json.loads(line) for line in f]

# Filter function
def should_include(entry):
    # Include only application/json or text/html
    if entry['res_ctype'] not in ['application/json', 'text/html']:
        return False
    
    # Exclude based on HTTP status code
    if entry['status'] >= 300:
        return False
    
    # Exclude /libs/* requests
    if entry['url'].startswith('/libs/'):
        return False
    
    # Exclude DDOS attacks
    if entry['ddos']:
        return False
    
    # Exclude /system/probes/health
    if entry['url'] == '/system/probes/health':
        return False
    
    # Exclude specific User Agent
    if entry['req_ua'].startswith('skyline-service-warmup/1.'):
        return False
    
    # Exclude well-known bots
    bot_patterns = [
        r'AddSearchBot', r'AhrefsBot', r'Applebot', r'Ask Jeeves', r'Bing', 
        r'BLEX', r'BuiltWith', r'Bytespider', r'CrawlerKengo', r'Facebook', 
        r'Google', r'lmspider', r'LucidWorks', r'MJ12bot', r'Pinterest', 
        r'Semrush', r'SiteImprove', r'StashBot', r'StatusCake', r'Yandex',
        r'Claudebot'
    ]
    if any(re.search(pattern, entry['req_ua'], re.IGNORECASE) for pattern in bot_patterns):
        return False
    
    # Exclude manifest.json and favicon.ico
    if entry['url'] in ['/manifest.json', '/favicon.ico']:
        return False
    
    return True

# Analyze the log data
def analyze_logs(logs):
    # Filter logs
    filtered_logs = [log for log in logs if should_include(log)]
    
    df = pd.DataFrame(filtered_logs)
    
    # Convert timestamp to datetime
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Requests per hour
    requests_per_hour = df.groupby(df['timestamp'].dt.hour).size()
    
    # Top 100 IP addresses
    top_ips = df['cli_ip'].value_counts().head(100)
    
    # Top 100 URLs
    top_urls = df['url'].value_counts().head(100)
    
    # HTTP status code distribution
    status_distribution = df['status'].value_counts()
    
    # Average TTFB
    avg_ttfb = df['ttfb'].mean()
    
    # Cache hit ratio
    cache_hit_ratio = df['cache'].value_counts(normalize=True)
    
    # Country distribution
    country_distribution = df['cli_country'].value_counts()
    
    # Content type distribution
    content_type_distribution = df['res_ctype'].value_counts()
    
    return {
        'total_requests': len(df),
        'requests_per_hour': requests_per_hour,
        'top_ips': top_ips,
        'top_urls': top_urls,
        'status_distribution': status_distribution,
        'avg_ttfb': avg_ttfb,
        'cache_hit_ratio': cache_hit_ratio,
        'country_distribution': country_distribution,
        'content_type_distribution': content_type_distribution
    }

# Main execution
if __name__ == "__main__":
    logs = read_log_file('publish_cdn_2024-10-17.log')
    results = analyze_logs(logs)
    
    # Print results
    for key, value in results.items():
        print(f"\n{key.upper()}:")
        print(value)