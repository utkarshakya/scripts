# Universal Script Runner

Run one script across many files without writing a loop for each use case. This utility supports Python, Node.js, shell scripts, PowerShell, and custom commands.

## Features

- Interactive or command-line execution
- File filtering by pattern
- Optional recursive folder scanning
- Support for custom argument templates
- Execution summaries and error reporting
- Cross-platform support for Windows, Linux, and macOS

## Requirements

- Python 3.8+

## How to Run

```bash
python universal_runner.py
```

The script will guide you through selecting the folder, file pattern, script type, and execution options.

## Command-Line Usage

```bash
python universal_runner.py --folder ./data --script "python process.py" --pattern "*.csv"
```

## Important Argument Pattern

Use the `{FILE}` placeholder anywhere in the command where the file path should be inserted:

```bash
python universal_runner.py --folder ./datasets --script "python analyze.py --mode=strict {FILE} --output=./results" --pattern "*.json"
```

This is useful when the target script expects the file path in a specific position rather than as the last argument.

## Examples

### Python Script

```bash
python universal_runner.py --folder ./data --script "python process_csv.py" --pattern "*.csv"
```

### Node.js Script

```bash
python universal_runner.py --folder ./data --script "node processor.js" --pattern "*.json"
```

### Shell Script

```bash
python universal_runner.py --folder ./documents --script "bash backup.sh" --pattern "*.txt" --recursive
```

### PowerShell Script

```bash
python universal_runner.py --folder C:\Data --script "powershell -File convert.ps1" --pattern "*.csv"
```

## Notes

- Interactive scripts that call `input()` can behave poorly in batch mode. The tool warns about this and offers safer alternatives.
- Some environments may require additional packages for nicer formatting or prompts, but the basic workflow still works without them.
- The script is most useful when you want to process many files with the same command, without repeating the same loop manually.

## Files

- `universal_runner.py` — main batch execution utility
