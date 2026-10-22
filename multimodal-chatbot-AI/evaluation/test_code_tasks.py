"""Code pass rate: generates code, appends asserts, runs it.
Run: python -m evaluation.test_code_tasks"""
from core.config import ask
from modules.module2_code import SYSTEM, extract_code, run_python

TASKS = [
    ("Write a function is_prime(n) that returns True if n is prime.",
     "assert is_prime(2) and is_prime(13) and not is_prime(1) and not is_prime(15)"),
    ("Write a function reverse_string(s) that returns the reversed string.",
     "assert reverse_string('abc') == 'cba' and reverse_string('') == ''"),
    ("Write a function factorial(n) returning n! for n >= 0.",
     "assert factorial(0) == 1 and factorial(5) == 120"),
    ("Write a function is_palindrome(s) ignoring case.",
     "assert is_palindrome('Madam') and not is_palindrome('hello')"),
    ("Write a function fibonacci(n) returning the n-th Fibonacci number (fibonacci(0)=0, fibonacci(1)=1).",
     "assert fibonacci(0) == 0 and fibonacci(1) == 1 and fibonacci(10) == 55"),
]

passed = 0
for prompt, test in TASKS:
    code = extract_code(ask([{"role": "user", "content": prompt}], SYSTEM, 1500))
    ok, out = run_python(code + "\n" + test) if code else (False, "no code")
    passed += ok
    print("PASS" if ok else "FAIL", "-", prompt[:60])
print(f"\nCode pass rate: {passed}/{len(TASKS)} = {100 * passed / len(TASKS):.0f}%")
