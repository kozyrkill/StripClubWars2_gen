"""
Stable Diffusion WebUI API client
"""
import requests
import base64
import io
from PIL import Image
from typing import Optional, Tuple
from .config import Config
from .models import GenerationSettings

class StableDiffusionClient:
    """Client for Stable Diffusion WebUI API"""
    
    def __init__(self, config: Config = None):
        self.config = config or Config()
        self.session = requests.Session()
        self.session.timeout = 300  # 5 minutes timeout
    
    def check_connection(self) -> bool:
        """Check if WebUI API is accessible"""
        try:
            response = self.session.get(f"{self.config.WEBUI_URL}/internal/ping", timeout=10)
            return response.status_code == 200
        except Exception:
            return False
    
    def generate_image(self, prompt: str, negative_prompt: str, 
                      settings: GenerationSettings) -> Optional[Image.Image]:
        """Generate image using txt2img API"""
        payload = {
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "steps": settings.steps,
            "cfg_scale": settings.cfg_scale,
            "sampler_name": settings.sampler,
            "width": settings.width,
            "height": settings.height,
            "seed": settings.seed,
            "batch_size": 1,
            "n_iter": 1,
            "restore_faces": False,
            "tiling": False,
            "enable_hr": False
        }
        
        try:
            response = self.session.post(
                f"{self.config.WEBUI_API_URL}/txt2img", 
                json=payload,
                timeout=300
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("images"):
                    # Decode base64 image
                    image_data = base64.b64decode(result["images"][0])
                    return Image.open(io.BytesIO(image_data))
            else:
                print(f"❌ API Error {response.status_code}: {response.text}")
                
        except requests.exceptions.Timeout:
            print("❌ Request timeout - generation took too long")
        except Exception as e:
            print(f"❌ Generation error: {e}")
            
        return None
    
    def get_models(self) -> list:
        """Get available models"""
        try:
            response = self.session.get(f"{self.config.WEBUI_API_URL}/sd-models")
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"❌ Error getting models: {e}")
        return []
    
    def get_samplers(self) -> list:
        """Get available samplers"""
        try:
            response = self.session.get(f"{self.config.WEBUI_API_URL}/samplers")
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"❌ Error getting samplers: {e}")
        return []
