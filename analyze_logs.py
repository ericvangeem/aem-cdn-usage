import pandas as pd
import json
from collections import Counter
import re
import os
import sys

# Read the log file
def read_log_file(file_path):
    with open(file_path, 'r') as f:
        return [json.loads(line) for line in f]

# Filter function
def should_include(entry):
    # Include only application/json or text/html
    if not (entry['res_ctype'].startswith('application/json') or entry['res_ctype'].startswith('text/html')):
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
        r'Claudebot', r'Baiduspider', r'bot', r'spider', r'amazon-QBusiness'
    ]
    if any(re.search(pattern, entry['req_ua'], re.IGNORECASE) for pattern in bot_patterns):
        return False
    
    # Exclude manifest.json and favicon.ico
    if entry['url'] in ['/manifest.json', '/favicon.ico']:
        return False
    
    # Exclude events.html URLs
    if 'events.html' in entry['url']:
        return False
    
    # Exclude specific JSON content paths
    if entry['res_ctype'].startswith('application/json'):
        if entry['url'].startswith('/content/cq:tags') or entry['url'].startswith('/content/bc-web'):
            return False
    
    return True

# Analyze the log data
def analyze_logs(logs, input_filename):
    # Filter logs
    filtered_logs = [log for log in logs if should_include(log)]
    
    df = pd.DataFrame(filtered_logs)
    
    # Convert timestamp to datetime
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Requests per hour
    requests_per_hour = df.groupby(df['timestamp'].dt.hour).size()
    
    # Top 50 IP addresses
    top_ips = df['cli_ip'].value_counts().head(50)
    
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
    def simplify_content_type(ctype):
        if ctype.startswith('text/html'):
            return 'HTML'
        elif ctype.startswith('application/json'):
            return 'JSON'
        else:
            return 'Other'

    df['simplified_ctype'] = df['res_ctype'].apply(simplify_content_type)
    content_type_distribution = df['simplified_ctype'].value_counts()
    
    # Adjust JSON count and create a new distribution
    adjusted_content_type_distribution = content_type_distribution.astype(float)
    if 'JSON' in adjusted_content_type_distribution:
        json_count = adjusted_content_type_distribution['JSON']
        adjusted_content_type_distribution['JSON'] = json_count / 5
    
    # Top 50 User Agents
    top_user_agents = df['req_ua'].value_counts().head(50)

    # Generate CSV of requested URLs, their counts, and top 5 user agents
    url_counts = df.groupby('url').agg({
        'url': 'count',
        'req_ua': lambda x: x.value_counts().nlargest(5).to_dict()
    })
    url_counts.columns = ['Count', 'UserAgents']
    url_counts = url_counts.reset_index()

    # Expand the UserAgents dictionary into separate columns
    for i in range(1, 6):
        url_counts[f'UserAgent_{i}'] = url_counts['UserAgents'].apply(
            lambda x: list(x.keys())[i-1] if len(x) >= i else '')
        url_counts[f'UACount_{i}'] = url_counts['UserAgents'].apply(
            lambda x: list(x.values())[i-1] if len(x) >= i else 0)

    # Drop the temporary UserAgents column
    url_counts = url_counts.drop('UserAgents', axis=1)

    # Sort the DataFrame by Count in descending order
    url_counts = url_counts.sort_values('Count', ascending=False)

    # Create CSV filename based on input log file
    csv_filename = f'requested_urls_{os.path.splitext(os.path.basename(input_filename))[0]}.csv'
    url_counts.to_csv(csv_filename, index=False)
    
    return {
        'total_requests': len(df),
        'requests_per_hour': requests_per_hour,
        'top_ips': top_ips,
        'top_urls': top_urls,
        'top_user_agents': top_user_agents,
        'status_distribution': status_distribution,
        'avg_ttfb': avg_ttfb,
        'cache_hit_ratio': cache_hit_ratio,
        'country_distribution': country_distribution,
        'content_type_distribution': content_type_distribution,
        'adjusted_content_type_distribution': adjusted_content_type_distribution
    }, csv_filename

# Main execution
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python analyze_logs.py <input_log_file>")
        sys.exit(1)

    input_log_file = sys.argv[1]
    logs = read_log_file(input_log_file)
    results, csv_filename = analyze_logs(logs, input_log_file)
    
    # Print results
    with pd.option_context('display.max_rows', None, 'display.max_columns', None, 'display.width', None, 'display.max_seq_items', 50):
        for key, value in results.items():
            print(f"\n{key.upper()}:")
            print(value)            
    
    print(f"\nCSV file '{csv_filename}' has been generated with URL counts.")
