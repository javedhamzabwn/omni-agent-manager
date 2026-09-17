import unittest
from omni_core.cli_projects import handle_project_cli, handle_agent_cli

class TestCliSubcommands(unittest.TestCase):
    def test_project_list_cli(self):
        rc = handle_project_cli(["list"])
        self.assertEqual(rc, 0)

    def test_project_list_json_cli(self):
        rc = handle_project_cli(["list", "--json"])
        self.assertEqual(rc, 0)

    def test_agent_list_cli(self):
        rc = handle_agent_cli(["list"])
        self.assertEqual(rc, 0)

    def test_agent_detect_cli(self):
        rc = handle_agent_cli(["detect"])
        self.assertEqual(rc, 0)

if __name__ == "__main__":
    unittest.main()
