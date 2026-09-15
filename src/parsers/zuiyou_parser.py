from src.parser_factory import register_parser

import random
from urllib.parse import parse_qs, urlparse

from src.parsers.base_parser import BaseParser
from configs.general_constants import USER_AGENT_PC

@register_parser("最右")
class ZuiyouParser(BaseParser):
    def __init__(self, real_url):
        super().__init__(real_url)
        self.headers = {
            "Content-Type": "application/json",
            "User-Agent": random.choice(USER_AGENT_PC),
            "Referer": "https://share.xiaochuankeji.cn/",
        }
        self.data = self.fetch_html_data()

    def fetch_html_data(self):
        video_id = parse_qs(urlparse(self.real_url).query).get("pid", [None])[0]
        if not video_id:
            return {}
        try:
            int_video_id = int(video_id)
        except (TypeError, ValueError):
            return {}
        req_url = "https://share.xiaochuankeji.cn/planck/share/post/detail_h5"
        post_data = {"h_av": "5.2.13.011", "pid": int_video_id}
        try:
            resp = self.session.post(req_url, headers=self.headers, json=post_data, timeout=10)
            resp.raise_for_status()
            return resp.json()
        except Exception:
            return {}
    def _extract_image_url(self, img_node):
        if not isinstance(img_node, dict):
            return None
        urls_dict = img_node.get("urls")
        if isinstance(urls_dict, dict):
            for key in ("origin", "origin_webp", "540", "540_webp", "360", "360_webp"):
                cand = urls_dict.get(key, {}).get("urls", [])
                if cand and isinstance(cand, list):
                    return cand[0]
        return img_node.get("url")

    def get_real_video_url(self):
        try:
            data = self.data["data"]["post"]
            videos = data.get("videos") or {}
            if not videos:
                return None
            video_key = str(data["imgs"][0]["id"]) if data.get("imgs") else None
            if video_key and video_key in videos:
                return videos[video_key].get("url")
            for v in videos.values():
                if isinstance(v, dict) and v.get("url"):
                    return v["url"]
            return None
        except Exception:
            return None

    def get_image_list(self):
        try:
            data = self.data["data"]["post"]
            if data.get("videos"):
                return []
            imgs = data.get("imgs") or []
            image_urls = []
            for img in imgs:
                url = self._extract_image_url(img)
                if url:
                    image_urls.append(url)
            return image_urls
        except Exception:
            return []

    def get_cover_photo_url(self):
        try:
            data = self.data["data"]["post"]
            if data.get("cover"):
                return data["cover"]
            imgs = data.get("imgs") or []
            if imgs:
                return self._extract_image_url(imgs[0]) or ""
            return ""
        except Exception:
            return ""

    def get_title_content(self):
        return None

    def get_description(self):
        try:
            return self.data["data"]["post"]["content"] or None
        except (KeyError, TypeError):
            return None

    def get_author_info(self):
        try:
            member = self.data["data"]["post"]["member"]
            avatar_urls = member.get("avatar_urls", {}).get("origin", {}).get("urls", [])
            return {
                "nickname": member.get("name", ""),
                "author_id": str(member.get("id", "")),
                "avatar": avatar_urls[0] if avatar_urls else "",
            }
        except (KeyError, TypeError):
            return {}
