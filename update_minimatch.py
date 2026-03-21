import json
import glob
import os

def update_minimatch_override(target_version="3.1.5"):
    """Add or update minimatch override to the specified version in all package.json files."""
    package_files = glob.glob("**/package.json", recursive=True)
    updated_files = []

    for filepath in package_files:
        # Skip node_modules
        if "node_modules" in filepath:
            continue

        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Ensure overrides section exists
        if "overrides" not in data:
            data["overrides"] = {}

        old_version = data["overrides"].get("minimatch")
        data["overrides"]["minimatch"] = target_version

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
            f.write("\n")

        if old_version:
            print(f"Updated: {filepath} (minimatch: {old_version} -> {target_version})")
        else:
            print(f"Added override: {filepath} (minimatch: {target_version})")
        updated_files.append(filepath)

    print(f"\nDone. Updated {len(updated_files)} file(s).")

if __name__ == "__main__":
    update_minimatch_override()
