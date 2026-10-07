import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union


def load_base_path() -> Optional[str]:
    """Read the optional base_path setting from config.json."""
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


class GitRepoManager:
    """Interactive Git Repository Manager for navigating and managing repositories."""

    def __init__(self, base_path: Union[str, Path]) -> None:
        self.base_path = Path(base_path)
        self.current_path = self.base_path
        self.path_history: List[Path] = []

    @staticmethod
    def is_git_repo(path: Path) -> bool:
        """Check if a directory is a git repository."""
        git_dir = path / '.git'
        return git_dir.exists() and git_dir.is_dir()

    def get_git_info(
        self, path: Path
    ) -> Tuple[Optional[str], Optional[bool]]:
        """Get current branch and status of a git repository."""
        try:
            branch_result = subprocess.run(
                ['git', '-C', str(path), 'branch', '--show-current'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if branch_result.returncode != 0:
                error = branch_result.stderr.strip() or "Could not read the current branch"
                print(f"\n⚠️  Could not inspect {path}: {error}")
                return None, None

            branch = branch_result.stdout.strip() or 'detached HEAD'
            status_result = subprocess.run(
                ['git', '-C', str(path), 'status', '--porcelain'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if status_result.returncode != 0:
                error = status_result.stderr.strip() or "Could not read repository status"
                print(f"\n⚠️  Could not inspect {path}: {error}")
                return None, None

            has_changes = bool(status_result.stdout.strip())
            return branch, has_changes
        except (OSError, subprocess.SubprocessError) as error:
            print(f"\n⚠️  Could not inspect {path}: {error}")
            return None, None

    def list_directories(self) -> List[Dict[str, Any]]:
        """List all directories in the current path with git indicators."""
        try:
            items: List[Dict[str, Any]] = []
            for item in sorted(self.current_path.iterdir()):
                if item.is_dir() and not item.name.startswith('.'):
                    is_git = self.is_git_repo(item)
                    info = {'path': item, 'name': item.name, 'is_git': is_git}
                    
                    if is_git:
                        branch, has_changes = self.get_git_info(item)
                        info['branch'] = branch
                        info['has_changes'] = has_changes
                    
                    items.append(info)
            return items
        except OSError as error:
            print(f"\n❌ Could not access {self.current_path}: {error}")
            return []

    def display_folders(self, items: List[Dict[str, Any]]) -> None:
        """Display folders with git information."""
        if not items:
            print("\n📂 No folders found in this directory.")
            return

        print(f"\n📍 Current location: {self.current_path}")
        print("=" * 80)

        for idx, item in enumerate(items, 1):
            if item['is_git']:
                git_info = f"[GIT: {item['branch']}"
                if item['has_changes']:
                    git_info += " - UNCOMMITTED CHANGES"
                git_info += "]"
                print(f"{idx}. {item['name']:<40} {git_info}")
            else:
                print(f"{idx}. {item['name']:<40} [FOLDER]")

        print("=" * 80)

    def git_pull(self, path: Path) -> None:
        """Perform git pull operation."""
        print(f"\n🔄 Pulling changes for: {path.name}")
        print("-" * 60)

        try:
            result = subprocess.run(
                ['git', '-C', str(path), 'pull'],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                print("✅ Pull successful!")
                print(result.stdout)
            else:
                print("❌ Pull failed!")
                print(result.stderr)
        except subprocess.TimeoutExpired:
            print("❌ Pull operation timed out (30 seconds).")
        except (OSError, subprocess.SubprocessError) as error:
            print(f"❌ Error during pull: {error}")

        print("-" * 60)

    def open_in_explorer(self, path: Path) -> None:
        """Open folder in Windows File Explorer."""
        try:
            subprocess.run(['explorer', str(path)], check=True)
            print(f"✅ Opened {path.name} in File Explorer")
        except (OSError, subprocess.SubprocessError) as error:
            print(f"❌ Failed to open in File Explorer: {error}")

    def navigate_to(self, path: Path) -> None:
        """Navigate to a new directory."""
        self.path_history.append(self.current_path)
        self.current_path = path

    def go_back(self) -> bool:
        """Go back to the previous directory."""
        if self.path_history:
            self.current_path = self.path_history.pop()
            return True
        return False

    def show_breadcrumb(self) -> None:
        """Display breadcrumb trail of navigation history."""
        if self.path_history:
            print("\n🔖 Navigation trail:")
            trail = " → ".join([path.name for path in self.path_history])
            print(f"   {trail} → {self.current_path.name}")

    def run(self) -> None:
        """Main interactive loop."""
        print("=" * 80)
        print("🚀 GIT REPOSITORY MANAGER".center(80))
        print("=" * 80)

        while True:
            items = self.list_directories()
            self.display_folders(items)
            self.show_breadcrumb()

            print("\n📋 Options:")
            if items:
                print("   • Enter folder number to select")
            if self.path_history:
                print("   • Type 'b' or 'back' to go to parent folder")
            print("   • Type 'h' or 'home' to return to base folder")
            print("   • Type 'q' or 'quit' to exit")

            choice = input("\n👉 Your choice: ").strip().lower()

            if choice in ['q', 'quit', 'exit']:
                print("\n👋 Goodbye!")
                break

            if choice in ['b', 'back']:
                if self.go_back():
                    print("✅ Moved to parent folder")
                else:
                    print("❌ Already at base folder")
                continue

            if choice in ['h', 'home']:
                self.current_path = self.base_path
                self.path_history.clear()
                print("✅ Returned to base folder")
                continue

            try:
                idx = int(choice) - 1
                if 0 <= idx < len(items):
                    selected = items[idx]

                    if selected['is_git']:
                        print(f"\n📦 Selected: {selected['name']} (Git Repository)")
                        print(f"   Branch: {selected['branch']}")
                        if selected['has_changes']:
                            print("   ⚠️  Has uncommitted changes")

                        print("\n   1. Pull from remote")
                        print("   2. Open in File Explorer")
                        print("   3. Navigate into folder")
                        print("   4. Cancel")

                        action = input("\n   Choose action (1-4): ").strip()

                        if action == '1':
                            self.git_pull(selected['path'])
                            input("\nPress Enter to continue...")
                        elif action == '2':
                            self.open_in_explorer(selected['path'])
                        elif action == '3':
                            self.navigate_to(selected['path'])
                        elif action == '4':
                            print("   Cancelled")
                        else:
                            print("   ❌ Invalid action")
                    else:
                        self.navigate_to(selected['path'])
                        print(f"✅ Navigated to: {selected['name']}")
                else:
                    print("❌ Invalid selection")
            except ValueError:
                print("❌ Please enter a valid number or command")


def main() -> None:
    """Entry point for the interactive script."""
    try:
        configured_base_path = load_base_path()
    except ValueError as error:
        print(f"❌ Configuration error: {error}")
        sys.exit(1)

    base_path = Path(
        configured_base_path
        or Path.home() / 'OneDrive' / 'Desktop' / 'Public'
    )

    if not base_path.is_dir():
        print(f"❌ Error: Base folder not found or is not a directory: {base_path}")
        print("   Update the path in config.json or create the folder and try again.")
        sys.exit(1)

    manager = GitRepoManager(base_path)
    manager.run()


if __name__ == "__main__":
    main()
