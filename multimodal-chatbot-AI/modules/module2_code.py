"""Code generation and execution helpers."""

import re
import subprocess
import sys
import tempfile

from core.config import ask


SYSTEM = (
    "You are an expert programmer. Write correct, clean, runnable Python code. "
    "Return the code in ONE ```python block, then a short explanation."
)


def extract_code(text):
    match = re.search(r"```python\s*(.*?)```", text or "", re.S)
    return match.group(1).strip() if match else None


def run_python(code, timeout=10):
    path = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", encoding="utf-8", delete=False) as file:
            file.write(code)
            path = file.name
        result = subprocess.run([sys.executable, "-I", path], capture_output=True, text=True, timeout=timeout)
        output = (result.stdout + result.stderr).strip()
        return result.returncode == 0, output
    except subprocess.TimeoutExpired:
        return False, f"Timed out after {timeout} seconds"
    except Exception as error:
        return False, str(error)
    finally:
        if path and sys.platform.startswith("win"):
            try:
                import os
                os.remove(path)
            except OSError:
                pass


def generate_code(request, history=None, max_fixes=2):
    messages = list(history or []) + [{"role": "user", "content": request}]
    answer = ask(messages, SYSTEM, 1500)
    for attempt in range(max_fixes + 1):
        code = extract_code(answer)
        if not code:
            return answer
        ok, output = run_python(code)
        if ok:
            return answer + "\n\nTest run passed.\nOutput:\n" + output[:1000]
        if attempt == max_fixes:
            return answer + "\n\nExecution failed after repair attempts.\nLast error:\n" + output[:1000]
        messages.extend([
            {"role": "assistant", "content": answer},
            {"role": "user", "content": "The generated Python code failed when executed.\n" + f"Error/output:\n{output[:3000]}\nReturn the complete corrected code in one ```python block, followed by a short explanation."},
        ])
        answer = ask(messages, SYSTEM, 1500)
    return answer
