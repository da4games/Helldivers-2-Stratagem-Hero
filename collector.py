import requests

class DataCollector:
    def __init__(self, base_url, parse_html=True):
        self.base_url = base_url
        self.parse_html = parse_html
    
    def fetch_data(self):
        try:
            response = requests.get(self.base_url)
            response.raise_for_status()
            # If configured to parse HTML, return a BeautifulSoup object when possible
            if self.parse_html:
                try:
                    from bs4 import BeautifulSoup
                    return BeautifulSoup(response.content, "html.parser")
                except Exception:
                    # bs4 not available or parsing failed — return raw text
                    print("Warning: failed to parse HTML content")
                    return response.text

            content_type = response.headers.get("Content-Type", "")
            if "application/json" in content_type:
                try:
                    return response.json()
                except ValueError:
                    print("Warning: response not valid JSON, returning raw text")
                    return response.text
            # fallback for non-JSON responses (HTML, plain text, etc.)
            return response.text
        except requests.RequestException as e:
            print(f"Error fetching data: {e}")
            return None
        
Collector = DataCollector("https://helldivers.wiki.gg/wiki/Stratagems", parse_html=True)
result = Collector.fetch_data()
print(f"{result}")