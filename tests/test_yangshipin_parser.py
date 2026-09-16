import unittest
from unittest.mock import MagicMock, patch

from src.parsers.yangshipin_parser import YangshipinParser


class YangshipinParserTest(unittest.TestCase):
    def test_parses_portrait_video_successfully(self):
        fake_html = """
        <html>
        <head><title>央视频</title></head>
        <body>
            <script>
            window.__STATE_portrait_video__ = {
                "payloads": {
                    "videoDataList": {
                        "items": [
                            {
                                "videoData": {
                                    "vid": "l00005817wl",
                                    "title": "5次助攻对4次助攻！巅峰对决",
                                    "shareItem": {
                                        "shareImgUrl": "https://jietufengmian.yangshipin.cn/cover1.jpg"
                                    },
                                    "detailFollowItem": {
                                        "actorItem": {
                                            "nickName": {"text": "奥运来了"},
                                            "headUrl": "https://mpuser.ysp.cctv.cn/avatar1.jpeg"
                                        }
                                    }
                                }
                            }
                        ]
                    }
                }
            };
            </script>
        </body>
        </html>
        """

        def mock_fetch(self, vid):
            self.video_url = "https://mp4playcloud-cdn.ysp.cctv.cn/l00005817wl.mp4?vkey=mock"

        with patch.object(YangshipinParser, "fetch_html_content", return_value=fake_html), \
             patch.object(YangshipinParser, "_fetch_video_url_by_vid", side_effect=mock_fetch, autospec=True):
            parser = YangshipinParser("https://m.yangshipin.cn/portrait_video?vid=l00005817wl")
            self.assertEqual(parser.get_title_content(), "5次助攻对4次助攻！巅峰对决")
            self.assertEqual(parser.get_cover_photo_url(), "https://jietufengmian.yangshipin.cn/cover1.jpg")
            self.assertEqual(
                parser.get_author_info(),
                {"name": "奥运来了", "avatar": "https://mpuser.ysp.cctv.cn/avatar1.jpeg"},
            )
            self.assertEqual(parser.get_real_video_url(), "https://mp4playcloud-cdn.ysp.cctv.cn/l00005817wl.mp4?vkey=mock")
            self.assertEqual(parser.get_image_list(), [])

    def test_parses_landscape_video_successfully(self):
        fake_html = """
        <html>
        <head><title>央视频</title></head>
        <body>
            <script>
            window.__STATE_video__ = {
                "payloads": {
                    "sharevideo": {
                        "vid": "v000007pgfu",
                        "title": "《普法栏目剧》远山的守望",
                        "cover_pic": "https://jietufengmian.yangshipin.cn/cover2.jpg",
                        "om_info": {
                            "title": "社会与法频道"
                        }
                    }
                }
            };
            </script>
        </body>
        </html>
        """

        def mock_fetch(self, vid):
            self.video_url = "https://mp4playcloud-cdn.ysp.cctv.cn/v000007pgfu.mp4?vkey=mock"

        with patch.object(YangshipinParser, "fetch_html_content", return_value=fake_html), \
             patch.object(YangshipinParser, "_fetch_video_url_by_vid", side_effect=mock_fetch, autospec=True):
            parser = YangshipinParser("https://m.yangshipin.cn/video?type=0&vid=v000007pgfu")
            self.assertEqual(parser.get_title_content(), "《普法栏目剧》远山的守望")
            self.assertEqual(parser.get_cover_photo_url(), "https://jietufengmian.yangshipin.cn/cover2.jpg")
            self.assertEqual(parser.get_author_info(), {"name": "社会与法频道", "avatar": None})
            self.assertEqual(parser.get_real_video_url(), "https://mp4playcloud-cdn.ysp.cctv.cn/v000007pgfu.mp4?vkey=mock")
            self.assertEqual(parser.get_image_list(), [])

    def test_ckey_generation_and_playvinfo_flow(self):
        probe_resp = MagicMock()
        probe_resp.text = '({"em":85,"exem":-3,"curTime":1789545734})'

        vinfo_resp = MagicMock()
        vinfo_resp.text = '({"s":"o","vl":{"cnt":1,"vi":[{"fn":"test.mp4","fvkey":"ABC123KEY","ul":{"ui":[{"url":"https://mp4playcloud-cdn.ysp.cctv.cn/"}]}}]}})'

        fake_html = """
        <html><body>
        <script>
        window.__STATE_portrait_video__ = {
            "payloads": {"videoDataList": {"items": [{"videoData": {"vid": "test_vid", "title": "测试视频"}}]}}
        };
        </script>
        </body></html>
        """
        with patch.object(YangshipinParser, "fetch_html_content", return_value=fake_html), \
             patch("requests.Session.get", side_effect=[probe_resp, vinfo_resp]):
            parser = YangshipinParser("https://m.yangshipin.cn/portrait_video?vid=test_vid")
            self.assertEqual(
                parser.get_real_video_url(),
                "https://mp4playcloud-cdn.ysp.cctv.cn/test.mp4?vkey=ABC123KEY&platform=2",
            )
            self.assertEqual(parser.get_image_list(), [])

    def test_follows_meta_refresh_redirect(self):
        meta_html = """
        <!DOCTYPE html>
        <meta charset="utf-8">
        <meta http-equiv="refresh" content="0; URL='https://m.yangshipin.cn/portrait_video?vid=5Sqx'"/>
        <title>央视频</title>
        """
        detail_html = """
        <html><body>
            <script>
            window.__STATE_portrait_video__ = {
                "payloads": {
                    "videoDataList": {
                        "items": [
                            {
                                "videoData": {
                                    "title": "跳转后的视频标题",
                                    "shareItem": {"shareImgUrl": "https://jietufengmian.yangshipin.cn/cover3.jpg"}
                                }
                            }
                        ]
                    }
                }
            };
            </script>
        </body></html>
        """
        with patch.object(YangshipinParser, "fetch_html_content", side_effect=[meta_html, detail_html]), \
             patch.object(YangshipinParser, "_fetch_video_url_by_vid", return_value=None):
            parser = YangshipinParser("https://www.yspapp.cn/5Sqx")
            self.assertEqual(parser.get_title_content(), "跳转后的视频标题")
            self.assertEqual(parser.get_cover_photo_url(), "https://jietufengmian.yangshipin.cn/cover3.jpg")
            self.assertEqual(parser.get_image_list(), ["https://jietufengmian.yangshipin.cn/cover3.jpg"])

    def test_handles_empty_or_broken_html(self):
        with patch.object(YangshipinParser, "fetch_html_content", return_value="<html><body>404 Not Found</body></html>"), \
             patch.object(YangshipinParser, "_fetch_video_url_by_vid", return_value=None):
            parser = YangshipinParser("https://m.yangshipin.cn/video?vid=empty")
            self.assertEqual(parser.get_title_content(), "")
            self.assertIsNone(parser.get_cover_photo_url())
            self.assertIsNone(parser.get_author_info())
            self.assertEqual(parser.get_image_list(), [])


if __name__ == "__main__":
    unittest.main()
