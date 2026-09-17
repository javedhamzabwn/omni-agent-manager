import os
import unittest
from omni_core.projects import inspect_project_metadata, detect_project_type, find_git_root

class TestDiscovery(unittest.TestCase):
    def test_inspect_current_repo(self):
        repo_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        meta = inspect_project_metadata(repo_dir)
        self.assertTrue(meta["valid"])
        self.assertEqual(meta["name"], "omni-agent-manager")
        self.assertEqual(meta["project_type"], "python")
        self.assertTrue(bool(meta["git_root"]))
        
        inst_names = [i["name"] for i in meta["instructions"]]
        self.assertIn("README.md", inst_names)

    def test_detect_project_type(self):
        repo_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        ptype = detect_project_type(repo_dir)
        self.assertEqual(ptype, "python")

    def test_find_git_root(self):
        repo_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        git_root = find_git_root(repo_dir)
        self.assertIsNotNone(git_root)
        self.assertTrue(os.path.isdir(os.path.join(git_root, ".git")))

if __name__ == "__main__":
    unittest.main()
