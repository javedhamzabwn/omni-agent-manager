import os
import unittest
from omni_core.paths import (
    normalize_path, is_safe_subpath, quote_windows_arg,
    detect_terminals, detect_editors, get_default_project_roots
)

class TestPaths(unittest.TestCase):
    def test_normalize_path(self):
        p = "D:\\Projects\\..\\Projects\\my-service\\"
        norm = normalize_path(p)
        self.assertFalse(norm.endswith("\\"))
        self.assertNotIn("..", norm)

    def test_path_with_spaces_and_unicode(self):
        p = "D:\\Javed Hamza\\Projects\\测试项目\\app"
        norm = normalize_path(p)
        self.assertIn("Javed Hamza", norm)
        self.assertIn("测试项目", norm)

    def test_is_safe_subpath(self):
        parent = "D:\\Projects\\alpha"
        child_safe = "D:\\Projects\\alpha\\sub\\file.txt"
        child_escape = "D:\\Projects\\beta\\other.txt"
        self.assertTrue(is_safe_subpath(child_safe, parent))
        self.assertFalse(is_safe_subpath(child_escape, parent))

    def test_quote_windows_arg(self):
        self.assertEqual(quote_windows_arg("simple"), "simple")
        self.assertEqual(quote_windows_arg("path with spaces"), '"path with spaces"')
        self.assertEqual(quote_windows_arg('quoted"arg'), '"quoted\\"arg"')

    def test_detect_terminals(self):
        terms = detect_terminals()
        self.assertIsInstance(terms, dict)
        self.assertTrue("cmd" in terms or "powershell" in terms)

    def test_detect_editors(self):
        eds = detect_editors()
        self.assertIsInstance(eds, dict)
        self.assertTrue("notepad" in eds)

    def test_default_project_roots(self):
        roots = get_default_project_roots()
        self.assertIsInstance(roots, list)
        self.assertTrue(len(roots) >= 1)

if __name__ == "__main__":
    unittest.main()
