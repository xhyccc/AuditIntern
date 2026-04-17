# Work Paper Generator — API Reference

## Function Signature

```python
from skills.wp_generator.scripts.skill_wp_generator import run

result = run(
    template_path="assets/wp-generator/audit_memo_template.xlsx",
    data_file="data/audit_data.json",
    output_path="results/completed_audit_memo.xlsx"
)
```

## OpenCode CLI — Intent Name

`run_wp_generate`

## Required Parameters

| Parameter       | Type   | Description                                         |
|-----------------|--------|-----------------------------------------------------|
| `template_path` | string | Path to Excel (`.xlsx`) or Word (`.docx`) template |
| `data_file`     | string | Path to JSON file with substitution data            |

## Optional Parameters

| Parameter     | Type   | Default       | Description                                        |
|---------------|--------|---------------|----------------------------------------------------|
| `output_path` | string | `wp_output`   | Output file path (extension must match template)   |

## Placeholder Syntax

Placeholders in templates use double curly braces: `{{key_name}}`

- All values from the JSON data file are converted to strings before substitution.
- Keys are case-sensitive: `{{ClientName}}` ≠ `{{clientname}}`.
- Unmatched placeholders remain as-is in the output.

## Template Engine Behavior

### Excel (`.xlsx`)

- Scans every cell in every worksheet
- Only string-value cells are checked
- Formula cells are NOT processed

### Word (`.docx`)

- Scans all paragraphs in the main body
- Scans all table cells
- Run-level replacement: searches each `run.text` for the placeholder
- If a placeholder is split across runs, it will NOT be replaced (re-type it fresh in Word to fix)

## Output Files

Two files are always written:

| File                           | Content                              |
|--------------------------------|--------------------------------------|
| `<output_path>`                | Completed work paper (Excel or Word) |
| `<output_path>.result.json`    | Result JSON with `fields_filled`     |

## Dependencies

| Package     | Purpose                  |
|-------------|--------------------------|
| `openpyxl`  | Excel template reading/writing |
| `python-docx` | Word template reading/writing |
