"""
Fix ESLint peer dependency conflict across all exercism exercise directories.

Problem: @babel/eslint-parser@7.28.6 requires peer eslint@"^7.5.0 || ^8.0.0 || ^9.0.0"
         but eslint@10.1.0 is the latest and is outside that range.

Solution: Remove @babel/eslint-parser (not needed for these exercises),
          remove the "parser": "babel-eslint" line from .eslintrc files,
          and delete stale package-lock.json files so they get regenerated.
"""

import json
import os

WORKSPACE = os.path.dirname(os.path.abspath(__file__))


def find_exercise_dirs():
    """Find all subdirectories containing a package.json."""
    dirs = []
    for entry in sorted(os.listdir(WORKSPACE)):
        full = os.path.join(WORKSPACE, entry)
        if os.path.isdir(full) and os.path.isfile(os.path.join(full, "package.json")):
            dirs.append(entry)
    return dirs


def fix_package_json(directory):
    """Remove @babel/eslint-parser from devDependencies in package.json."""
    pkg_path = os.path.join(WORKSPACE, directory, "package.json")
    with open(pkg_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    dev_deps = data.get("devDependencies", {})
    if "@babel/eslint-parser" in dev_deps:
        del dev_deps["@babel/eslint-parser"]
        with open(pkg_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
            f.write("\n")
        print(f"  [UPDATED] {directory}/package.json: removed @babel/eslint-parser")
        return True
    else:
        print(f"  [SKIPPED] {directory}/package.json: @babel/eslint-parser not found")
        return False


def fix_eslintrc(directory):
    """Remove 'parser': 'babel-eslint' from .eslintrc."""
    rc_path = os.path.join(WORKSPACE, directory, ".eslintrc")
    if not os.path.isfile(rc_path):
        print(f"  [SKIPPED] {directory}/.eslintrc: file not found")
        return False

    with open(rc_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if "parser" in data:
        old_parser = data["parser"]
        del data["parser"]
        with open(rc_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
            f.write("\n")
        print(f"  [UPDATED] {directory}/.eslintrc: removed parser '{old_parser}'")
        return True
    else:
        print(f"  [SKIPPED] {directory}/.eslintrc: no parser field found")
        return False


def delete_package_lock(directory):
    """Delete package-lock.json so it gets regenerated on next npm install."""
    lock_path = os.path.join(WORKSPACE, directory, "package-lock.json")
    if os.path.isfile(lock_path):
        os.remove(lock_path)
        print(f"  [DELETED] {directory}/package-lock.json")
        return True
    return False


def main():
    exercise_dirs = find_exercise_dirs()
    print(f"Found {len(exercise_dirs)} exercise directories:\n  {', '.join(exercise_dirs)}\n")

    print("=== Step 1: Removing @babel/eslint-parser from package.json ===")
    pkg_updated = 0
    for d in exercise_dirs:
        if fix_package_json(d):
            pkg_updated += 1

    print(f"\n=== Step 2: Removing parser from .eslintrc ===")
    rc_updated = 0
    for d in exercise_dirs:
        if fix_eslintrc(d):
            rc_updated += 1

    print(f"\n=== Step 3: Deleting stale package-lock.json files ===")
    deleted = 0
    for d in exercise_dirs:
        if delete_package_lock(d):
            deleted += 1

    print(f"\n=== Summary ===")
    print(f"  package.json files updated:      {pkg_updated}")
    print(f"  .eslintrc files updated:         {rc_updated}")
    print(f"  package-lock.json files deleted:  {deleted}")
    print(f"\nDone! Run 'npm install' in each exercise directory to regenerate lock files.")


if __name__ == "__main__":
    main()
