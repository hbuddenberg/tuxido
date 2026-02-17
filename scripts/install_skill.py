#!/usr/bin/env python3
from __future__ import annotations

import shutil
import sys
from pathlib import Path

SKILL_NAME = "tuxido"


def get_skill_source() -> Path | None:
    """Auto-detect SKILL.md location with multiple fallback paths."""
    script_dir = Path(__file__).parent.resolve()

    # Try 1: Source tree in src/tuxido/skills/
    try:
        source_path = script_dir.parent / "src" / "tuxido" / "skills" / SKILL_NAME / "SKILL.md"
        if source_path.exists():
            return source_path
    except (OSError, AttributeError):
        pass

    # Try 2: Skills folder at project root
    try:
        source_path = script_dir.parent / "skills" / SKILL_NAME / "SKILL.md"
        if source_path.exists():
            return source_path
    except (OSError, AttributeError):
        pass

    # Try 3: Import tuxido package and use its location
    try:
        import tuxido

        package_dir = Path(tuxido.__file__).parent
        source_path = package_dir / "skills" / SKILL_NAME / "SKILL.md"
        if source_path.exists():
            return source_path
    except ImportError:
        pass

    # Try 4: Check parent's parent's skills folder (for nested project structure)
    try:
        source_path = (
            script_dir.parent.parent / "src" / "tuxido" / "skills" / SKILL_NAME / "SKILL.md"
        )
        if source_path.exists():
            return source_path
    except (OSError, AttributeError):
        pass

    print(f"SKILL.md not found in any location")
    return None


def get_destinations() -> list[tuple[Path, str]]:
    """Auto-discover all possible agent skill destinations."""
    home = Path.home()
    cwd = Path.cwd()

    # Define all agent types to check
    agent_types = [
        ".claude",
        ".opencode",
        ".agents",
        ".gemini",
        ".github",
    ]

    destinations = []

    root_dest = cwd / "skills" / SKILL_NAME
    destinations.append((root_dest, "local"))

    for agent_type in agent_types:
        local_dest = cwd / agent_type / "skills" / SKILL_NAME
        destinations.append((local_dest, "local"))

        # Global destination
        if agent_type == ".opencode":
            global_dest = home / ".config" / "opencode" / "skills" / SKILL_NAME
        else:
            global_dest = home / agent_type / "skills" / SKILL_NAME

        destinations.append((global_dest, "global"))

    return destinations


def install_skill() -> bool:
    """Install SKILL.md to all available destinations, reporting success/failure per destination."""
    source = get_skill_source()
    if not source:
        print("SKILL.md not found, skipping installation")
        return False

    print(f"\nInstalling Tuxido skill from: {source}")
    print(f"Target locations: {len(get_destinations())}\n")

    overall_success = False

    for dest, location_type in get_destinations():
        try:
            # Create directory if it doesn't exist
            dest.mkdir(parents=True, exist_ok=True)

            # Copy SKILL.md
            target_file = dest / "SKILL.md"
            shutil.copy(source, target_file)

            # Report success
            print(f"✓ Installed to {dest} ({location_type})")
            overall_success = True

        except PermissionError as e:
            print(f"✗ Failed: {dest} ({location_type}) - Permission denied: {e}")
        except OSError as e:
            print(f"✗ Failed: {dest} ({location_type}) - {e}")
        except Exception as e:
            print(f"✗ Failed: {dest} ({location_type}) - Unexpected error: {e}")

    print()

    if overall_success:
        print("✓ At least one installation succeeded")
        return True
    else:
        print("✗ All installations failed")
        print("\nManual installation:")
        print(f"  Copy {source} to ~/.claude/skills/{SKILL_NAME}/")
        return False


if __name__ == "__main__":
    success = install_skill()
    sys.exit(0 if success else 1)
