import subprocess
import sys


def main() -> int:
    args = sys.argv[1:]
    command = [sys.executable, "-m", "pytest", *args]
    return subprocess.call(command)


if __name__ == "__main__":
    raise SystemExit(main())
