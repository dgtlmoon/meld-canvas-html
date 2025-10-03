#!/usr/bin/env python3
"""
Unit tests for meld_port.py
"""

import unittest

# Import meld_port module
import meld_port

compute_diff = meld_port.compute_diff
compute_inline_diff = meld_port.compute_inline_diff
format_line_with_inline_diff = meld_port.format_line_with_inline_diff
check_file_limits = meld_port.check_file_limits


class TestComputeDiff(unittest.TestCase):
    def test_no_changes(self):
        """Test diff with identical texts"""
        text_a = "line1\nline2\nline3"
        text_b = "line1\nline2\nline3"
        chunks = compute_diff(text_a, text_b)
        self.assertEqual(len(chunks), 0, "Identical texts should have no diff chunks")

    def test_insert(self):
        """Test insertion detection"""
        text_a = "line1\nline3"
        text_b = "line1\nline2\nline3"
        chunks = compute_diff(text_a, text_b)
        self.assertEqual(len(chunks), 1)
        self.assertEqual(chunks[0].tag, 'insert')
        self.assertEqual(chunks[0].start_b, 1)
        self.assertEqual(chunks[0].end_b, 2)

    def test_delete(self):
        """Test deletion detection"""
        text_a = "line1\nline2\nline3"
        text_b = "line1\nline3"
        chunks = compute_diff(text_a, text_b)
        self.assertEqual(len(chunks), 1)
        self.assertEqual(chunks[0].tag, 'delete')
        self.assertEqual(chunks[0].start_a, 1)
        self.assertEqual(chunks[0].end_a, 2)

    def test_replace(self):
        """Test replacement detection"""
        text_a = "line1\nold line\nline3"
        text_b = "line1\nnew line\nline3"
        chunks = compute_diff(text_a, text_b)
        self.assertEqual(len(chunks), 1)
        self.assertEqual(chunks[0].tag, 'replace')

    def test_multiple_changes(self):
        """Test multiple changes"""
        text_a = "A\nB\nC\nD"
        text_b = "A\nX\nC\nY\nZ"
        chunks = compute_diff(text_a, text_b)
        self.assertGreater(len(chunks), 1, "Should detect multiple changes")


class TestComputeInlineDiff(unittest.TestCase):
    def test_no_change(self):
        """Test inline diff with identical strings"""
        opcodes = compute_inline_diff("hello", "hello")
        self.assertEqual(len(opcodes), 1)
        self.assertEqual(opcodes[0][0], 'equal')

    def test_character_replacement(self):
        """Test character-level replacement"""
        opcodes = compute_inline_diff("hello", "hallo")
        found_replace = any(op[0] == 'replace' for op in opcodes)
        self.assertTrue(found_replace, "Should detect character replacement")

    def test_insertion(self):
        """Test character insertion"""
        opcodes = compute_inline_diff("hello", "helllo")
        found_insert = any(op[0] == 'insert' for op in opcodes)
        self.assertTrue(found_insert, "Should detect character insertion")

    def test_deletion(self):
        """Test character deletion"""
        opcodes = compute_inline_diff("hello", "helo")
        found_delete = any(op[0] == 'delete' for op in opcodes)
        self.assertTrue(found_delete, "Should detect character deletion")


class TestFormatLineWithInlineDiff(unittest.TestCase):
    def test_no_change(self):
        """Test formatting unchanged line"""
        result = format_line_with_inline_diff("test", "test", True)
        self.assertIn("test", result)
        self.assertNotIn('<span class="inline-diff">', result)

    def test_with_change(self):
        """Test formatting changed line"""
        result = format_line_with_inline_diff("hello", "hallo", True)
        self.assertIn('<span class="inline-diff">', result)

    def test_empty_line(self):
        """Test formatting empty line"""
        result = format_line_with_inline_diff("", "", False)
        self.assertEqual(result, "&nbsp;")

    def test_html_escaping(self):
        """Test HTML special characters are escaped"""
        result = format_line_with_inline_diff("<script>", "<script>", False)
        self.assertIn("&lt;", result)
        self.assertIn("&gt;", result)
        self.assertNotIn("<script>", result)


class TestCheckFileLimits(unittest.TestCase):
    def test_normal_file(self):
        """Test file within limits"""
        text = "line1\nline2\nline3"
        result = check_file_limits(text, "test.txt")
        self.assertTrue(result)

    def test_binary_file(self):
        """Test binary file detection"""
        text = "normal text\x00binary data"
        result = check_file_limits(text, "test.bin")
        self.assertFalse(result, "Should reject binary files")

    def test_long_line(self):
        """Test excessively long line detection"""
        text = "x" * 9000  # Exceeds 8KB limit
        result = check_file_limits(text, "test.txt")
        self.assertFalse(result, "Should reject files with very long lines")

    def test_multiple_normal_lines(self):
        """Test file with many normal lines"""
        text = "\n".join(["line " + str(i) for i in range(1000)])
        result = check_file_limits(text, "test.txt")
        self.assertTrue(result)


if __name__ == '__main__':
    # Run tests with verbosity
    unittest.main(verbosity=2)
