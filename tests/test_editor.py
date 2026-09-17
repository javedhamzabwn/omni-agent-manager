import os
import unittest
from omni_core.editor import (
    validate_content, generate_diff, detect_file_format,
    read_file_safe, write_file_safe
)

class TestEditor(unittest.TestCase):
    def test_file_format_detection(self):
        self.assertEqual(detect_file_format("config.json"), "json")
        self.assertEqual(detect_file_format("settings.jsonc"), "json")
        self.assertEqual(detect_file_format("service.yaml"), "yaml")
        self.assertEqual(detect_file_format("pyproject.toml"), "toml")
        self.assertEqual(detect_file_format("CLAUDE.md"), "markdown")

    def test_validate_content(self):
        ok, _ = validate_content('{"key": "value"}', "json")
        self.assertTrue(ok)
        bad_ok, _ = validate_content('{key: value}', "json")
        self.assertFalse(bad_ok)

    def test_generate_diff(self):
        diff = generate_diff("line1\nline2\n", "line1\nline2_modified\n", "test.txt")
        self.assertIn("-line2", diff)
        self.assertIn("+line2_modified", diff)

    def test_safe_read_write(self):
        temp_file = os.path.join(os.path.dirname(__file__), "temp_edit_test.json")
        try:
            ok, _, _ = write_file_safe(temp_file, '{"test": 1}', validate=True)
            self.assertTrue(ok)
            data = read_file_safe(temp_file)
            self.assertTrue(data["success"])
            self.assertEqual(data["format"], "json")
        finally:
            if os.path.exists(temp_file):
                os.remove(temp_file)

if __name__ == "__main__":
    unittest.main()
