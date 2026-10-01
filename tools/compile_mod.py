"""Compile the mod's real sources offline, against the actual game jars.

The agent sandbox has no JDK, but the project machine does, and Loom has already
downloaded Minecraft 26.2 plus Fabric API. Running javac over src/main/java with
that classpath catches every API mistake before a full `gradlew build`.

Usage:  <python> tools/compile_mod.py
"""

import glob
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GRADLE_HOME = os.path.join(os.path.expanduser("~"), ".gradle")
JAVAC_CANDIDATES = (glob.glob(r"D:\Program Files\Java\jdk-*\bin\javac.exe")
                    + glob.glob(r"C:\Program Files\Java\jdk-*\bin\javac.exe"))

DEPENDENCY_PATTERNS = (
    "caches/modules-2/files-2.1/net.fabricmc.fabric-api/**/*.jar",
    "caches/modules-2/files-2.1/net.fabricmc/fabric-loader/**/*.jar",
    "caches/modules-2/files-2.1/com.mojang/datafixerupper/**/*.jar",
    "caches/modules-2/files-2.1/com.mojang/brigadier/**/*.jar",
    "caches/modules-2/files-2.1/com.mojang/authlib/**/*.jar",
    "caches/modules-2/files-2.1/com.mojang/logging/**/*.jar",
    "caches/modules-2/files-2.1/org.slf4j/**/*.jar",
    "caches/modules-2/files-2.1/org.jspecify/**/*.jar",
    "caches/modules-2/files-2.1/org.jetbrains/annotations/**/*.jar",
    "caches/modules-2/files-2.1/com.google.guava/**/*.jar",
    "caches/modules-2/files-2.1/com.google.code.gson/**/*.jar",
    "caches/modules-2/files-2.1/io.netty/**/*.jar",
    "caches/modules-2/files-2.1/org.apache.commons/**/*.jar",
    "caches/modules-2/files-2.1/commons-io/**/*.jar",
    "caches/modules-2/files-2.1/commons-codec/**/*.jar",
    "caches/modules-2/files-2.1/org.joml/**/*.jar",
    "caches/modules-2/files-2.1/org.apache.logging.log4j/**/*.jar",
)


def find(patterns) -> list[str]:
    found: list[str] = []
    for pattern in patterns:
        found.extend(glob.glob(os.path.join(GRADLE_HOME, pattern), recursive=True))
    return [path.replace("\\", "/") for path in found]


def main() -> int:
    if not JAVAC_CANDIDATES:
        print("no javac found; skipping offline compile check")
        return 0

    javac = JAVAC_CANDIDATES[0]

    minecraft = find(["caches/fabric-loom/*/minecraft-merged.jar"])
    if not minecraft:
        print("minecraft-merged.jar not found; run 'gradlew build' once first")
        return 1

    sources = [path.replace("\\", "/") for path in
               glob.glob(os.path.join(ROOT, "src", "main", "java", "**", "*.java"), recursive=True)]
    if not sources:
        print("no sources found")
        return 1

    classpath = ";".join(minecraft + find(DEPENDENCY_PATTERNS))
    output = f"{ROOT}/build/compile-check".replace("\\", "/")
    os.makedirs(output, exist_ok=True)

    argfile = os.path.join(os.environ.get("TEMP", "/tmp"), "xfyj_compile_args.txt")
    with open(argfile, "w", encoding="ascii") as handle:
        handle.write("\n".join([
            "--release 25",
            "-nowarn",
            "-encoding UTF-8",
            f'-classpath "{classpath}"',
            f'-d "{output}"',
        ] + [f'"{source}"' for source in sources]))

    print(f"javac     : {javac}")
    print(f"sources   : {len(sources)}")
    print(f"classpath : {len(minecraft + find(DEPENDENCY_PATTERNS))} jars")

    result = subprocess.run([javac, f"@{argfile}"], capture_output=True, text=True)
    sys.stdout.write(result.stdout)
    sys.stderr.write(result.stderr)

    if result.returncode == 0:
        print("OK - the mod compiles against real Minecraft 26.2 + Fabric API")
    else:
        print(f"FAILED with exit code {result.returncode}")

    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
