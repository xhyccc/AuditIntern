---
name: wp-generator
description: Generates audit work papers by filling tagged placeholders in Excel or Word templates. Use when the user asks to generate a work paper, fill in an audit template, populate a Word or Excel document with data, create a formatted report from a template, or produce a work paper from a JSON data file.
---

# Work Paper Generator

Reads a JSON data file and fills `{{key}}` placeholders in an Excel (`.xlsx`) or Word
(`.docx`) template, then saves the completed document to the specified output path.

## Script

`scripts/skill_wp_generator.py` — `run(template_path, data_file, output_path) -> dict`
