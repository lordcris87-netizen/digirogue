"""Regression checks for DigiRogue. Run: python -m unittest discover -s tests -v
No external packages required for static checks.
"""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]

class DigiRogueStaticTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.page = (ROOT / "index.html").read_text(encoding="utf-8")
        cls.server = (ROOT / "server.py").read_text(encoding="utf-8")
        cls.render = (ROOT / "render.yaml").read_text(encoding="utf-8")

    def test_free_plan_without_paid_disk(self):
        self.assertRegex(self.render, r"(?m)^\s*plan:\s*free\s*$")
        self.assertNotRegex(self.render, r"(?m)^\s*disk:\s*$")

    def test_reconnect_and_manual_retry(self):
        for token in ('scheduleReconnect', 'retryConnection', 'checkServerHealth', 'new WebSocket'):
            with self.subTest(token=token):
                self.assertIn(token, self.page)

    def test_multiplayer_ranking_and_blue_shield(self):
        for token in ('/api/leaderboard', 'ESCUDO AZUL ACTIVADO', 'rewardChoices', 'choose_reward'):
            with self.subTest(token=token):
                self.assertIn(token, self.page)
        for token in ("'/ws'", "'/api/health'", "'/api/leaderboard'"):
            self.assertIn(token, self.server)

    def test_assets_exist(self):
        for name in ('portada.webp','bat.png','kunemon.png','agumon_idle.png'):
            with self.subTest(name=name):
                self.assertTrue((ROOT / 'assets' / name).is_file())

    def test_separated_cover_assets_and_dimensions(self):
        import struct
        import json
        folder = ROOT / 'assets' / 'title_layers'
        expected = {
            'agumon': (298,297),
            'gabumon': (275,305),
            'bat': (205,131),
            'bird': (176,208)
        }
        for name, expected_size in expected.items():
            with self.subTest(name=name):
                path = folder / (name + '.png')
                data = path.read_bytes()[:26]
                self.assertEqual(data[:8], bytes([137,80,78,71,13,10,26,10]))
                self.assertEqual(struct.unpack('>II', data[16:24]), expected_size)
                self.assertEqual(data[25], 6, 'Character PNG must have RGBA transparency')
        bg=(folder / 'background.webp').read_bytes()[:12]
        self.assertEqual(bg[:4], b'RIFF')
        self.assertEqual(bg[8:], b'WEBP')
        meta = json.loads((folder/'manifest.json').read_text(encoding='utf-8'))
        self.assertEqual(set(meta),set(expected))
        self.assertIn('setOriginalTitleMotionMode',self.page)
        self.assertIn('originalTitleLayers=null',self.page)

    def test_dev_preview_remains_separate(self):
        self.assertTrue((ROOT / 'preview-animations.html').is_file())
        self.assertIn('drawTitleActors', self.page)

    def test_animated_title_renders_only_when_home_visible(self):
        self.assertIn("screen==='home'", self.page)
        self.assertIn('reducedMotion.matches', self.page)
        self.assertIn('document.hidden', self.page)

    def test_title_atlas_frame_boundaries(self):
        self.assertIn('image.naturalWidth%actor.cell', self.page)
        self.assertIn('image.naturalHeight%actor.cell', self.page)


if __name__ == '__main__':
    unittest.main()
