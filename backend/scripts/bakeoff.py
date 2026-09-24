"""BUI-8 bake-off: compare Claude vs Gemini at writing valid CadQuery code.

Usage:
    uv run python scripts/bakeoff.py

Requires ANTHROPIC_API_KEY and GEMINI_API_KEY to be set (in .env or the
environment). For each test prompt and each provider, this asks for CadQuery
code, executes it in a fresh namespace, and checks that it produced a
non-empty `result` solid with actual volume. Prints a per-prompt pass/fail
and a final score per provider.
"""

import sys
import traceback
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.config import settings
from app.services import llm

SYSTEM_PROMPT = (Path(__file__).resolve().parent.parent / "app" / "prompts" / "cad_system_v1.txt").read_text()

TEST_PROMPTS = [
    "phone stand, 80 mm wide, holds a phone at a 60 degree angle",
    "hook for a 25 mm diameter bed rail, holds 2 kg",
    "simple open-top box, 100 mm x 60 mm x 40 mm, 2 mm walls",
    "cable clip that snaps onto a 6 mm diameter cable, mounts to a wall with one screw hole",
    "pen holder, cylindrical, 70 mm tall, 40 mm inner diameter, flat base",
    "wall bracket for a 20 mm x 20 mm square tube, two M4 screw holes",
    "coaster, 90 mm diameter, 5 mm deep recess for the cup, 3 mm base thickness",
    "small parametric gear, 12 teeth, 5 mm bore, 8 mm face width",
    "drawer handle, 96 mm screw spacing, standard M4 screws, ergonomic bar shape",
    "headphone stand, base 120 mm diameter, post 200 mm tall, hook top for headband",
]


@dataclass
class Result:
    prompt: str
    provider: str
    ok: bool
    error: str = ""


def try_execute(code: str) -> tuple[bool, str]:
    """Run generated code in an isolated namespace and check for a valid `result` solid."""
    namespace: dict = {}
    try:
        exec(code, namespace)  # noqa: S102 - deliberately executing model output for the bake-off
    except BaseException:  # noqa: BLE001 - any failure in untrusted model output counts as a fail
        return False, traceback.format_exc(limit=2)

    result = namespace.get("result")
    if result is None:
        return False, "no `result` variable produced"

    try:
        val = result.val()
        volume = val.Volume() if hasattr(val, "Volume") else val.Solids()[0].Volume()
    except BaseException:  # noqa: BLE001 - any failure means the solid isn't usable
        return False, "`result` is not a valid solid (couldn't compute volume)"

    if volume <= 0:
        return False, f"`result` has non-positive volume ({volume})"

    return True, ""


def strip_code_fences(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines)
    return text


def run_provider(provider: str) -> list[Result]:
    original_provider = settings.ai_provider
    settings.ai_provider = provider
    results = []
    try:
        for prompt in TEST_PROMPTS:
            try:
                response = llm.generate(SYSTEM_PROMPT, [{"role": "user", "content": prompt}])
                code = strip_code_fences(response.text)
                ok, error = try_execute(code)
            except BaseException:  # noqa: BLE001 - a provider/network failure counts as a fail
                ok, error = False, traceback.format_exc(limit=2)
            results.append(Result(prompt=prompt, provider=provider, ok=ok, error=error))
            print(f"[{provider}] {'PASS' if ok else 'FAIL'} - {prompt}")
            if not ok:
                print(f"    {error.strip().splitlines()[-1] if error else ''}")
    finally:
        settings.ai_provider = original_provider
    return results


def main() -> None:
    all_results: list[Result] = []
    if settings.anthropic_api_key:
        all_results += run_provider("anthropic")
    else:
        print("Skipping anthropic: ANTHROPIC_API_KEY not set")

    if settings.gemini_api_key:
        all_results += run_provider("gemini")
    else:
        print("Skipping gemini: GEMINI_API_KEY not set")

    print("\n--- Score ---")
    for provider in ("anthropic", "gemini"):
        provider_results = [r for r in all_results if r.provider == provider]
        if not provider_results:
            continue
        passed = sum(r.ok for r in provider_results)
        print(f"{provider}: {passed}/{len(provider_results)}")


if __name__ == "__main__":
    main()
