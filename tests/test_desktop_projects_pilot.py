import asyncio
import unittest
import omni_agent_manager as m

class TestDesktopProjectsPilot(unittest.IsolatedAsyncioTestCase):
    async def test_projects_desktop_interface(self):
        app = m.AgentCustomizerDesktopApp()
        async with app.run_test() as pilot:
            # Verify app loaded
            self.assertIsNotNone(app)
            
            # Check projects tab exists
            tabs = app.query_one("#tabs-main", m.TabbedContent)
            self.assertIsNotNone(tabs)
            
            # Switch to Projects tab via keybinding 'p'
            await pilot.press("p")
            await pilot.pause(0.1)
            self.assertEqual(tabs.active, "pane-projects")
            print("Successfully switched to pane-projects via 'p' shortcut.")
            
            # Verify projects table and buttons exist
            p_table = app.query_one("#table-projects", m.DataTable)
            self.assertIsNotNone(p_table)
            btn_add = app.query_one("#btn-add-project", m.Button)
            self.assertIsNotNone(btn_add)
            btn_scan = app.query_one("#btn-scan-projects", m.Button)
            self.assertIsNotNone(btn_scan)
            
            # Switch to Sessions tab via keybinding 'x'
            await pilot.press("x")
            await pilot.pause(0.1)
            self.assertEqual(tabs.active, "pane-sessions")
            print("Successfully switched to pane-sessions via 'x' shortcut.")
            
            # Test DesktopAddProjectModal
            add_modal = m.DesktopAddProjectModal(app.agents)
            app.push_screen(add_modal)
            await pilot.pause(0.1)
            self.assertIsInstance(app.screen, m.DesktopAddProjectModal)
            app.pop_screen()
            await pilot.pause(0.1)
            print("DesktopAddProjectModal verified.")
            
            # Test DesktopProjectScanModal
            scan_modal = m.DesktopProjectScanModal()
            app.push_screen(scan_modal)
            await pilot.pause(0.1)
            self.assertIsInstance(app.screen, m.DesktopProjectScanModal)
            app.pop_screen()
            await pilot.pause(0.1)
            print("DesktopProjectScanModal verified.")

if __name__ == "__main__":
    unittest.main()
