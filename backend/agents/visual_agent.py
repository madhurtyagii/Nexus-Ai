"""Nexus AI - Visual Agent (Unified Vision + Generation).

This module implements the VisualAgent — a unified visual intelligence agent
that combines three capabilities:
  1. IMAGE ANALYSIS — Describe/explain images using multimodal LLMs
  2. IMAGE GENERATION — Create new images using Stable Diffusion XL (SDXL)
  3. IMAGE EDITING — Transform existing images via img2img pipeline

Image generation runs in a separate subprocess so that all model memory
(~8 GB) is returned to the OS as soon as the image is saved.
"""

import os
import sys
import time
import base64
import subprocess
from typing import Dict, Any, List, Optional
from datetime import datetime

from agents.base_agent import BaseAgent
from agents.agent_registry import AgentRegistry
from logging_config import get_logger

logger = get_logger("agents.visual")


# ── Vision / Analysis constants ──────────────────────────────────────
VISION_MODEL = "meta-llama/llama-4-maverick-17b-128e-instruct"  # Groq Llama 4 Multimodal
VISION_SYSTEM_PROMPT = """You are a highly skilled visual expert and friendly collaborator. You analyze images with high precision and explain them in a conversational, helpful tone.
When shown an image, describe it clearly as if talking to a friend. If asked a specific question, be accurate but keep it engaging. If it's a UI sketch, explain the layout and possibilities vividly."""

# Keywords that signal the user wants to ANALYZE an existing image (not generate)
ANALYZE_KEYWORDS = [
    "describe", "what is", "what's in", "explain", "analyze", "identify",
    "tell me about", "what do you see", "read", "extract", "ocr", "summarize this image"
]

# Keywords that signal the user wants to EDIT an existing image
EDIT_KEYWORDS = [
    "edit", "modify", "change", "transform", "make it", "add a",
    "remove", "style as", "convert to", "turn this into"
]


# ── Generation constants ─────────────────────────────────────────────
# Quality boosters appended to every prompt for consistent high quality
QUALITY_SUFFIX = (
    ", masterpiece, best quality, highly detailed, sharp focus, "
    "professional, 8k uhd, high resolution, intricate details"
)

# Style Presets for consistent artistic looks
STYLE_PRESETS = {
    "Photorealistic": "highly realistic, cinematic lighting, 8k, raw photo, detailed texture",
    "Digital Art": "digital painting, vibrant colors, sharp lines, concept art, artstation style",
    "Anime": "anime style, cel shaded, vibrant, high quality anime art, studio ghibli inspired",
    "3D Render": "unreal engine 5, octane render, ray tracing, volumetric lighting, hyper-realistic 3D",
    "Sketch": "hand-drawn sketch, pencil drawing, graphite, charcoal, artistic, hatching",
    "Cyberpunk": "neon lights, futuristic, dark rainy city, glowing accents, synthwave aesthetic",
    "Minimalist": "clean, simple, flat design, elegant, negative space, modern aesthetic"
}

# Negative prompt to suppress common artifacts
NEGATIVE_PROMPT = (
    "blurry, low quality, worst quality, low resolution, pixelated, "
    "jpeg artifacts, noisy, grainy, deformed, ugly, disfigured, "
    "bad anatomy, bad proportions, extra limbs, mutated hands, "
    "poorly drawn face, out of frame, watermark, text, logo, "
    "signature, cropped, oversaturated"
)

# Path to the standalone worker script
WORKER_SCRIPT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sdxl_worker.py")


