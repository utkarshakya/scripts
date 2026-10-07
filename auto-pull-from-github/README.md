# Auto Pull from GitHub

Utilities for keeping local Git repositories in sync with their remotes from a shared base folder.

## Included Scripts

- `auto_git_pull.py` — scans a folder for Git repos, fetches updates, and pulls only the ones that are behind.
- `interactive_git_manager.py` — lets you browse repos, inspect status, and pull or open them individually.

## Requirements

- Python 3.8+
- Git available on your `PATH`
- Windows (for File Explorer integration and `explorer` calls)

## Usage

Run the automated bulk updater:

```powershell
python auto_git_pull.py
```

Run the interactive repository manager:

```powershell
python interactive_git_manager.py
```

## How It Works

### `auto_git_pull.py`

- Walks the configured base folder recursively
- Finds Git repositories and skips hidden/system folders
- Runs `git fetch` for each repo
- Checks whether the current branch is behind its upstream
- Runs `git pull` only when needed
- Prints a summary of updated, up-to-date, skipped, and failed repositories

### `interactive_git_manager.py`

- Lists folders from the configured base location
- Shows which directories are Git repos
- Displays current branch and repository status
- Lets you pull, open, or navigate to a repo from the terminal

## Configuration

Both scripts read the base folder from `config.json` in this folder. The file currently looks like this:

```json
{
  "base_path": "C:\\Users\\your_name\\OneDrive\\Desktop\\dev_backup"
}
```

If you want to use a different directory, edit `config.json` and replace the value with your own local path. If `config.json` is missing or `base_path` is empty, the scripts use the default `OneDrive\Desktop\Public` location. If the configured path does not exist or the config file is invalid, the script reports an error instead of silently using another folder. The bulk updater's optional `--path` argument takes precedence over the config value.

## Notes

- If the configured folder does not exist, the script will report that it could not find the base directory.
- If a fetch or pull times out, the script marks that repo as failed and leaves the decision to you.
- The interactive manager uses `explorer` to open directories, so it is designed for Windows.

## Troubleshooting

- Check that Git is installed and available in your shell: `git --version`
- Run a repo manually if needed:

```powershell
git -C "C:\path\to\repo" fetch
git -C "C:\path\to\repo" pull
```

## Files

- `auto_git_pull.py` — automated repository sync
- `interactive_git_manager.py` — interactive repo manager
