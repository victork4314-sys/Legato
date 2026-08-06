#!/usr/bin/env python3
"""Apply the audited Legato direct-command patch to pinned whisper.cpp source."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

PATCH_VERSION = "legato-direct-command-v1"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected exactly one match, found {count}")
    return text.replace(old, new, 1)


def patch_tree(root: Path) -> dict[str, object]:
    cpp_path = root / "examples" / "command.wasm" / "emscripten.cpp"
    cmake_path = root / "examples" / "command.wasm" / "CMakeLists.txt"
    if not cpp_path.is_file() or not cmake_path.is_file():
        raise RuntimeError("Pinned whisper.cpp command.wasm sources are missing")

    cpp = cpp_path.read_text()
    cmake = cmake_path.read_text()

    cpp = replace_once(
        cpp,
        "constexpr int N_THREAD = 8;",
        "constexpr int N_THREAD = 4; // LEGATO_DIRECT_COMMANDS",
        "worker thread count",
    )
    cpp = replace_once(
        cpp,
        "    bool have_prompt  = false;",
        "    bool have_prompt  = true;  // LEGATO_DIRECT_COMMANDS: no wake phrase",
        "wake phrase state",
    )
    cpp = replace_once(
        cpp,
        "    bool ask_prompt   = true;",
        "    bool ask_prompt   = false; // LEGATO_DIRECT_COMMANDS: listen immediately",
        "wake phrase request",
    )
    cpp = replace_once(
        cpp,
        "    std::vector<float> pcmf32_prompt;\n\n    const std::string k_prompt",
        "    std::vector<float> pcmf32_prompt;\n\n    command_set_status(\"Waiting for voice commands ...\");\n\n    const std::string k_prompt",
        "initial direct-listening status",
    )

    start_marker = "                    // prepend the prompt audio"
    end_marker = "                    const std::string command = ::trim(txt.substr(best_len));"
    start = cpp.find(start_marker)
    end = cpp.find(end_marker, start)
    if start < 0 or end < 0:
        raise RuntimeError("wake-phrase command extraction block was not found")
    end += len(end_marker)
    replacement = """                    // LEGATO_DIRECT_COMMANDS: transcribe the spoken command directly.
                    const std::string command = ::trim(
                        ::command_transcribe(ctx, wparams, pcmf32_cur, prob, t_ms));"""
    cpp = cpp[:start] + replacement + cpp[end:]

    cmake = replace_once(
        cmake,
        "-s PTHREAD_POOL_SIZE=8",
        "-s PTHREAD_POOL_SIZE=4",
        "pthread pool size",
    )
    cmake = replace_once(
        cmake,
        "-s INITIAL_MEMORY=1024MB",
        "-s INITIAL_MEMORY=512MB",
        "initial memory",
    )
    cmake = replace_once(
        cmake,
        "-s TOTAL_MEMORY=1024MB",
        "-s TOTAL_MEMORY=512MB",
        "total memory",
    )

    required_bindings = (
        'emscripten::function("init"',
        'emscripten::function("free"',
        'emscripten::function("set_audio"',
        'emscripten::function("get_transcribed"',
        'emscripten::function("get_status"',
        'emscripten::function("set_status"',
    )
    for binding in required_bindings:
        if binding not in cpp:
            raise RuntimeError(f"required command binding is missing: {binding}")

    if "LEGATO_DIRECT_COMMANDS" not in cpp:
        raise RuntimeError("direct-command marker was not applied")
    if "const std::string command = ::trim(txt.substr(best_len));" in cpp:
        raise RuntimeError("wake-phrase stripping remained after patch")

    cpp_path.write_text(cpp)
    cmake_path.write_text(cmake)

    result = {
        "patchVersion": PATCH_VERSION,
        "wakePhraseRequired": False,
        "threads": 4,
        "pthreadPool": 4,
        "initialMemoryMB": 512,
        "cppSha256": hashlib.sha256(cpp.encode()).hexdigest(),
        "cmakeSha256": hashlib.sha256(cmake.encode()).hexdigest(),
    }
    (root / "legato-direct-command-build.json").write_text(
        json.dumps(result, indent=2) + "\n"
    )
    return result


def self_test() -> None:
    if PATCH_VERSION != "legato-direct-command-v1":
        raise RuntimeError("unexpected patch version")
    sample = "one target one"
    assert replace_once(sample, "target", "patched", "self-test") == "one patched one"
    try:
        replace_once("twice twice", "twice", "x", "self-test duplicate")
    except RuntimeError:
        pass
    else:
        raise RuntimeError("duplicate replacement self-test did not fail closed")


def main(argv: list[str]) -> int:
    if len(argv) == 2 and argv[1] == "--self-test":
        self_test()
        print("patch self-test passed")
        return 0
    if len(argv) != 2:
        print(f"usage: {argv[0]} WHISPER_CPP_ROOT | --self-test", file=sys.stderr)
        return 2
    result = patch_tree(Path(argv[1]))
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
