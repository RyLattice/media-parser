import os
from flask import has_app_context


# 平台 Cookie 键名与环境变量别名映射关系
PLATFORM_COOKIE_ALIASES = {
    "xhs": ["XHS_COOKIE", "XIAOHONGSHU_COOKIE"],
    "xiaohongshu": ["XHS_COOKIE", "XIAOHONGSHU_COOKIE"],
    "pinduoduo": ["PINDUODUO_COOKIE", "PDD_COOKIE"],
    "douyin": ["DOUYIN_COOKIE"],
    "yuanbao": ["YUANBAO_COOKIE"],
    "wechat_channels": ["YUANBAO_COOKIE", "WECHAT_CHANNELS_COOKIE"],
    "doubao": ["DOUBAO_COOKIE"],
    "bilibili": ["BILIBILI_COOKIE", "BILI_COOKIE"],
    "weibo": ["WEIBO_COOKIE"],
    "kuaishou": ["KUAISHOU_COOKIE", "KS_COOKIE"],
}

# 管理后台支持配置的 Cookie 列表定义（用于后台页面渲染与持久化）
SUPPORTED_COOKIE_SETTINGS = [
    {
        "key": "xhs_cookie",
        "platform": "xhs",
        "name": "小红书 (Xiaohongshu)",
        "env": "XHS_COOKIE",
        "description": "包含 a1 / webId 访客或登录 web_session 凭据，用于彻底避免小红书 302 重定向到登录页。",
        "placeholder": "例如: a1=18f8...; webId=...; web_session=...",
    },
    {
        "key": "pinduoduo_cookie",
        "platform": "pinduoduo",
        "name": "拼多多 (Pinduoduo)",
        "env": "PINDUODUO_COOKIE",
        "description": "包含 _nano_fp / pdd_user_id 等字段，用于多多视频与商品评价秀高清数据抓取。",
        "placeholder": "例如: _nano_fp=...; pdd_user_id=...",
    },
    {
        "key": "yuanbao_cookie",
        "platform": "yuanbao",
        "name": "腾讯元宝 / 微信视频号",
        "env": "YUANBAO_COOKIE",
        "description": "包含 hy_user / hy_token 等字段，用于微信视频号转写与腾讯元宝多模态解析。",
        "placeholder": "例如: hy_user=...; hy_token=...",
    },
    {
        "key": "douyin_cookie",
        "platform": "douyin",
        "name": "抖音 (Douyin 放映厅长片)",
        "env": "DOUYIN_COOKIE",
        "description": "仅需提供 s_v_web_id / __ac_nonce 防控通行证（无需个人 sessionid），用于影视长片与放映厅。",
        "placeholder": "例如: s_v_web_id=verify_...; __ac_nonce=...",
    },
    {
        "key": "doubao_cookie",
        "platform": "doubao",
        "name": "豆包 (Doubao AI)",
        "env": "DOUBAO_COOKIE",
        "description": "包含 sessionid / passport_csrf_token 等字段，用于豆包 AI 对话与生成音乐/视频提取。",
        "placeholder": "例如: sessionid=...; passport_csrf_token=...",
    },
    {
        "key": "bilibili_cookie",
        "platform": "bilibili",
        "name": "哔哩哔哩 (Bilibili 大会员/高清)",
        "env": "BILIBILI_COOKIE",
        "description": "包含 SESSDATA / bili_jct 等字段，用于大会员专享番剧与 1080P+ 高清码率直链提取。",
        "placeholder": "例如: SESSDATA=...; bili_jct=...",
    },
]


def get_platform_cookie(platform_key: str, env_var: str | None = None) -> str:
    """获取指定平台的 Cookie 凭据。

    支持双轨热更新机制：
    1. 优先从 SQLite 数据库系统设置 (system_settings 表中的 {platform_key}_cookie) 读取后台配置的凭据；
    2. 若未在后台配置或数据库不可用，自动回退读取环境变量 (如 XHS_COOKIE, DOUYIN_COOKIE 等)；
    3. 若均未配置则返回空字符串。
    """
    key_normalized = platform_key.lower().replace("-", "_")
    if env_var is None:
        env_var = f"{key_normalized.upper()}_COOKIE"

    # 1. 尝试从数据库系统设置读取 (在 Flask 应用上下文中)
    try:
        if has_app_context():
            from src.db import setting
            val = setting(f"{key_normalized}_cookie")
            if val and isinstance(val, str) and val.strip():
                return val.strip()
    except Exception:
        pass

    # 2. 回退到指定环境变量
    cookie_from_env = os.getenv(env_var, "").strip()
    if cookie_from_env:
        return cookie_from_env

    # 3. 别名兜底检查
    for alias in PLATFORM_COOKIE_ALIASES.get(key_normalized, []):
        val = os.getenv(alias, "").strip()
        if val:
            return val

    return ""
