#!/usr/bin/env python3
from __future__ import annotations

import shutil
import sys
from pathlib import Path

SKILL_NAME = "tuxido"


def get_skill_source() -> Path | None:
    try:
        import tuxido

        package_dir = Path(tuxido.__file__).parent
        skill_file = package_dir / "skills" / SKILL_NAME / "SKILL.md"
        if skill_file.exists():
            return skill_file
    except ImportError:
        pass

    dev_skill = Path(__file__).parent.parent / "src" / "tuxido" / "skills" / SKILL_NAME / "SKILL.md"
    if dev_skill.exists():
        return dev_skill

    return None


def get_destinations() -> list[Path]:
    home = Path.home()
    cwd = Path.cwd()

    return [
        cwd / ".claude" / "skills" / SKILL_NAME,
        cwd / ".opencode" / "skills" / SKILL_NAME,
        cwd / ".agents" / "skills" / SKILL_NAME,
        home / ".claude" / "skills" / SKILL_NAME,
        home / ".config" / "opencode" / "skills" / SKILL_NAME,
        home / ".agents" / "skills" / SKILL_NAME,
    ]


def install_skill() -> bool:
    source = get_skill_source()
    if not source:
        print("SKILL.md not found, skipping installation")
        return False

    for dest in get_destinations():
        try:
            dest.mkdir(parents=True, exist_ok=True)
            shutil.copy(source, dest / "SKILL.md")
            print(f"Tuxido skill installed to: {dest}")
            return True
        except (PermissionError, OSError):
            continue

    print("Could not auto-install skill")
    print("Manually copy SKILL.md to ~/.claude/skills/tuxido/")
    return False


if __name__ == "__main__":
    success = install_skill()
    sys.exit(0 if success else 0)
