from huggingface_hub import HfApi
from typing import List, Dict, Any

class HFMatcher:
    def __init__(self):
        self.api = HfApi()

    def find_replacements(self, description: str, limit: int = 3) -> List[Dict[str, Any]]:
        try:
            models = self.api.list_models(
                search=description,
                sort="downloads",
                direction=-1,
                limit=limit
            )
            results = []
            for model in models:
                results.append({
                    "id": model.id,
                    "downloads": model.downloads,
                    "likes": model.likes,
                    "url": f"https://huggingface.co/{model.id}"
                })
            return results
        except Exception as e:
            print(f"HF search failed: {e}")
            return []
