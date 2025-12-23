# Model Setup and Deployment Guide

## Production VPS Setup

### Step 1: Prepare Your VPS

```bash
# Install Python and dependencies
sudo apt update
sudo apt install python3 python3-pip

# Install required packages
pip install torch transformers
```

### Step 2: Authentication (One-time)

```bash
# Install HuggingFace CLI
pip install huggingface-hub

# Login with your HF token
huggingface-cli login
# Paste your token from: https://huggingface.co/settings/tokens
```

### Step 3: Download Model

```bash
# Upload and run the download script
python download_model.py
```

### Step 4: Deploy Your Application

```bash
# Copy your application files
# - yt_acquisition.py
# - promo_extractor.py
# - main.py (your app)

# Model is now cached, no internet needed for inference
python your_app.py
```

## Alternative: Copy Cached Model

If you want to avoid downloading on VPS:

```bash
# On your local machine
cd ~/.cache/huggingface/hub
tar -czf functiongemma-cache.tar.gz models--google--functiongemma-270m-it

# Upload to VPS
scp functiongemma-cache.tar.gz user@your-vps:/tmp/

# On VPS
mkdir -p ~/.cache/huggingface/hub
cd ~/.cache/huggingface/hub
tar -xzf /tmp/functiongemma-cache.tar.gz
```

## Verification

Test that everything works:

```python
from promo_extractor import PromoExtractorKernel

extractor = PromoExtractorKernel()
result = extractor.process_description("Sponsored by Test. Use code TEST123 for 10% off")
print(result)
```

## Resource Requirements

- **RAM**: 2-4GB minimum
- **Disk**: 1GB for model cache
- **CPU**: Any modern CPU (GPU/MPS faster but not required)
- **Internet**: Only for initial download

## Notes

- Model runs locally, no API calls
- No per-request costs
- Works offline after download
- Accepts Gemma license terms (already done)
