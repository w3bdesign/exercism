"""
Verify the ESLint fix by running 'npm install' in all exercise directories.
Reports success/failure for each directory.
"""

import os
import subprocess
import sys

WORKSPACE = os.path.dirname(os.path.abspath(__file__))


def find_exercise_dirs():
    """Find all subdirectories containing a package.json."""
    dirs = []
    for entry in sorted(os.listdir(WORKSPACE)):
        full = os.path.join(WORKSPACE, entry)
        if os.path.isdir(full) and os.path.isfile(os.path.join(full, "package.json")):
            dirs.append(entry)
    return dirs


def run_npm_install(directory):
    """Run npm install in the given directory and return (success, output)."""
    dir_path = os.path.join(WORKSPACE, directory)
    result = subprocess.run(
        ["npm", "install"],
        cwd=dir_path,
        capture_output=True,
        text=True,
        shell=True,
        timeout=120,
    )
    return result.returncode == 0, result.stdout, result.stderr


def main():
    exercise_dirs = find_exercise_dirs()
    print(f"Running 'npm install' in {len(exercise_dirs)} exercise directories...\n")

    successes = []
    failures = []

    for d in exercise_dirs:
        print(f"  [{d}] Installing...", end=" ", flush=True)
        try:
            ok, stdout, stderr = run_npm_install(d)
            if ok:
                print("OK")
                successes.append(d)
            else:
                print("FAILED")
                failures.append((d, stderr))
        except subprocess.TimeoutExpired:
            print("TIMEOUT")
            failures.append((d, "npm install timed out after 120s"))

    print(f"\n=== Summary ===")
    print(f"  Succeeded: {len(successes)}")
    print(f"  Failed:    {len(failures)}")

    if failures:
        print(f"\n=== Failures ===")
        for d, err in failures:
            print(f"\n--- {d} ---")
            # Print only the lines containing "ERR!" for brevity
            err_lines = [line for line in err.splitlines() if "ERR!" in line]
            if err_lines:
                print("\n".join(err_lines))
            else:
                print(err[:500] if err else "(no output)")
        sys.exit(1)
    else:
        print("\nAll directories installed successfully!")
        sys.exit(0)


if __name__ == "__main__":
    main()
