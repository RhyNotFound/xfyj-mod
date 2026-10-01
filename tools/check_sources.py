"""Cheap static sanity check for the Java sources.

No JDK is available in this environment, so this only verifies structural
integrity: balanced braces/parens, matching package and directory, and that
every imported type is actually referenced in the file body.
"""

import glob
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JAVA_ROOT = os.path.join(ROOT, "src", "main", "java")


def strip_literals(text: str) -> str:
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    text = re.sub(r"//[^\n]*", "", text)
    text = re.sub(r'"(?:\\.|[^"\\])*"', '""', text)
    text = re.sub(r"'(?:\\.|[^'\\])*'", "''", text)
    return text


def check(path: str) -> list[str]:
    problems = []
    raw = open(path, encoding="utf-8").read()
    code = strip_literals(raw)

    for opener, closer, label in (("{", "}", "brace"), ("(", ")", "paren"), ("[", "]", "bracket")):
        if code.count(opener) != code.count(closer):
            problems.append(f"{label} mismatch: {code.count(opener)} '{opener}' vs {code.count(closer)} '{closer}'")

    package = re.search(r"^package\s+([\w.]+);", raw, flags=re.M)
    relative = os.path.relpath(path, JAVA_ROOT).replace(os.sep, "/")
    expected = relative[: -len(".java")].rsplit("/", 1)[0].replace("/", ".")

    if package is None:
        problems.append("no package declaration")
    elif package.group(1) != expected:
        problems.append(f"package '{package.group(1)}' does not match directory '{expected}'")

    body = code.split("\n")
    body = "\n".join(line for line in body if not line.strip().startswith("import"))

    for imported in re.findall(r"^import\s+(?:static\s+)?([\w.]+);", raw, flags=re.M):
        simple = imported.rsplit(".", 1)[-1]
        if simple == "*":
            continue
        if not re.search(r"\b" + re.escape(simple) + r"\b", body):
            problems.append(f"unused import: {imported}")

    if raw.count("\t") and "    " in raw:
        problems.append("mixed tabs and 4-space indentation")

    return problems


def main() -> int:
    files = glob.glob(os.path.join(JAVA_ROOT, "**", "*.java"), recursive=True)
    failures = 0

    for path in sorted(files):
        problems = check(path)
        name = os.path.relpath(path, ROOT)

        if problems:
            failures += 1
            print(f"FAIL {name}")
            for problem in problems:
                print(f"       - {problem}")
        else:
            print(f"OK   {name}")

    print(f"\n{len(files)} files checked, {failures} with problems")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
