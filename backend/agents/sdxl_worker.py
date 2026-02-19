"""Standalone SDXL Worker — runs in a subprocess, exits after generation.

Usage:
    python sdxl_worker.py --prompt "a cute panda" --negative "blurry" --output "path/to/image.png"

When this process exits, ALL model memory (~8GB) is returned to the OS.
"""

import argparse
import sys
import time
import os
import torch
from PIL import Image
from diffusers import (
    StableDiffusionXLPipeline, 
    StableDiffusionXLImg2ImgPipeline,
    DPMSolverMultistepScheduler
)

MODEL_ID = "stabilityai/stable-diffusion-xl-base-1.0"


def generate(prompt: str, negative_prompt: str, output_path: str, init_image_path: str = None, strength: float = 0.75) -> None:
    """Load model, generate image, save, and exit."""
    start = time.time()

    device = "cuda" if torch.cuda.is_available() else "cpu"
    torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32

    # Choose pipeline based on mode
    if init_image_path and os.path.exists(init_image_path):
        print(f"[WORKER] Mode: Image-to-Image (Editing)", flush=True)
        print(f"[WORKER] Loading SDXL Img2Img model...", flush=True)
        
        # Load the image
        init_image = Image.open(init_image_path).convert("RGB")
        # Resize to 1024x1024 for SDXL
        init_image = init_image.resize((1024, 1024))
        
        pipe = StableDiffusionXLImg2ImgPipeline.from_pretrained(
            MODEL_ID,
            torch_dtype=torch_dtype,
            variant="fp16" if torch.cuda.is_available() else None,
            use_safetensors=True,
        )
    else:
        print(f"[WORKER] Mode: Text-to-Image (Generation)", flush=True)
        print(f"[WORKER] Loading SDXL Base model...", flush=True)
        pipe = StableDiffusionXLPipeline.from_pretrained(
            MODEL_ID,
            torch_dtype=torch_dtype,
            variant="fp16" if torch.cuda.is_available() else None,
            use_safetensors=True,
        )

    pipe.scheduler = DPMSolverMultistepScheduler.from_config(
        pipe.scheduler.config,
        algorithm_type="dpmsolver++",
        use_karras_sigmas=True,
    )

    pipe.to(device)
    
    # Memory optimizations
    if device == "cuda":
        pipe.enable_model_cpu_offload()

    load_time = time.time() - start
    print(f"[WORKER] Pipeline ready in {load_time:.1f}s", flush=True)

    print(f"[WORKER] Processing: '{prompt[:80]}...'", flush=True)
    inf_start = time.time()

    with torch.inference_mode():
        if init_image_path:
            result = pipe(
                prompt=prompt,
                negative_prompt=negative_prompt,
                image=init_image,
                strength=strength,
                num_inference_steps=30,
                guidance_scale=7.5,
            )
        else:
            result = pipe(
                prompt=prompt,
                negative_prompt=negative_prompt,
                num_inference_steps=30,
                guidance_scale=7.5,
                width=1024,
                height=1024,
            )

    image = result.images[0]
    image.save(output_path, quality=95)

    total = time.time() - start
    inf_time = time.time() - inf_start
    print(f"[WORKER] Output saved to {output_path}", flush=True)
    print(f"[WORKER] Inference: {inf_time:.1f}s | Total: {total:.1f}s", flush=True)
    print("[WORKER] SUCCESS", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SDXL Subprocess Worker")
    parser.add_argument("--prompt", required=True, help="Prompt")
    parser.add_argument("--negative", default="", help="Negative prompt")
    parser.add_argument("--output", required=True, help="Output path")
    parser.add_argument("--init_image", default=None, help="Initial image for img2img")
    parser.add_argument("--strength", type=float, default=0.75, help="Transformation strength")
    args = parser.parse_args()

    try:
        generate(args.prompt, args.negative, args.output, args.init_image, args.strength)
        sys.exit(0)
    except Exception as e:
        print(f"[WORKER] ERROR: {e}", flush=True)
        sys.exit(1)
