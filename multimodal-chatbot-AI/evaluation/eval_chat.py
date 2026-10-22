"""Chat accuracy: checks whether answers contain expected keywords.
Run: python -m evaluation.eval_chat   (add more questions to test_questions.json)"""
import json
import os

from modules.module1_chat import reply

path = os.path.join(os.path.dirname(__file__), "test_questions.json")
items = json.load(open(path, encoding="utf-8"))
correct = 0
for it in items:
    ans = reply([], it["question"]).lower()
    ok = all(k.lower() in ans for k in it["keywords"])
    correct += ok
    print("PASS" if ok else "FAIL", "-", it["question"])
print(f"\nChat accuracy: {correct}/{len(items)} = {100 * correct / len(items):.0f}%")
