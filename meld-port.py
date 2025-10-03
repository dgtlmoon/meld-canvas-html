#!/usr/bin/env python3
"""
Web-based Meld port - Proof of concept
Generates HTML/CSS/JS for a 3-column diff viewer with SVG/WebGL linkmap
"""

import difflib
import json
import os
from pathlib import Path
from typing import List, NamedTuple
import html

from jinja2 import Environment, FileSystemLoader


class DiffChunk(NamedTuple):
    tag: str
    start_a: int
    end_a: int
    start_b: int
    end_b: int


def compute_diff(text_a: str, text_b: str) -> List[DiffChunk]:
    """Compute diff chunks between two texts using Python's difflib"""
    lines_a = text_a.splitlines()
    lines_b = text_b.splitlines()

    matcher = difflib.SequenceMatcher(None, lines_a, lines_b)
    chunks = []

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag != 'equal':  # Only include changes, not equal blocks
            chunks.append(DiffChunk(tag, i1, i2, j1, j2))

    return chunks


def compute_inline_diff(text1: str, text2: str) -> List[tuple]:
    """Compute character-level diff for inline highlighting"""
    matcher = difflib.SequenceMatcher(None, text1, text2)
    return matcher.get_opcodes()


def format_line_with_inline_diff(line: str, other_line: str, is_changed: bool) -> str:
    """Format a line with inline character-level highlighting"""
    INLINE_HIGHLIGHT_LIMIT = 20 * 1024  # 20KB combined length limit

    if not is_changed or not line or not other_line:
        # No inline diff needed
        return html.escape(line) if line else "&nbsp;"

    # Bail on long sequences - character-level diff is expensive
    if len(line) + len(other_line) > INLINE_HIGHLIGHT_LIMIT:
        # Skip inline highlighting for performance
        return html.escape(line) if line else "&nbsp;"

    # Compute character-level diff
    opcodes = compute_inline_diff(line, other_line)

    result = []
    for tag, i1, i2, j1, j2 in opcodes:
        if tag == 'equal':
            result.append(html.escape(line[i1:i2]))
        elif tag in ('replace', 'delete'):
            # Highlight changed/deleted characters
            text = html.escape(line[i1:i2])
            result.append(f'<span class="inline-diff">{text}</span>')
        # Insert is only on the other side, skip here

    return ''.join(result) if result else "&nbsp;"


def format_lines(lines: List[str], other_lines: List[str], chunks: List[DiffChunk], is_left: bool) -> str:
    """Format lines with line numbers and chunk highlighting"""
    html_lines = []
    for i, line in enumerate(lines):
        # Find if this line is part of a chunk
        chunk_class = ""
        chunk_tag = None
        for chunk in chunks:
            if is_left:
                if chunk.start_a <= i < chunk.end_a:
                    chunk_class = f"chunk-{chunk.tag}"
                    chunk_tag = chunk.tag
                    break
            else:
                if chunk.start_b <= i < chunk.end_b:
                    chunk_class = f"chunk-{chunk.tag}"
                    chunk_tag = chunk.tag
                    break

        # For replace chunks, compute inline diff
        if chunk_tag == 'replace':
            # Find corresponding line in other file
            for chunk in chunks:
                if is_left:
                    if chunk.start_a <= i < chunk.end_a and chunk.tag == 'replace':
                        # Map to corresponding line in other file
                        offset = i - chunk.start_a
                        other_idx = chunk.start_b + offset
                        if 0 <= other_idx < len(other_lines):
                            formatted_line = format_line_with_inline_diff(
                                line, other_lines[other_idx], True
                            )
                        else:
                            formatted_line = html.escape(line) if line else "&nbsp;"
                        break
                else:
                    if chunk.start_b <= i < chunk.end_b and chunk.tag == 'replace':
                        # Map to corresponding line in other file
                        offset = i - chunk.start_b
                        other_idx = chunk.start_a + offset
                        if 0 <= other_idx < len(other_lines):
                            formatted_line = format_line_with_inline_diff(
                                line, other_lines[other_idx], True
                            )
                        else:
                            formatted_line = html.escape(line) if line else "&nbsp;"
                        break
            else:
                formatted_line = html.escape(line) if line else "&nbsp;"
        else:
            formatted_line = html.escape(line) if line else "&nbsp;"

        html_lines.append(
            f'<div class="line {chunk_class}" data-line="{i}">'
            f'<span class="line-num">{i + 1}</span>'
            f'<span class="line-content">{formatted_line}</span>'
            f'</div>'
        )
    return '\n'.join(html_lines)


