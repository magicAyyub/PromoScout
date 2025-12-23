"""
Download and cache the FunctionGemma model locally.
Run this once to pre-download the model.
"""
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from pathlib import Path

MODEL_ID = "google/functiongemma-270m-it"

def get_device() -> torch.device:
    """Select best available device"""
    if getattr(torch.backends, "mps", None) and torch.backends.mps.is_available():
        return torch.device("mps")
    elif torch.cuda.is_available():
        return torch.device("cuda")
    else:
        return torch.device("cpu")

def download_and_cache_model():
    """Download model and tokenizer to local cache"""
    print(f"Downloading model: {MODEL_ID}")
    print("This will take a few minutes (~536MB)...")
    print("-" * 50)
    
    device = get_device()
    dtype = torch.float32 if device.type == "mps" else torch.float16
    
    print(f"\nDevice: {device}")
    print(f"Data type: {dtype}")
    print("\nDownloading tokenizer...")
    
    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
    print("✓ Tokenizer downloaded")
    
    print("\nDownloading model...")
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_ID,
        torch_dtype=dtype,
        device_map="auto"
    )
    print("✓ Model downloaded")
    
    # Get cache location
    cache_dir = Path.home() / ".cache" / "huggingface" / "hub"
    print(f"\n{'='*50}")
    print("Download complete!")
    print(f"{'='*50}")
    print(f"Cache location: {cache_dir}")
    print("\nThe model is now cached and ready for offline use.")
    print("You can run your application without internet access.")
    
    # Test quick inference
    print("\nTesting model...")
    test_input = tokenizer("Hello", return_tensors="pt").to(device)
    with torch.no_grad():
        model.generate(**test_input, max_new_tokens=5)
    print("✓ Model test successful")
    
    print("\n" + "="*50)
    print("Setup complete! You can now use PromoExtractorKernel.")
    print("="*50)

if __name__ == "__main__":
    try:
        download_and_cache_model()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nMake sure you:")
        print("1. Accepted the license at https://huggingface.co/google/functiongemma-270m-it")
        print("2. Are logged in: huggingface-cli login")