@AgentRegistry.register
class VisualAgent(BaseAgent):
    """Unified Visual Agent — analyzes, generates, and edits images.
    
    Modes:
      - ANALYZE: Uses multimodal LLM to describe/explain uploaded images
      - GENERATE: Creates new images from text prompts via SDXL subprocess
      - EDIT: Transforms existing images using img2img pipeline
    """
    
    DEFAULT_ROLE = "Unified visual intelligence — analyzes, generates, and edits images."
    
    def __init__(self, **kwargs):
        super().__init__(
            name="VisualAgent",
            role=self.DEFAULT_ROLE,
            system_prompt="You are a friendly and talkative visual assistant. You can analyze images, generate stunning new visuals, and edit existing ones while being a helpful partner in the creative process.",
            **kwargs
        )
        self.output_dir = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "..", "storage", "images"
        )
        os.makedirs(self.output_dir, exist_ok=True)

    # ── Vision helpers ────────────────────────────────────────────────
    def _encode_image(self, image_path: str) -> str:
        """Encode image to base64 for multimodal LLM."""
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")

    def _detect_mode(self, prompt: str, has_image: bool) -> str:
        """Detect whether user wants ANALYZE, EDIT, GENERATE, or just CHAT."""
        prompt_lower = prompt.lower()
        
        # If there's an image attached, it's either edit or analyze
        if has_image:
            if any(kw in prompt_lower for kw in EDIT_KEYWORDS):
                return "edit"
            return "analyze"
        
        # Strip conversation context to get the actual user message
        clean = prompt_lower
        if "current request:" in clean:
            clean = clean.split("current request:")[-1].split("note:")[0].strip()
        
        # Explicit generation keywords — user clearly wants an image
        GENERATE_KEYWORDS = [
            "generate", "create", "draw", "paint", "make me", "make an",
            "make a", "design", "render", "sketch", "illustrate",
            "show me", "picture of", "image of", "photo of",
            "portrait of", "landscape of", "scene of", "artwork",
            "wallpaper", "logo", "icon", "poster", "banner",
        ]
        if any(kw in clean for kw in GENERATE_KEYWORDS):
            return "generate"
        
        # If the message is short and casual, it's probably chat
        # (e.g., "good job", "thanks", "hello", "nice", "wow", "cool")
        CHAT_INDICATORS = [
            "good", "nice", "great", "thanks", "thank", "hello", "hi",
            "hey", "wow", "cool", "awesome", "love it", "perfect",
            "amazing", "beautiful", "well done", "ok", "okay",
            "what can you", "who are you", "help", "how are",
            "sure", "yes", "no", "please", "sorry", "lol", "haha",
            "?", "!", "bruh", "bro", "dude", "man", "yo",
        ]
        if len(clean.split()) <= 8 and any(kw in clean for kw in CHAT_INDICATORS):
            return "chat"
        
        # If the message is very short (1-3 words) without clear visual content, chat
        if len(clean.split()) <= 3 and not any(c.isdigit() for c in clean):
            return "chat"
        
        # Default: assume they want to generate
        return "generate"

    async def _analyze_image(self, image_path: str, prompt: str) -> Dict[str, Any]:
        """Analyze an image using the multimodal LLM."""
        logger.info(f"👁️ VisualAgent ANALYZE mode: {image_path}")
        base64_image = self._encode_image(image_path)
        
        response = self.llm.generate(
            prompt=prompt,
            model=VISION_MODEL,
            images=[base64_image],
            use_cache=False
        )
        
        if not response:
            raise RuntimeError("Vision model failed to return a response.")
        
        return self.format_output({
            "analysis": response,
            "image_path": image_path,
            "model_used": VISION_MODEL,
            "mode": "analyze"
        })

    async def _chat_response(self, prompt: str, input_data: dict) -> Dict[str, Any]:
        """Generate a friendly conversational response using the LLM."""
        user_msg = input_data.get("user_message") or prompt
        # Strip conversation context
        if "Current request:" in user_msg:
            user_msg = user_msg.split("Current request:")[-1].split("Note:")[0].strip()
        
        chat_prompt = f"""You are the VisualAgent — a friendly, creative AI artist. 
The user just said: "{user_msg}"

Respond naturally and warmly in 1-3 sentences. Be conversational, encouraging, and a little playful.
If they complimented your work, thank them genuinely.
If they're asking about your capabilities, briefly mention you can generate images, analyze photos, and edit visuals.
Do NOT generate or describe an image unless they explicitly ask for one.
Keep it short and human-like."""
        
        try:
            response = self.llm.generate(
                prompt=chat_prompt,
                model="meta-llama/llama-4-maverick-17b-128e-instruct",
                use_cache=False
            )
            if response:
                return self.format_output(response.strip())
        except Exception as e:
            logger.error(f"Chat response error: {e}")
        
        # Fallback
        return self.format_output("Thanks! 😊 Let me know if you'd like me to create, analyze, or edit any images!")

    def _build_prompt(self, raw_prompt: str, style: str = None) -> str:
        """Strips command prefixes and enhances the prompt with quality boosters and style presets."""
        prompt = raw_prompt.strip()
        prompt_lower = prompt.lower()
        
        # Strip common prefixes
        for prefix in [
            "generate an image of ", "create an image of ", 
            "make an image of ", "make me an image of ",
            "draw ", "paint ", "generate ", "create ", "make ",
            "show me ", "give me ", "i want ", "can you ",
        ]:
            if prompt_lower.startswith(prefix):
                prompt = prompt[len(prefix):]
                prompt_lower = prompt.lower()
                break
        
        # Build prompt
        enhanced = prompt.strip()
        
        # Add style preset if valid
        if style and style in STYLE_PRESETS:
            enhanced = f"{enhanced}, {STYLE_PRESETS[style]}"
        
        # Add universal quality suffix if not already present
        if not any(kw in prompt_lower for kw in ["8k", "masterpiece", "best quality", "highly detailed"]):
            enhanced += QUALITY_SUFFIX
        
        return enhanced

    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Unified execute — routes to ANALYZE, EDIT, or GENERATE based on input."""
        self.start_execution()
        
        raw_prompt = (
            input_data.get("original_prompt") or
            input_data.get("prompt") or
            input_data.get("task") or 
            input_data.get("topic", "a beautiful landscape")
        )
        
        # Resolve image from file_id or image_path
        file_id = input_data.get("file_id")
        image_path = input_data.get("image_path") or input_data.get("init_image")
        if file_id and not image_path:
            image_path = self._get_file_path(file_id)
        
        has_image = bool(image_path and os.path.exists(str(image_path)))
        mode = self._detect_mode(raw_prompt, has_image)
        
        logger.info(f"🎨 VisualAgent mode={mode}, has_image={has_image}, prompt='{raw_prompt[:60]}...'")
        
        try:
            # ── CHAT MODE (casual conversation) ──
            if mode == "chat":
                logger.info("💬 VisualAgent CHAT mode — responding conversationally")
                result = await self._chat_response(raw_prompt, input_data)
                self.end_execution()
                return result
            
            # ── ANALYZE MODE ──
            if mode == "analyze":
                result = await self._analyze_image(image_path, raw_prompt)
                self.end_execution()
                return result
            
            # ── EDIT MODE (img2img) ──
            if mode == "edit":
                input_data["init_image"] = image_path
                input_data["strength"] = input_data.get("strength", 0.65)
                # Fall through to generation with init_image set

            # ── GENERATE / EDIT MODE (SDXL subprocess) ──
            style = input_data.get("style")
            sd_prompt = self._build_prompt(raw_prompt, style)

            # Check for cancellation before starting
            request_id = input_data.get("request_id")
            task_id = input_data.get("task_id")
            from services.cancellation_service import cancellation_service
            
            def is_cancelled():
                if request_id and cancellation_service.is_cancelled(request_id):
                    return True
                if task_id and cancellation_service.is_cancelled(f"task_{task_id}"):
                    return True
                return False

            if is_cancelled():
                return self.format_output(None, status="error", error="Request cancelled by user")

            # Prepare output file
            filename = f"gen_{int(time.time())}.png"
            filepath = os.path.join(self.output_dir, filename)
            
            # Find the Python executable (same venv we're running in)
            python_exe = sys.executable
            
            logger.info(f"🖼️ Spawning SDXL subprocess for: '{sd_prompt[:80]}...'")
            logger.info(f"🐍 Using Python: {python_exe}")
            
            import anyio
            
            # Prepare worker arguments
            worker_args = [
                python_exe, WORKER_SCRIPT,
                "--prompt", sd_prompt,
                "--negative", NEGATIVE_PROMPT,
                "--output", filepath,
            ]
            
            # Handle init_image for image-to-image tasks
            init_image_input = input_data.get("init_image")
            if init_image_input:
                init_path = None
                if isinstance(init_image_input, int) or (isinstance(init_image_input, str) and init_image_input.isdigit()):
                    init_path = self._get_file_path(int(init_image_input))
                elif isinstance(init_image_input, str) and os.path.exists(init_image_input):
                    init_path = init_image_input
                
                if init_path:
                    worker_args.extend(["--init_image", init_path])
                    strength = input_data.get("strength", 0.75)
                    worker_args.extend(["--strength", str(strength)])
                    logger.info(f"🎨 Running IMMG2IMG with init_image: {init_path}")

            def run_worker():
                """Run the SDXL worker in a subprocess."""
                proc = subprocess.Popen(
                    worker_args,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    cwd=os.path.dirname(WORKER_SCRIPT),
                )
                
                # Stream output to our logger
                output_lines = []
                for line in proc.stdout:
                    line = line.strip()
                    if line:
                        logger.info(f"  {line}")
                        output_lines.append(line)
                        
                        # Check cancellation during generation
                        if is_cancelled():
                            logger.info("🛑 Cancellation detected — killing worker subprocess")
                            proc.kill()
                            raise RuntimeError("Operation cancelled by user")
                
                proc.wait()
                return proc.returncode, output_lines
            
            inf_start = time.time()
            returncode, output_lines = await anyio.to_thread.run_sync(run_worker)
            inf_duration = time.time() - inf_start
            
            if returncode != 0:
                error_msg = "\n".join(output_lines[-5:]) if output_lines else "Unknown worker error"
                raise RuntimeError(f"SDXL worker failed (exit code {returncode}): {error_msg}")
            
            if not os.path.exists(filepath):
                raise RuntimeError("Worker completed but image file was not created")
            
            logger.info(f"✨ Image generated in {inf_duration:.1f}s (subprocess exited, RAM freed!)")
            
            relative_path = f"/storage/images/{filename}"
            print(f"✅ Image saved: {relative_path}")
            
            # Save to Database for Image Gallery History
            if self.db:
                try:
                    from models.file import File
                    db_file = File(
                        user_id=input_data.get("user_id", 1), # Default to test user
                        project_id=input_data.get("project_id"),
                        task_id=input_data.get("task_id"),
                        filename=filename,
                        original_filename=f"SDXL: {raw_prompt[:50]}...",
                        file_path=filepath,
                        file_size=os.path.getsize(filepath),
                        mime_type="image/png"
                    )
                    self.db.add(db_file)
                    self.db.commit()
                    logger.info(f"💾 Image record saved to DB (ID: {db_file.id})")
                except Exception as db_err:
                    logger.error(f"⚠️ Failed to save image to DB: {db_err}")
            
            # Use the clean user message for alt text, not the full context prompt
            clean_description = input_data.get("user_message") or raw_prompt
            # Strip conversation context if it leaked into the message
            if "Previous conversation:" in clean_description:
                parts = clean_description.split("Current request:")
                if len(parts) > 1:
                    clean_description = parts[-1].split("Note:")[0].strip()
            # Keep alt text short
            alt_text = clean_description[:100].strip()
            
            response_text = f"Here's your generated image:\n\n![{alt_text}]({relative_path})"
            
            return self.format_output(response_text)
            
        except Exception as e:
            print(f"❌ VisualAgent Error: {str(e)}")
            import traceback
            traceback.print_exc()
            return {
                "status": "failed",
                "error": str(e),
                "agent": self.name
            }
