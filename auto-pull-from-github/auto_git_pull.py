import argparse
import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple, Union


class MinimalGitPuller:
    """Automated git pull with fetch-first optimization and animated UI."""

    def __init__(self, base_path: Union[str, Path]) -> None:
        self.base_path = Path(base_path)
        self.found_repos: List[Path] = []
        self.results: Dict[str, List[Any]] = {
            "updated": [],
            "up_to_date": [],
            "failed": [],
            "skipped": [],
        }

    @staticmethod
    def is_git_repo(path: Path) -> bool:
        git_dir = path / ".git"
        return git_dir.exists() and git_dir.is_dir()

    def find_git_repos(self, path: Path, depth: int = 0, max_depth: int = 10) -> None:
        if depth > max_depth:
            return

        try:
            children = sorted(path.iterdir())
        except OSError as error:
            print(f"⚠️  Could not scan {path}: {error}")
            return

        for item in children:
            if item.name.startswith("."):
                continue
            try:
                if item.is_dir():
                    if self.is_git_repo(item):
                        self.found_repos.append(item)
                    else:
                        self.find_git_repos(item, depth + 1, max_depth)
            except OSError as error:
                print(f"⚠️  Could not inspect {item}: {error}")

    def has_remote(self, repo_path: Path) -> Tuple[Optional[bool], str]:
        try:
            result = subprocess.run(
                ["git", "-C", str(repo_path), "remote", "-v"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode != 0:
                return None, result.stderr.strip() or "Could not inspect repository remotes"
            return bool(result.stdout.strip()), ""
        except (OSError, subprocess.SubprocessError) as error:
            return None, str(error)

    def fetch_repo(self, repo_path: Path) -> Tuple[bool, str]:
        try:
            result = subprocess.run(
                ["git", "-C", str(repo_path), "fetch"],
                capture_output=True,
                text=True,
                timeout=30,
            )
            return result.returncode == 0, result.stderr.strip()
        except (OSError, subprocess.SubprocessError) as error:
            return False, str(error)

    def check_behind(self, repo_path: Path) -> Tuple[Optional[bool], int, str]:
        try:
            result = subprocess.run(
                ["git", "-C", str(repo_path), "rev-list", "HEAD..@{u}", "--count"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                commit_count = int(result.stdout.strip())
                return commit_count > 0, commit_count, ""
            return None, 0, result.stderr.strip() or "Could not determine upstream status"
        except (OSError, subprocess.SubprocessError, ValueError) as error:
            return None, 0, str(error)

    def pull_repo(self, repo_path: Path) -> Tuple[bool, str]:
        try:
            result = subprocess.run(
                ["git", "-C", str(repo_path), "pull"],
                capture_output=True,
                text=True,
                timeout=30,
            )
            message = result.stdout.strip() or result.stderr.strip()
            return result.returncode == 0, message
        except (OSError, subprocess.SubprocessError) as error:
            return False, str(error)

    def process_repo(self, repo_path: Path) -> None:
        relative_path = repo_path.relative_to(self.base_path)
        has_remote, error = self.has_remote(repo_path)
        if has_remote is None:
            self.results["failed"].append(
                {"path": relative_path, "error": f"Remote check failed: {error}"}
            )
            return
        if not has_remote:
            self.results["skipped"].append(
                {"path": relative_path, "reason": "No remote"}
            )
            return

        success, error = self.fetch_repo(repo_path)
        if not success:
            self.results["failed"].append(
                {"path": relative_path, "error": f"Fetch failed: {error}"}
            )
            return

        is_behind, commit_count, error = self.check_behind(repo_path)
        if is_behind is None:
            self.results["failed"].append(
                {"path": relative_path, "error": f"Upstream check failed: {error}"}
            )
            return
        if not is_behind:
            self.results["up_to_date"].append(relative_path)
            return

        success, message = self.pull_repo(repo_path)
        if success:
            self.results["updated"].append(
                {"path": relative_path, "commits": commit_count}
            )
        else:
            self.results["failed"].append(
                {"path": relative_path, "error": f"Pull failed: {message}"}
            )

    def run(self) -> None:
        start_time = datetime.now()
        print("=" * 60)
        print("  AUTO GIT PULL".center(60))
        print("=" * 60)
        print(f"📂 Base: {self.base_path}")
        self.find_git_repos(self.base_path)
        print(f"🔍 Found {len(self.found_repos)} repositories")

        for idx, repo in enumerate(self.found_repos, 1):
            print(f"\r🔄 Processing {idx}/{len(self.found_repos)}...", end="", flush=True)
            self.process_repo(repo)

        print("\n" + "=" * 60)
        if self.results["updated"]:
            print(f"✅ UPDATED ({len(self.results['updated'])}):")
            for item in self.results["updated"]:
                print(f"   • {item['path']} (+{item['commits']} commits)")

        if self.results["failed"]:
            print(f"❌ FAILED ({len(self.results['failed'])}):")
            for item in self.results["failed"]:
                print(f"   • {item['path']}: {item['error']}")

        print(
            f"⏩ UP TO DATE: {len(self.results['up_to_date'])} | "
            f"⚠️ SKIPPED: {len(self.results['skipped'])}"
        )
        print(f"⏱️  Duration: {(datetime.now() - start_time).total_seconds():.1f}s")
        print("=" * 60)


def load_config() -> Optional[str]:
    config_path = Path(__file__).parent / 'config.json'
    if not config_path.exists():
        return None

    try:
        with config_path.open("r", encoding="utf-8") as config_file:
            config = json.load(config_file)
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"Could not read {config_path}: {error}") from error

    if not isinstance(config, dict):
        raise ValueError(f"{config_path} must contain a JSON object")

    base_path = config.get("base_path")
    if base_path is not None and not isinstance(base_path, str):
        raise ValueError(f"'base_path' in {config_path} must be a string")
    return base_path or None


def main():
    parser = argparse.ArgumentParser(
        description="Auto-pull updates for all Git repos in a directory."
    )
    parser.add_argument("--path", type=str, help="Directory to scan for Git repos")
    args = parser.parse_args()

    configured_path = None
    if not args.path:
        try:
            configured_path = load_config()
        except ValueError as error:
            print(f"❌ Configuration error: {error}")
            sys.exit(1)

    base_path = Path(
        args.path or configured_path or Path.home() / "OneDrive" / "Desktop" / "Public"
    )
    if not base_path.is_dir():
        print(f"❌ Error: Base folder not found or is not a directory: {base_path}")
        sys.exit(1)

    puller = MinimalGitPuller(base_path)
    puller.run()
    input("\nPress Enter to exit...")


if __name__ == "__main__":
    main()