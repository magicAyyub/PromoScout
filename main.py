from helper.yt_acquisition import YouTubeAcquisitionKernel
from helper.promo_extractor import PromoExtractorKernel

TARGET_URL = "https://www.youtube.com/watch?v=jFP35_4Y0ic"

# Get description from YouTube
print("Fetching video description...")
scraper = YouTubeAcquisitionKernel()
raw_description = scraper.get_description(TARGET_URL)

if not raw_description:
    print("Failed to fetch description")
    exit(1)

print(f"\nDescription fetched: {len(raw_description)} characters\n")

# Extract promo information
print("Extracting promo details...\n")
extractor = PromoExtractorKernel()
result = extractor.process_description(raw_description)

if result:
    print("\n" + "="*50)
    print("EXTRACTED PROMO INFORMATION")
    print("="*50)
    print(f"Brand: {result.get('brand', 'N/A')}")
    print(f"Code: {result.get('code', 'N/A')}")
    print(f"Discount: {result.get('discount', 'N/A')}")
    print("="*50)
else:
    print("\nNo promo information found")