from __future__ import annotations

from pathlib import Path
import shutil
import subprocess
import sys


def run() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    source_dir = repo_root / "documentation" / "sphinx" / "source"
    generated_dir = source_dir / "_generated"
    src_dir = repo_root / "src"
    output_dir = repo_root / "documentation" / "static" / "sphinx"

    if not src_dir.exists():
        raise RuntimeError(f"Source folder not found: {src_dir}")
    if not source_dir.exists():
        raise RuntimeError(f"Sphinx source folder not found: {source_dir}")

    shutil.rmtree(generated_dir, ignore_errors=True)
    shutil.rmtree(output_dir, ignore_errors=True)
    generated_dir.mkdir(parents=True, exist_ok=True)

    python_exe = sys.executable

    apidoc_cmd = [
        python_exe,
        "-m",
        "sphinx.ext.apidoc",
        "-f",
        "-e",
        "-o",
        str(generated_dir),
        str(src_dir),
    ]
    subprocess.run(apidoc_cmd, check=True)

    build_cmd = [
        python_exe,
        "-m",
        "sphinx.cmd.build",
        "-b",
        "html",
        str(source_dir),
        str(output_dir),
    ]
    subprocess.run(build_cmd, check=True)

    print(f"Generated internal contract docs at: {output_dir}")


if __name__ == "__main__":
    run()
