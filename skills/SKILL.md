---
name: markdown-to-presentation
description: Use when converting markdown files to interactive HTML presentations, generating slide decks from markdown content, creating reusable presentation templates, or building interactive demos with progress tracking. Make sure to use this skill whenever the user mentions presentations, slides, markdown conversion, or wants to display content in an interactive format.
---

# Markdown to Presentation Generator

## Overview

This skill converts markdown files into self-contained, interactive HTML presentations with progress tracking, collapsible sections, and localStorage persistence.

## Invocation

Users can invoke this skill naturally:
- "Generate a presentation from Demo_Agentic_AI_Test_Automation.md"
- "Create a presentation from this markdown file"
- "Convert my markdown to an interactive HTML presentation"

## Markdown Format

Expected input format:

```markdown
# Presentation Title

## Section Name
- **Bold term** — description

## Demo 1
http://localhost:3000

## Questions & Answers
```

## Conversion Process

1. **Read the markdown file** - Extract the file path from the user's request
2. **Parse the markdown** - Use `generator.py` to extract:
   - `# Heading` → Presentation title
   - `## Section` → Collapsible card sections
   - `- **text** — text` → Checklist items
   - `## Demo N` + URL → Demo sections with links
3. **Generate HTML** - Inject parsed content into `template.html`
4. **Write output** - Save as `presentation.html` in the current directory

## Files

- `generator.py` - Python script with regex-based markdown parser
- `template.html` - Reusable HTML template with CSS variables for theming

## Theme Customization

The template uses CSS variables for easy theming. Users can edit these in the generated HTML:

```css
:root {
  --primary-color: #0066cc;
  --font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  --background: #f5f5f5;
  --card-background: #ffffff;
}
```

## Output Features

- Progress bar tracking completed sections
- Collapsible cards for each section
- Checkbox completion with localStorage persistence
- Reset button to clear progress
- Responsive design (mobile/desktop)
- Self-contained HTML (works offline, no external dependencies)

## Common Mistakes

- **Missing URL for Demo sections** - Demo sections require a URL on the line after the header
- **Incorrect markdown format** - Use `**bold** — text` format for checklist items
- **Hardcoded content** - The template is reusable; don't hardcode topic-specific content

## Example

**Input markdown:**
```markdown
# My Presentation

## Introduction
- **Point 1** - First key point
- **Point 2** - Second key point

## Demo
http://localhost:3000
```

**Output:** Interactive HTML presentation with collapsible sections, progress tracking, and demo link.
