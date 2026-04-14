#!/usr/bin/env python3
"""
Markdown to Presentation Generator

Converts markdown files to interactive HTML presentations with progress tracking.
"""

import re
import sys
from pathlib import Path


def parse_markdown(content: str) -> dict:
    """
    Parse markdown content and extract structure.

    Returns:
        dict with keys:
            - title: str (main # heading)
            - sections: list of dicts with:
                - name: str (## heading)
                - items: list of checklist items
                - is_demo: bool
                - demo_url: str or None
    """
    lines = content.split('\n')

    title = ""
    sections = []
    current_section = None

    i = 0
    while i < len(lines):
        line = lines[i].strip()

        # Main title (# Heading)
        if line.startswith('# ') and not title:
            title = line[2:].strip()
            i += 1
            continue

        # Section (## Heading)
        if line.startswith('## '):
            section_name = line[3:].strip()
            is_demo = 'demo' in section_name.lower()

            # Check if next non-empty line is a URL for demo sections
            demo_url = None
            if is_demo:
                for j in range(i + 1, len(lines)):
                    next_line = lines[j].strip()
                    if next_line:  # Skip empty lines
                        if next_line.startswith('http://') or next_line.startswith('https://'):
                            demo_url = next_line
                            i = j  # Skip to the URL line
                        break

            current_section = {
                'name': section_name,
                'items': [],
                'is_demo': is_demo,
                'demo_url': demo_url
            }
            sections.append(current_section)
            i += 1
            continue

        # Checklist item (- **text** — description)
        if line.startswith('- ') and current_section:
            # Match pattern: - **bold** — text
            match = re.match(r'- \*\*(.+?)\*\* — (.+)', line)
            if match:
                item = {
                    'label': match.group(1),
                    'description': match.group(2)
                }
                current_section['items'].append(item)
            else:
                # Plain bullet point
                item_text = line[2:].strip()
                current_section['items'].append({
                    'label': '',
                    'description': item_text
                })
            i += 1
            continue

        i += 1

    return {
        'title': title,
        'sections': sections
    }


def load_template() -> str:
    """Load the HTML template."""
    template_path = Path(__file__).parent / 'template.html'
    with open(template_path, 'r', encoding='utf-8') as f:
        return f.read()


def generate_html(parsed: dict) -> str:
    """
    Generate HTML from parsed markdown.

    Args:
        parsed: dict with title and sections

    Returns:
        Complete HTML string
    """
    template = load_template()

    # Replace Title
    html = template.replace('{{TITLE}}', parsed['title'])

    # Generate section HTML
    sections_html = []
    for i, section in enumerate(parsed['sections']):
        # Sanitize section ID: lowercase, replace spaces with hyphens, remove special chars
        section_id = section['name'].lower().replace(' ', '-').replace('&', 'and').replace(':', '').replace('?', '')

        # Demo section with URL
        if section['is_demo'] and section['demo_url']:
            section_html = f'''
    <div class="card" id="{section_id}Card">
      <div class="card-header" onclick="toggleCard('{section_id}Card')">
        <div style="display: flex; align-items: center; gap: 12px;">
          <input type="checkbox" id="{section_id}" onchange="updateProgress()" style="width: 18px; height: 18px; cursor: pointer; accent-color: #0066cc;">
          <span>{section['name']}</span>
        </div>
        <span class="card-icon">&#9662;</span>
      </div>
      <div class="card-body">
        <div class="card-content">
          <div class="checklist-item">
            <label><a href="{section['demo_url']}" target="_blank" style="color: #0066cc; text-decoration: none;">{section['demo_url']}</a></label>
          </div>
        </div>
      </div>
    </div>'''

        # Q&A section
        elif 'question' in section['name'].lower() or 'qa' in section['name'].lower():
            section_html = f'''
    <div class="card" id="{section_id}Card">
      <div class="card-header" onclick="toggleCard('{section_id}Card')">
        <div style="display: flex; align-items: center; gap: 12px;">
          <input type="checkbox" id="{section_id}" onchange="updateProgress()" style="width: 18px; height: 18px; cursor: pointer; accent-color: #0066cc;">
          <span>{section['name']}</span>
        </div>
        <span class="card-icon">&#9662;</span>
      </div>
      <div class="card-body">
        <div class="card-content">
          <div class="checklist-item">
            <label>Address audience questions</label>
          </div>
        </div>
      </div>
    </div>'''

        # Regular section with checklist items
        else:
            items_html = ''
            for item in section['items']:
                if item['label']:
                    items_html += f'''
          <div class="checklist-item">
            <label><strong>{item['label']}</strong> — {item['description']}</label>
          </div>'''
                else:
                    items_html += f'''
          <div class="checklist-item">
            <label>{item['description']}</label>
          </div>'''

            section_html = f'''
    <div class="card" id="{section_id}Card">
      <div class="card-header" onclick="toggleCard('{section_id}Card')">
        <div style="display: flex; align-items: center; gap: 12px;">
          <input type="checkbox" id="{section_id}" onchange="updateProgress()" style="width: 18px; height: 18px; cursor: pointer; accent-color: #0066cc;">
          <span>{section['name']}</span>
        </div>
        <span class="card-icon">&#9662;</span>
      </div>
      <div class="card-body">
        <div class="card-content">{items_html}
        </div>
      </div>
    </div>'''

        sections_html.append(section_html)

    # Replace sections placeholder
    html = html.replace('<!-- SECTIONS_PLACEHOLDER -->', '\n'.join(sections_html))

    # Update total items count for progress
    total_items = len(parsed['sections'])
    html = html.replace('{{TOTAL}}', str(total_items))

    # Update section IDs in JavaScript (sanitize: remove colons and other special chars)
    def sanitize_id(name):
        return name.lower().replace(' ', '-').replace('&', 'and').replace(':', '').replace('?', '')

    section_ids = [sanitize_id(sec['name']) for sec in parsed['sections']]
    sections_array = ', '.join([f"'{sid}'" for sid in section_ids])

    # Replace all occurrences of the sections array in JavaScript
    html = re.sub(
        r"const sections = \[[^\]]+\];",
        f"const sections = [{sections_array}];",
        html
    )

    return html


def convert_markdown_to_presentation(input_path: str, output_path: str = None):
    """
    Convert a markdown file to an HTML presentation.

    Args:
        input_path: Path to the markdown file
        output_path: Path for the output HTML (default: presentation.html in same directory)
    """
    input_file = Path(input_path)

    if not input_file.exists():
        print(f"Error: Input file not found: {input_path}")
        sys.exit(1)

    # Read markdown
    with open(input_file, 'r', encoding='utf-8') as f:
        markdown_content = f.read()

    # Parse markdown
    parsed = parse_markdown(markdown_content)

    if not parsed['title']:
        print("Warning: No title found in markdown (use # Title)")
        parsed['title'] = "Presentation"

    if not parsed['sections']:
        print("Warning: No sections found in markdown (use ## Section)")

    # Generate HTML
    html = generate_html(parsed)

    # Write output
    if output_path is None:
        output_path = input_file.parent / 'presentation.html'

    output_file = Path(output_path)
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"Generated presentation: {output_file}")
    print(f"  Title: {parsed['title']}")
    print(f"  Sections: {len(parsed['sections'])}")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python generator.py <input.md> [output.html]")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None

    convert_markdown_to_presentation(input_path, output_path)
