"""OCR accuracy. Put images in evaluation/ocr_samples/ as name.png with the correct text in name.txt.
Run: python -m evaluation.eval_ocr"""
import glob
import os


def edit_distance(a, b):
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]


def cer(truth, pred):
    return edit_distance(truth, pred) / max(len(truth), 1)


def wer(truth, pred):
    t, p = truth.split(), pred.split()
    return edit_distance(t, p) / max(len(t), 1)


if __name__ == "__main__":
    from modules.module5_ocr import extract_text

    folder = os.path.join(os.path.dirname(__file__), "ocr_samples")
    cers, wers = [], []
    for img in sorted(glob.glob(os.path.join(folder, "*.[pj][np]g"))):
        txt = os.path.splitext(img)[0] + ".txt"
        if not os.path.exists(txt):
            continue
        truth = open(txt, encoding="utf-8").read().strip()
        pred, conf, engine = extract_text(img)
        cers.append(cer(truth, pred)); wers.append(wer(truth, pred))
        print(f"{os.path.basename(img)}: CER={cers[-1]:.2%} WER={wers[-1]:.2%} ({engine})")
    if cers:
        print(f"\nAverage CER: {sum(cers)/len(cers):.2%} | Average WER: {sum(wers)/len(wers):.2%}")
    else:
        print("No samples found. Add name.png + name.txt pairs to evaluation/ocr_samples/")
