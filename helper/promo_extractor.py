import torch
from transformers import pipeline
from typing import Dict, Any, Optional

def get_device() -> torch.device:
    """
    Select the best available device:
    - MPS on Apple Silicon (if available)
    - CUDA GPU on NVIDIA systems (if available)
    - CPU fallback otherwise
    """
    if getattr(torch.backends, "mps", None) and torch.backends.mps.is_available():
        return torch.device("mps")
    elif torch.cuda.is_available():
        return torch.device("cuda")
    else:
        return torch.device("cpu")

class PromoExtractorKernel:
    """
    NLP Kernel using FunctionGemma-270M to extract structured 
    promotion data from unstructured video descriptions.
    """

    def __init__(self, model_id: str = "google/functiongemma-270m-it"):
        device = get_device()
        dtype = torch.float32 if device.type == "mps" else torch.float16
        
        self.generator = pipeline(
            "text-generation",
            model=model_id,
            device=device,
            dtype=dtype
        )

    def process_description(self, description: str) -> Optional[Dict[str, Any]]:
        """
        Submits the description to Gemma and parses the function call result.
        Uses few-shot learning for better extraction.
        """
        context = description[:800]
        prompt = self._build_few_shot_prompt(context)
        
        response = self.generator(
            prompt,
            max_new_tokens=200,
            temperature=0.1,
            do_sample=False,
            return_full_text=False,
            pad_token_id=self.generator.tokenizer.eos_token_id
        )
        
        return self._parse_llm_output(response[0]['generated_text'])

    def _build_few_shot_prompt(self, text: str) -> str:
        """
        Builds a few-shot learning prompt with examples for better extraction.
        """
        return f"""Extract sponsor/brand, promo code, and discount from YouTube descriptions. Return JSON format with these exact keys: brand, code, discount.

IMPORTANT: Only extract if there is a clear sponsorship or promotional offer. If no promo code or sponsor exists, return null for all fields.

Example 1:
Input: "Pour découvrir les offres VPS d'Hostinger : https://www.hostinger.fr/solene. En plus de l'offre Black Friday, profite de réductions supplémentaires avec le code SOLENE. Encore un grand merci à Hostinger!"
Output: {{"brand": "Hostinger", "code": "SOLENE", "discount": "Black Friday + extra discount"}}

Example 2:
Input: "Hey everyone! This video is sponsored by Squarespace. Get 10% off your first purchase using code TECH2023 at checkout."
Output: {{"brand": "Squarespace", "code": "TECH2023", "discount": "10% off"}}

Example 3:
Input: "Sponsored by Brilliant. Use code SCIENCE for 20% off premium."
Output: {{"brand": "Brilliant", "code": "SCIENCE", "discount": "20% off premium"}}

Example 4:
Input: "In this tutorial, we'll learn Python basics. No sponsors today, just pure content! Follow me on Twitter."
Output: {{"brand": null, "code": null, "discount": null}}

Example 5:
Input: "Check out my GitHub repo for the code. Thanks for watching!"
Output: {{"brand": null, "code": null, "discount": null}}

Now extract from:
Input: "{text}"
Output:"""

    def _parse_llm_output(self, output: str) -> Optional[Dict[str, Any]]:
        """
        Parses LLM output expecting JSON format.
        """
        import json
        import re
        
        print(f"Model Raw Output: {output}")
        print("-" * 50)
        
        # Try to find JSON object in output
        json_match = re.search(r'\{[^{}]*\}', output)
        if json_match:
            try:
                result = json.loads(json_match.group(0))
                # Ensure all required keys exist
                for key in ["brand", "code", "discount"]:
                    if key not in result:
                        result[key] = None
                return result if any(result.values()) else None
            except json.JSONDecodeError as e:
                print(f"JSON parse error: {e}")
        
        # Fallback: try to parse key-value format
        result = {"brand": None, "code": None, "discount": None}
        brand_match = re.search(r'["\']?brand["\']?\s*[:=]\s*["\']([^"\'\n]+)["\']', output, re.IGNORECASE)
        code_match = re.search(r'["\']?code["\']?\s*[:=]\s*["\']([^"\'\n]+)["\']', output, re.IGNORECASE)
        discount_match = re.search(r'["\']?discount["\']?\s*[:=]\s*["\']([^"\'\n]+)["\']', output, re.IGNORECASE)
        
        if brand_match:
            result["brand"] = brand_match.group(1).strip()
        if code_match:
            result["code"] = code_match.group(1).strip()
        if discount_match:
            result["discount"] = discount_match.group(1).strip()
        
        return result if any(result.values()) else None

# Execution test
if __name__ == "__main__":
    with open("../sample_description.txt", "r", encoding="utf-8") as f:
        sample_description = f.read()
    extractor = PromoExtractorKernel()
    promo_info = extractor.process_description(sample_description)
    if promo_info:
        print("Extracted Promo Information:")
        print(promo_info)