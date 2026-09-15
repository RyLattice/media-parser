import json
import unittest
from unittest.mock import patch, MagicMock

from configs.general_constants import USER_AGENT_M
from src.parsers.kuaishou_parser import KuaishouParser


class KuaishouParserHeadersTest(unittest.TestCase):
    def test_builds_headers_with_configured_mobile_user_agent(self):
        parser = KuaishouParser.__new__(KuaishouParser)
        parser.custom_cookie = ""

        with patch("src.parsers.kuaishou_parser.random.choice", return_value="mobile-user-agent") as choice:
            headers = parser._build_mobile_headers()

        choice.assert_called_once_with(USER_AGENT_M)
        self.assertEqual(headers["User-Agent"], "mobile-user-agent")
        self.assertEqual(headers["referer"], "https://v.m.chenzhongtech.com/")

    def test_graphql_video_parsing(self):
        parser = KuaishouParser.__new__(KuaishouParser)
        parser.page_type = "GRAPHQL"
        parser.video_id = "test_video_123"
        parser.structured_data = {
            "status": 1,
            "author": {
                "id": "author_001",
                "name": "创作者小明",
                "headerUrl": "https://tx-avatar.kuaishou.com/avatar.jpg"
            },
            "photo": {
                "id": "test_video_123",
                "caption": "快手精彩无水印视频",
                "coverUrl": "https://tx-cover.kuaishou.com/cover.jpg",
                "photoUrl": "https://tx-video.kuaishou.com/video_clean.mp4",
                "mainMvUrls": [
                    {"url": "https://tx-video.kuaishou.com/video_clean.mp4"}
                ]
            }
        }

        self.assertEqual(parser.get_real_video_url(), "https://tx-video.kuaishou.com/video_clean.mp4")
        self.assertEqual(parser.get_description(), "快手精彩无水印视频")
        self.assertEqual(parser.get_cover_photo_url(), "https://tx-cover.kuaishou.com/cover.jpg")
        self.assertEqual(parser.get_author_info(), {
            "nickname": "创作者小明",
            "unique_id": "author_001",
            "avatar": "https://tx-avatar.kuaishou.com/avatar.jpg"
        })
        self.assertEqual(parser.get_image_list(), [])

    def test_graphql_atlas_parsing(self):
        parser = KuaishouParser.__new__(KuaishouParser)
        parser.page_type = "GRAPHQL"
        parser.video_id = "test_atlas_456"
        parser.structured_data = {
            "status": 1,
            "author": {
                "id": "author_002",
                "name": "摄影师小红",
                "headerUrl": "https://tx-avatar.kuaishou.com/avatar2.jpg"
            },
            "photo": {
                "id": "test_atlas_456",
                "caption": "快手图集分享",
                "coverUrl": "https://tx-cover.kuaishou.com/cover2.jpg",
                "atlas": {
                    "cdn": "https://tx-atlas.kuaishou.com",
                    "list": [
                        "image1.webp",
                        "image2.webp"
                    ]
                }
            }
        }

        self.assertIsNone(parser.get_real_video_url())
        self.assertEqual(parser.get_description(), "快手图集分享")
        self.assertEqual(parser.get_cover_photo_url(), "https://tx-cover.kuaishou.com/cover2.jpg")
        self.assertEqual(parser.get_author_info(), {
            "nickname": "摄影师小红",
            "unique_id": "author_002",
            "avatar": "https://tx-avatar.kuaishou.com/avatar2.jpg"
        })
        self.assertEqual(parser.get_image_list(), [
            "https://tx-atlas.kuaishou.com/image1.webp",
            "https://tx-atlas.kuaishou.com/image2.webp"
        ])

    def test_blocked_payload_detection(self):
        self.assertTrue(KuaishouParser._is_blocked_payload('{"result": 2}'))
        self.assertTrue(KuaishouParser._is_blocked_payload('{"data": {"result": 400002, "bizName": "ANTICRAWL_DEFAULT"}}'))
        self.assertFalse(KuaishouParser._is_blocked_payload('<html><body>Hello</body></html>'))

    @patch("src.parsers.kuaishou_parser.get_platform_cookie", return_value="custom_kuaishou_cookie")
    @patch("src.parsers.kuaishou_parser.requests.get")
    @patch("src.parsers.kuaishou_parser.requests.post")
    def test_anticrawl_triggers_cookie_required(self, mock_post, mock_get, mock_cookie):
        mock_resp_get = MagicMock()
        mock_resp_get.text = json.dumps({"result": 2})
        mock_resp_get.status_code = 200
        mock_get.return_value = mock_resp_get

        mock_resp_post = MagicMock()
        mock_resp_post.text = json.dumps({"data": {"result": 400002, "bizName": "ANTICRAWL_DEFAULT"}})
        mock_resp_post.status_code = 200
        mock_post.return_value = mock_resp_post

        with patch("utils.web_fetcher.UrlParser.get_video_id", return_value="3x123456"):
            parser = KuaishouParser("https://v.kuaishou.com/3x123456")
            self.assertTrue(parser.cookie_required)
            self.assertIsNotNone(parser.terminal_error)
            self.assertEqual(parser.terminal_error["error_code"], "KUAISHOU_COOKIE_REQUIRED")


if __name__ == "__main__":
    unittest.main()
