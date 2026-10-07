# Data Toolbox

Small utilities for converting data files and splitting large JSON payloads into manageable chunks.

## Included Tools

- `csv2json` — converts a CSV file into JSON
- `paginate` — splits a JSON array into page-sized chunks

## Requirements

- Python 3.8+

## Usage

Convert a CSV file to JSON:

```bash
python toolbox.py csv2json ./input.csv -o ./output.json
```

Split a JSON file into pages:

```bash
python toolbox.py paginate ./data.json myprefix -s 10000
```

## What Each Command Does

### `csv2json`

- Reads a CSV file
- Converts each row into a JSON object
- Writes the result to a new JSON file

### `paginate`

- Loads a JSON array from a file
- Creates a folder like `myprefix_pages`
- Writes page files such as `myprefix_page1.json`, `myprefix_page2.json`, and so on

## Notes

- The pagination utility expects a top-level JSON array.
- Output files are written next to the input file or in the generated pages folder.
- Use a larger `-s` value for fewer files, or a smaller value for smaller chunk sizes.

## File

- `toolbox.py` — main data utility script
