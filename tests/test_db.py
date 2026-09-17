import os
import unittest
from omni_core.db import (
    init_db, upsert_project, get_projects, get_project,
    delete_project, toggle_project_favorite, update_project_last_opened,
    add_scan_root, get_scan_roots, remove_scan_root, sync_to_json, sync_from_json
)

class TestDatabase(unittest.TestCase):
    def setUp(self):
        init_db()

    def test_project_crud(self):
        test_path = "D:\\TempTestProjects\\proj_alpha"
        data = {
            "name": "Alpha Service",
            "path": test_path,
            "description": "Microservice for tests",
            "tags": ["python", "fastapi", "backend"],
            "default_agent": "claude",
            "project_type": "python"
        }
        p = upsert_project(data)
        self.assertIsNotNone(p)
        self.assertEqual(p["name"], "Alpha Service")
        self.assertIn("fastapi", p["tags"])

        # Fetch by ID
        fetched = get_project(p["id"])
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched["path"], test_path)

        # Toggle favorite
        fav = toggle_project_favorite(p["id"])
        self.assertTrue(fav)
        p_fav = get_project(p["id"])
        self.assertTrue(p_fav["favorite"])

        # Update last opened
        update_project_last_opened(p["id"])
        p_updated = get_project(p["id"])
        self.assertTrue(bool(p_updated["last_opened"]))

        # Query projects with search
        results = get_projects(search="Alpha")
        self.assertTrue(len(results) >= 1)

        # Delete project
        del_ok = delete_project(p["id"])
        self.assertTrue(del_ok)
        self.assertIsNone(get_project(p["id"]))

    def test_scan_roots(self):
        temp_root = os.path.dirname(os.path.abspath(__file__))
        add_scan_root(temp_root)
        roots = get_scan_roots()
        paths = [r["path"] for r in roots]
        self.assertIn(temp_root, paths)
        remove_scan_root(temp_root)

    def test_json_sync(self):
        ok = sync_to_json()
        self.assertTrue(ok)

if __name__ == "__main__":
    unittest.main()
