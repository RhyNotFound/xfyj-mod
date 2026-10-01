"""Cross-checks the identifiers that tie the mod's Java, data and assets together.

No JDK is available in this environment, so this validates the wiring that a
compiler could not check anyway: item ids, sound event ids, jukebox song ids,
model/texture paths and language keys.
"""

import glob
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NS = "xfyj"
ITEM_PATH = "music_disc_xfyj"
SONG_PATH = ITEM_PATH
SOUND_PATH = "music_disc.xfyj"


def read(relative: str) -> str:
    with open(os.path.join(ROOT, relative), encoding="utf-8") as handle:
        return handle.read()


def load(relative: str):
    return json.loads(read(relative))


def main() -> int:
    problems = []
    checks = 0

    def expect(condition: bool, message: str) -> None:
        nonlocal checks
        checks += 1
        if not condition:
            problems.append(message)

    java = read("src/main/java/com/xfyj/registry/ModItems.java")
    java_sounds = read("src/main/java/com/xfyj/registry/ModSounds.java")
    java_main = read("src/main/java/com/xfyj/Xfyj.java")

    # Identifier wiring: the ids in code must match the resource file names.
    expect(f'DISC_PATH = "{ITEM_PATH}"' in java, "ModItems.DISC_PATH changed")
    expect(f'DISC_SOUND_PATH = "{SOUND_PATH}"' in java_sounds, "ModSounds.DISC_SOUND_PATH changed")
    expect('MOD_ID = "xfyj"' in java_main, "mod id changed")

    # The jukebox song file must live under exactly the path the code asks for.
    expect(f"ResourceKey.create(Registries.JUKEBOX_SONG, Xfyj.id(DISC_PATH))" in java,
           "the song key no longer points at the item path, so the data file would not match")
    expect(f"jukebox_song/{SONG_PATH}.json" in java or SONG_PATH == ITEM_PATH,
           "song data file path and code path disagree")

    # Vanilla creative tab id used for the tab injection.
    expect('"minecraft", "tools_and_utilities"' in java,
           "the creative tab injection no longer targets tools_and_utilities")
    expect("CreativeModeTabEvents.modifyOutputEvent" in java,
           "the creative tab injection is not using CreativeModeTabEvents")

    # Minecraft 26.2 renamed these; keep the old names out of the sources.
    for path in ("src/main/java/com/xfyj/registry/ModItems.java",
                 "src/main/java/com/xfyj/registry/ModSounds.java"):
        source = read(path)
        expect("net.minecraft.resources.RegistryKey" not in source,
               f"{path} still imports RegistryKey, which does not exist in 26.2")
        expect("fabric.api.itemgroup" not in source,
               f"{path} still imports the removed Fabric item group package")

    # Jukebox song data file: path, sound id, description key, length.
    song_file = f"src/main/resources/data/{NS}/jukebox_song/{SONG_PATH}.json"
    song = load(song_file)
    expect(song["sound_event"]["sound_id"] == f"{NS}:{SOUND_PATH}",
           f"jukebox song sound_id is {song['sound_event']['sound_id']}")
    expect(song["description"]["translate"] == f"jukebox_song.{NS}.{SONG_PATH}",
           "jukebox song description key mismatch")
    expect(song["comparator_output"] == 15, "comparator output is not 15")

    # sounds.json: event name and the referenced ogg.
    sounds = load(f"src/main/resources/assets/{NS}/sounds.json")
    expect(SOUND_PATH in sounds, f"sounds.json has no '{SOUND_PATH}' event")
    entry = sounds[SOUND_PATH]["sounds"][0]
    expect(entry["name"] == f"{NS}:records/xfyj", f"sound file reference is {entry['name']}")
    expect(entry.get("stream") is True, "the record should be streamed, not preloaded")
    expect(sounds[SOUND_PATH].get("subtitle") == f"subtitles.{NS}.{ITEM_PATH}",
           "sounds.json subtitle key mismatch")
    ogg = f"src/main/resources/assets/{NS}/sounds/records/xfyj.ogg"
    expect(os.path.exists(os.path.join(ROOT, ogg)), f"missing audio file {ogg}")

    # Item definition + model + texture.
    item_def = load(f"src/main/resources/assets/{NS}/items/{ITEM_PATH}.json")
    model_id = item_def["model"]["model"]
    expect(item_def["model"]["type"] == "minecraft:model", "item definition is not a plain model")
    expect(model_id == f"{NS}:item/{ITEM_PATH}", f"item definition points at {model_id}")

    model = load(f"src/main/resources/assets/{NS}/models/item/{ITEM_PATH}.json")
    expect(model["parent"] == "minecraft:item/template_music_disc", "model parent changed")
    texture = model["textures"]["layer0"]
    expect(texture == f"{NS}:item/{ITEM_PATH}", f"model texture is {texture}")
    expect(os.path.exists(os.path.join(ROOT, f"src/main/resources/assets/{NS}/textures/item/{ITEM_PATH}.png")),
           "disc texture is missing")

    # Language keys used anywhere in the resources must exist in both locales.
    locales = {}
    for locale in ("en_us", "zh_cn"):
        locales[locale] = load(f"src/main/resources/assets/{NS}/lang/{locale}.json")

    needed = {
        f"item.{NS}.{ITEM_PATH}",
        f"item.{NS}.{ITEM_PATH}.desc",
        f"jukebox_song.{NS}.{SONG_PATH}",
    }
    if "subtitle" in sounds[SOUND_PATH]:
        needed.add(sounds[SOUND_PATH]["subtitle"])

    for locale, table in locales.items():
        for key in sorted(needed):
            expect(key in table, f"{locale}.json is missing '{key}'")

    # The disc must actually be titled as requested.
    title = "S9ryne - 星拂云锦 feat. koi"
    for locale, table in locales.items():
        expect(table.get(f"item.{NS}.{ITEM_PATH}.desc") == title,
               f"{locale}.json tooltip line is {table.get(f'item.{NS}.{ITEM_PATH}.desc')!r}")
        expect(table.get(f"jukebox_song.{NS}.{SONG_PATH}") == title,
               f"{locale}.json now-playing line is not the requested title")

    # fabric.mod.json entrypoint must exist on disk.
    mod_json = load("src/main/resources/fabric.mod.json")
    entrypoint = mod_json["entrypoints"]["main"][0]
    entry_path = os.path.join(ROOT, "src/main/java", *entrypoint.split(".")) + ".java"
    expect(os.path.exists(entry_path), f"entrypoint class {entrypoint} has no source file")
    expect(mod_json["id"] == NS, "mod id in fabric.mod.json changed")

    # Every JSON file must parse, and no stale template leftovers may remain.
    for path in glob.glob(os.path.join(ROOT, "src", "**", "*.json"), recursive=True):
        try:
            json.load(open(path, encoding="utf-8"))
        except Exception as error:  # noqa: BLE001
            problems.append(f"{os.path.relpath(path, ROOT)}: {error}")

    leftovers = [p for p in glob.glob(os.path.join(ROOT, "src", "**", "*"), recursive=True)
                 if re.search(r"(Example|example)", os.path.basename(p))]
    expect(not leftovers, f"template leftovers still present: {leftovers}")

    print(f"{checks} checks run")
    if problems:
        print(f"{len(problems)} problem(s):")
        for problem in problems:
            print(f"  - {problem}")
        return 1

    print("all identifier cross-references are consistent")
    return 0


if __name__ == "__main__":
    sys.exit(main())
