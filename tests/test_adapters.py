import unittest
from omni_core.adapters import get_all_adapters, get_adapter, CAP_SUPPORTED

class TestAdapters(unittest.TestCase):
    def test_get_all_adapters(self):
        adapters = get_all_adapters()
        self.assertGreaterEqual(len(adapters), 6)
        self.assertIn("claude", adapters)
        self.assertIn("opencode", adapters)
        self.assertIn("cursor", adapters)
        self.assertIn("antigravity", adapters)

    def test_claude_adapter(self):
        ad = get_adapter("claude")
        self.assertEqual(ad.id, "claude")
        caps = ad.get_capabilities()
        self.assertEqual(caps["project_instructions"], CAP_SUPPORTED)
        self.assertTrue(bool(ad.docs_url))

    def test_construct_launch_cmd(self):
        ad = get_adapter("claude")
        cmd = ad.construct_launch_cmd("D:\\test", profile={"extra_args": ["--model", "sonnet"]})
        self.assertIn("--model", cmd)
        self.assertIn("sonnet", cmd)

if __name__ == "__main__":
    unittest.main()
