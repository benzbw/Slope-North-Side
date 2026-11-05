# -*- coding: utf-8 -*-
"""วาดภาพปกด้วย AI บนเครื่องตัวเอง (SD-Turbo) ไม่ต้องใช้บริการออนไลน์ ครั้งแรกดาวน์โหลดโมเดล ~2.5GB"""
import io, os, sys, time, threading
_P = {}
_L = threading.Lock()
MODEL = os.environ.get("IMG_MODEL", "stabilityai/sd-turbo")

def pipe():
    with _L:
        if "p" not in _P:
            import torch
            from diffusers import AutoPipelineForText2Image
            torch.set_num_threads(max(1, os.cpu_count() or 1))
            p = AutoPipelineForText2Image.from_pretrained(MODEL, torch_dtype=torch.float32)
            p.set_progress_bar_config(disable=True)
            try:  # ตัวถอดภาพขนาดเล็ก เร็วกว่าหลายเท่าบน CPU
                from diffusers import AutoencoderTiny
                p.vae = AutoencoderTiny.from_pretrained("madebyollin/taesd", torch_dtype=torch.float32)
            except Exception as e:
                print("taesd ใช้ไม่ได้", e)
            try: p.enable_attention_slicing()
            except Exception: pass
            _P["p"] = p
        return _P["p"]

def generate(prompt, seed=0, steps=2, size=512):
    import torch
    p = pipe()
    g = torch.Generator("cpu").manual_seed(int(seed) % (2 ** 31))
    im = p(prompt=prompt[:600], num_inference_steps=int(steps), guidance_scale=0.0, width=size, height=size, generator=g).images[0]
    b = io.BytesIO(); im.save(b, "PNG"); return b.getvalue()

if __name__ == "__main__":
    t = time.time()
    data = generate(sys.argv[1] if len(sys.argv) > 1 else "album cover art, neon red light, rainy city night, cinematic, no text", 7)
    open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "img_test.png"), "wb").write(data)
    print("ok", round(time.time() - t, 1), "s", len(data), "bytes", flush=True)
