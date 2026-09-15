# 最右 (Zuiyou) 逆向解析指南

本篇详细记录 **最右 (Zuiyou)** 搞笑视频与神评图文帖子的接口抓取与多画质原图解析方案。

---

## 1. 平台特征与支持能力

* **平台标识**：`最右`
* **支持媒体类型**：高清视频 (MP4) / 多图图集 (原图 / WebP) / 封面 / 帖子正文 / 作者信息
* **常见链接形态**：
  * 分享落地页：`https://share.xiaochuankeji.cn/hybrid/share/post?pid=423835942&vid=2542343457`
  * 图文帖子页：`https://share.xiaochuankeji.cn/hybrid/share/post?pid=419346905`
* **Cookie 依赖**：无需 Cookie。

---

## 2. 核心逆向流程

1. **提取帖子 PID**：从分享链接的 Query 中提取 `pid`。
2. **核心接口**：
   * 接口：`POST https://share.xiaochuankeji.cn/planck/share/post/detail_h5`
   * 请求头：`Referer: https://share.xiaochuankeji.cn/`
   * 载荷：`{"h_av": "5.2.13.011", "pid": pid}`
3. **视频与图集双模提取**：
   * **视频模式**：
     * 从 `data.post.imgs[0].id` 获得 `video_key`。
     * 通过 `data.post.videos[video_key].url` 取得最终播放直链。
   * **图集模式 (无视频帖子)**：
     * 遍历 `data.post.imgs` 列表。
     * 针对每张图片，按画质优先级 `origin` (原图无损) -> `origin_webp` -> `540` -> `360` 自适应提取最高清图片直链，并注入 `image_list` 与 `cover_url`。

---

## 3. 测试与验证

* **单元测试**：[tests/test_zuiyou_parser.py](file:///Users/leo/Projects/media-parser/tests/test_zuiyou_parser.py)
* **执行命令**：
  ```bash
  python -m unittest tests/test_zuiyou_parser.py
  ```

