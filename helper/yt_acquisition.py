import requests
import re
import json
from typing import Optional, Any

class YouTubeAcquisitionKernel:
    """
    Handles raw data acquisition from YouTube without API keys.
    Focuses on extracting 'ytInitialData' from the page source.
    """

    def __init__(self):
        self.session = requests.Session()
        # Using a modern User-Agent to avoid being flagged as a basic bot
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
        })

    def get_description(self, video_url: str) -> Optional[str]:
        """
        Fetches the video page and extracts the full description from the 
        ytInitialData JSON object.
        """
        try:
            response = self.session.get(video_url, timeout=10)
            response.raise_for_status()
            
            return self._extract_description_from_html(response.text)
        except Exception as error:
            print(f"Acquisition error: {error}")
            return None

    def _extract_description_from_html(self, html_content: str) -> Optional[str]:
        """
        Parses the HTML to find the ytInitialData variable.
        """
        # Try multiple patterns as YouTube format may vary
        patterns = [
            r"var ytInitialData = ({.*?});</script>",
            r"var ytInitialData = ({.*?});",
            r"ytInitialData = ({.*?});</script>",
            r"ytInitialData = ({.*?});"
        ]
        
        match = None
        for pattern in patterns:
            match = re.search(pattern, html_content, re.DOTALL)
            if match:
                break
        
        if not match:
            return None
            
        try:
            data = json.loads(match.group(1))
            return self._parse_json_path(data)
        except json.JSONDecodeError:
            return None

    def _parse_json_path(self, data: Any) -> Optional[str]:
        """
        Navigates the deep JSON structure to find the description field.
        Path: contents -> twoColumnWatchNextResults -> results -> results 
              -> contents -> videoSecondaryInfoRenderer -> description
        """
        try:
            # The path can slightly vary depending on the UI version
            results = data['contents']['twoColumnWatchNextResults']['results']['results']['contents']
            
            for item in results:
                if 'videoSecondaryInfoRenderer' in item:
                    # Try new format: attributedDescription.content
                    description_data = item['videoSecondaryInfoRenderer'].get('attributedDescription')
                    if description_data:
                        content = description_data.get('content', '')
                        if content:
                            return content
                    
                    # Fallback to old format: description.runs
                    description_data = item['videoSecondaryInfoRenderer'].get('description')
                    if description_data:
                        runs = description_data.get('runs', [])
                        if runs:
                            return "".join([run.get('text', '') for run in runs])
            
            return None
        except (KeyError, IndexError, TypeError):
            return None
