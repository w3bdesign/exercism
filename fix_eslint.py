"""
Fix ESLint peer dependency conflicts across all exercism exercise directories.

Problems:
  1. @babel/eslint-parser@7.28.6 requires peer eslint@"^7.5.0 || ^8.0.0 || ^9.0.0"
  2. eslint-plugin-import@2.32.0 requires peer eslint@"^2 || ^3 || ^4 || ^5 || ^6 || ^7.2.0 || ^8 || ^9"
  Both conflict with eslint@10.1.0 (the latest stable).

Solution:
  - Remove @babel/eslint-parser from devDependencies (not needed, ESLint's built-in parser works)
  - Remove eslint-plugin-import from devDependencies (peer dep doesn't support eslint 10 yet)
  - Clean up .eslintrc: remove parser, import plugin extends, and import/* rules
  - Delete stale package-lock.json files
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
    """Remove @babel/eslint-parser and eslint-plugin-import from devDependencies."""
    pkg_path = os.path.join(WORKSPACE, directory, "package.json")
    with open(pkg_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    dev_deps = data.get("devDependencies", {})
    removed = []

    for pkg in ["@babel/eslint-parser", "eslint-plugin-import"]:
        if pkg in dev_deps:
            del dev_deps[pkg]
            removed.append(pkg)

    if removed:
        with open(pkg_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
            f.write("\n")
        print(f"  [UPDATED] {directory}/package.json: removed {', '.join(removed)}")
        return True
    else:
        print(f"  [SKIPPED] {directory}/package.json: nothing to remove")
        return False


def fix_eslintrc(directory):
    """Remove parser, import plugin extends, and import/* rules from .eslintrc."""
    rc_path = os.path.join(WORKSPACE, directory, ".eslintrc")
    if not os.path.isfile(rc_path):
        print(f"  [SKIPPED] {directory}/.eslintrc: file not found")
        return False

    with open(rc_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    changed = False

    # Remove parser field
    if "parser" in data:
        del data["parser"]
        changed = True

    # Remove import plugin extends
    if "extends" in data and isinstance(data["extends"], list):
        original_len = len(data["extends"])
        data["extends"] = [
            ext for ext in data["extends"]
            if not ext.startswith("plugin:import/")
        ]
        if len(data["extends"]) < original_len:
            changed = True

    # Remove import/* rules
    if "rules" in data and isinstance(data["rules"], dict):
        import_rules = [key for key in data["rules"] if key.startswith("import/")]
        for key in import_rules:
            del data["rules"][key]
            changed = True

    if changed:
        with open(rc_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
            f.write("\n")
        print(f"  [UPDATED] {directory}/.eslintrc")
        return True
    else:
        print(f"  [SKIPPED] {directory}/.eslintrc: no changes needed")
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

    print("=== Step 1: Removing incompatible packages from package.json ===")
    pkg_updated = 0
    for d in exercise_dirs:
        if fix_package_json(d):
            pkg_updated += 1

    print(f"\n=== Step 2: Cleaning up .eslintrc ===")
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
    print(f"\nDone! Run 'python verify_install.py' to test npm install in all directories.")


if __name__ == "__main__":
    main()
