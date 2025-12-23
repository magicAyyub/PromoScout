import json
import re
from typing import List, Dict, Any
from helper.yt_acquisition import YouTubeAcquisitionKernel

class PopulationHarvester:
    """
    Advanced discovery module using affiliate domain patterns.
    Targets hidden sponsorships in descriptions instead of titles.
    """

    def __init__(self, target_country: str = "FR"):
        self.target_country = target_country
        self.acquisition = YouTubeAcquisitionKernel()
        # Filter for 'Today' to ensure 48h recency constraint
        self.search_filter = "EgIIAg%253D%253D" 

    def discover_by_domains(self, domains: List[str]) -> List[Dict[str, Any]]:
        """
        Searches YouTube for videos containing specific affiliate domains.
        Example domains: 'hostinger.fr', 'nordvpn.com'
        """
        discovered_population = []
        
        for domain in domains:
            print(f"Scanning YouTube for domain: {domain}")
            # Searching for the domain string directly
            search_url = f"https://www.youtube.com/results?search_query=\"{domain}\"&sp={self.search_filter}"
            
            response = self.acquisition.session.get(search_url)
            if response.status_code == 200:
                videos = self._parse_search_results(response.text, domain)
                discovered_population.extend(videos)
                
        return discovered_population

    def _parse_search_results(self, html: str, source_domain: str) -> List[Dict[str, Any]]:
        """
        Parses ytInitialData to identify channels and videos.
        """
        pattern = r"var ytInitialData = ({.*?});"
        match = re.search(pattern, html)
        if not match:
            return []

        results = []
        try:
            data = json.loads(match.group(1))
            contents = data['contents']['twoColumnSearchResultsRenderer']['primaryContents']['sectionListRenderer']['contents']
            
            for section in contents:
                if 'itemSectionRenderer' in section:
                    for item in section['itemSectionRenderer']['contents']:
                        if 'videoRenderer' in item:
                            video = item['videoRenderer']
                            # Extracting core metadata
                            results.append({
                                "video_id": video['videoId'],
                                "channel_id": video['ownerText']['runs'][0]['navigationEndpoint']['browseEndpoint']['browseId'],
                                "channel_name": video['ownerText']['runs'][0]['text'],
                                "title": video['title']['runs'][0]['text'],
                                "detected_domain": source_domain,
                                "upload_date_text": video.get('publishedTimeText', {}).get('simpleText', '')
                            })
        except (KeyError, IndexError, TypeError):
            pass
            
        return results
    
if __name__ == "__main__":
    harvester = PopulationHarvester(target_country="FR")
    domains_to_search = ["weareholy.com"]
    population = harvester.discover_by_domains(domains_to_search)
    
    print(f"Discovered {len(population)} videos with target domains.")
    for entry in population:
        print(f"Video ID: {entry['video_id']}, Channel: {entry['channel_name']}, Domain: {entry['detected_domain']}, Title: {entry['title']}")