def generate_html(text_a: str, text_b: str, chunks: List[DiffChunk], template_path: str) -> str:
    """Generate complete HTML page with diff viewer using Jinja2 template"""

    lines_a = text_a.splitlines()
    lines_b = text_b.splitlines()

    # Format content for both panes (with inline diff support)
    left_content = format_lines(lines_a, lines_b, chunks, True)
    right_content = format_lines(lines_b, lines_a, chunks, False)

    # Convert chunks to JSON-serializable format
    chunks_data = [
        {
            "id": i,
            "tag": chunk.tag,
            "start_a": chunk.start_a,
            "end_a": chunk.end_a,
            "start_b": chunk.start_b,
            "end_b": chunk.end_b
        }
        for i, chunk in enumerate(chunks)
    ]

    # Setup Jinja2 environment
    template_dir = os.path.dirname(template_path)
    template_file = os.path.basename(template_path)

    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template(template_file)

    # Render template
    html_output = template.render(
        left_content=left_content,
        right_content=right_content,
        chunks_json=json.dumps(chunks_data),
        chunk_count=len(chunks)
    )

    return html_output


def check_file_limits(text: str, filename: str) -> bool:
    """Check file for limiting conditions (long lines, binary content)"""
    LINE_LENGTH_LIMIT = 8 * 1024  # 8KB per line

    # Check for binary content (null bytes)
    if '\x00' in text:
        print(f"Error: {filename} appears to be a binary file (contains null bytes)")
        print("Binary files are not supported in the diff viewer.")
        return False

    # Check for extremely long lines
    lines = text.splitlines()
    for i, line in enumerate(lines, 1):
        if len(line) > LINE_LENGTH_LIMIT:
            print(f"Error: {filename} line {i} exceeds {LINE_LENGTH_LIMIT} characters ({len(line)} chars)")
            print("Files with very long lines can cause browser hangs and are not supported.")
            return False

    return True


def main():
    """Generate test HTML file"""
    script_dir = Path(__file__).parent

    # Load text files
    file_a = script_dir / 'a.txt'
    file_b = script_dir / 'b.txt'

    if not file_a.exists() or not file_b.exists():
        print("Error: a.txt or b.txt not found!")
        print("Please ensure both files exist in the same directory as this script.")
        return

    with open(file_a, 'r', encoding='utf-8') as f:
        text_a = f.read()

    with open(file_b, 'r', encoding='utf-8') as f:
        text_b = f.read()

    print(f"Loaded a.txt: {len(text_a)} bytes ({len(text_a.splitlines())} lines)")
    print(f"Loaded b.txt: {len(text_b)} bytes ({len(text_b.splitlines())} lines)")

    # Check file limits
    if not check_file_limits(text_a, 'a.txt'):
        return
    if not check_file_limits(text_b, 'b.txt'):
        return

    # Compute diff
    chunks = compute_diff(text_a, text_b)
    print(f"\nComputing diff...")
    print(f"Found {len(chunks)} change chunks")

    # Generate HTML using template
    template_path = script_dir / 'template.html'

    if not template_path.exists():
        print(f"Error: template.html not found at {template_path}")
        return

    html_output = generate_html(text_a, text_b, chunks, str(template_path))

    # Write to file
    output_path = script_dir / 'test-output.html'
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_output)

    print(f"\nGenerated: {output_path}")
    print(f"File size: {len(html_output) / 1024:.1f} KB")
    print(f"\nOpen in browser: file://{output_path.absolute()}")

    # Print chunk summary
    print("\nChunk summary (first 20):")
    for i, chunk in enumerate(chunks[:20]):
        print(f"  {chunk.tag:8} | Left: {chunk.start_a:3}-{chunk.end_a:3} | Right: {chunk.start_b:3}-{chunk.end_b:3}")

    if len(chunks) > 20:
        print(f"  ... and {len(chunks) - 20} more chunks")


if __name__ == '__main__':
    main()
