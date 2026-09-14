import os
import unittest
from unittest.mock import patch

from src.utils.cookie_manager import get_platform_cookie, PLATFORM_COOKIE_ALIASES


class CookieManagerTest(unittest.TestCase):
    def test_reads_direct_env_var(self):
        with patch.dict(os.environ, {"XHS_COOKIE": "a1=from_env_123;"}):
            cookie = get_platform_cookie("xhs")
            self.assertEqual(cookie, "a1=from_env_123;")

    def test_reads_custom_env_var(self):
        with patch.dict(os.environ, {"MY_CUSTOM_COOKIE": "token=custom_456;"}):
            cookie = get_platform_cookie("douyin", env_var="MY_CUSTOM_COOKIE")
            self.assertEqual(cookie, "token=custom_456;")

    def test_falls_back_to_alias_env(self):
        with patch.dict(os.environ, {"XIAOHONGSHU_COOKIE": "a1=from_alias_789;", "XHS_COOKIE": ""}):
            cookie = get_platform_cookie("xiaohongshu")
            self.assertEqual(cookie, "a1=from_alias_789;")

    def test_returns_empty_string_when_not_configured(self):
        with patch.dict(os.environ, {}, clear=True):
            cookie = get_platform_cookie("nonexistent_platform")
            self.assertEqual(cookie, "")

    def test_supported_platform_aliases(self):
        self.assertIn("xhs", PLATFORM_COOKIE_ALIASES)
        self.assertIn("douyin", PLATFORM_COOKIE_ALIASES)
        self.assertIn("doubao", PLATFORM_COOKIE_ALIASES)
        self.assertIn("yuanbao", PLATFORM_COOKIE_ALIASES)
        self.assertIn("pinduoduo", PLATFORM_COOKIE_ALIASES)
        self.assertIn("bilibili", PLATFORM_COOKIE_ALIASES)


if __name__ == "__main__":
    unittest.main()
