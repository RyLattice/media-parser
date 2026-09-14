import os
import tempfile
import unittest
from unittest.mock import patch
from flask import Flask

from src.db import init_app, init_db, set_setting
from src.utils.cookie_manager import get_platform_cookie, SUPPORTED_COOKIE_SETTINGS


class CookieManagerTest(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.temp_dir.name, "test.db")
        self.app = Flask(__name__)
        self.app.config["TESTING"] = True
        self.app.config["DATABASE"] = self.db_path
        init_app(self.app)
        with self.app.app_context():
            init_db()

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_database_setting_takes_precedence_over_env(self):
        with self.app.app_context():
            set_setting("xhs_cookie", "a1=from_database_123;")
            with patch.dict(os.environ, {"XHS_COOKIE": "a1=from_env_456;"}):
                cookie = get_platform_cookie("xhs")
                self.assertEqual(cookie, "a1=from_database_123;")

    def test_falls_back_to_env_when_database_empty(self):
        with self.app.app_context():
            with patch.dict(os.environ, {"XHS_COOKIE": "a1=from_env_456;"}):
                cookie = get_platform_cookie("xhs")
                self.assertEqual(cookie, "a1=from_env_456;")

    def test_falls_back_to_alias_env(self):
        # 即使没有 app_context 也能安全回退到别名环境变量
        with patch.dict(os.environ, {"XIAOHONGSHU_COOKIE": "a1=from_alias_789;", "XHS_COOKIE": ""}):
            cookie = get_platform_cookie("xiaohongshu")
            self.assertEqual(cookie, "a1=from_alias_789;")

    def test_returns_empty_string_when_nothing_configured(self):
        with patch.dict(os.environ, {}, clear=True):
            cookie = get_platform_cookie("nonexistent_platform")
            self.assertEqual(cookie, "")

    def test_supported_cookie_settings_structure(self):
        keys = [item["key"] for item in SUPPORTED_COOKIE_SETTINGS]
        self.assertIn("xhs_cookie", keys)
        self.assertIn("pinduoduo_cookie", keys)
        self.assertIn("yuanbao_cookie", keys)
        self.assertIn("douyin_cookie", keys)
        self.assertIn("doubao_cookie", keys)
        self.assertIn("bilibili_cookie", keys)


if __name__ == "__main__":
    unittest.main()
