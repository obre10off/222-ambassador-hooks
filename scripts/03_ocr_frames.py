"""Step 3: OCR every frame with RapidOCR (ONNX, CPU). Output: work/ocr.json
{frame_filename: [[box, text, confidence], ...]}. About 4-5 minutes for ~750 frames on 8 cores.
"""
import json
import os
from concurrent.futures import ProcessPoolExecutor

from common import FRAMES, OCR_JSON


def work(paths):
    from rapidocr_onnxruntime import RapidOCR
    eng = RapidOCR()
    out = {}
    for p in paths:
        result, _ = eng(p)
        out[os.path.basename(p)] = [(box, text, float(score)) for box, text, score in (result or [])]
    return out


def main():
    files = sorted(str(p) for p in FRAMES.glob("*.jpg"))
    n = int(os.environ.get("HOOKS_PROCS", os.cpu_count() or 4))
    chunks = [files[i::n] for i in range(n)]
    res = {}
    with ProcessPoolExecutor(n) as ex:
        for part in ex.map(work, chunks):
            res.update(part)
    OCR_JSON.write_text(json.dumps(res))
    print(f"OCR'd {len(res)} frames -> {OCR_JSON}")


if __name__ == "__main__":
    main()
