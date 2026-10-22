"""Run:  python check_setup.py   -> tells you exactly what is wrong."""
import importlib, os, shutil, sys
from pathlib import Path

ok = True
def say(good, msg):
    global ok
    ok = ok and good
    print(("[ OK ] " if good else "[FAIL] ") + msg)

say(sys.version_info >= (3, 9), f"Python {sys.version.split()[0]}")
for mod, pip in [("anthropic","anthropic"),("dotenv","python-dotenv"),("streamlit","streamlit"),
                 ("cv2","opencv-python-headless"),("pytesseract","pytesseract"),("numpy","numpy"),
                 ("docx","python-docx"),("bs4","beautifulsoup4"),("requests","requests"),
                 ("sklearn","scikit-learn"),("joblib","joblib")]:
    try: importlib.import_module(mod); say(True, f"package {pip}")
    except Exception: say(False, f"package {pip} missing -> pip install {pip}")
try: importlib.import_module("fitz"); say(True, "package pymupdf")
except Exception:
    try: importlib.import_module("pypdf"); say(True, "PDF reading via pypdf")
    except Exception: say(False, "no PDF library -> pip install pymupdf")

win = Path(r"C:\Program Files\Tesseract-OCR\tesseract.exe")
say(bool(shutil.which("tesseract")) or win.exists(),
    "Tesseract OCR program found" if (shutil.which("tesseract") or win.exists())
    else "Tesseract OCR not installed (needed only for image text): https://github.com/UB-Mannheim/tesseract/wiki")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
env = Path(__file__).with_name(".env")
say(env.exists(), ".env file exists" if env.exists() else ".env missing -> copy .env.example to .env")
try:
    from core.config import ask, MODEL
    print(f"       model = {MODEL}")
    print("[ OK ] API test reply:", ask([{"role": "user", "content": "Say OK"}], max_tokens=10))
except Exception as e:
    say(False, f"API call failed: {e}")
print("\nALL GOOD - run:  streamlit run ui/app.py" if ok else "\nFix the [FAIL] lines above, then run this again.")
