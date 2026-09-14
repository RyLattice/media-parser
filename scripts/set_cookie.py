#!/usr/bin/env python3
"""CLI tool to view and update platform cookies in media-parser's SQLite database."""

import argparse
import os
import sqlite3
import sys

DEFAULT_DB_PATH = os.getenv("DATABASE_PATH", "data/media_parser.db")

SUPPORTED_PLATFORMS = {
    "xhs": "xhs_cookie",
    "xiaohongshu": "xhs_cookie",
    "douyin": "douyin_cookie",
    "doubao": "doubao_cookie",
    "yuanbao": "yuanbao_cookie",
    "pinduoduo": "pinduoduo_cookie",
    "bilibili": "bilibili_cookie",
}


def main():
    parser = argparse.ArgumentParser(description="管理 media-parser 数据库中的平台 Cookie 凭据")
    parser.add_argument("--db", default=DEFAULT_DB_PATH, help=f"SQLite 数据库路径 (默认: {DEFAULT_DB_PATH})")
    parser.add_argument("--list", action="store_true", help="列出当前数据库中所有已配置的 Cookie")
    parser.add_argument("--platform", "-p", help="平台标识 (如 xhs, douyin, doubao, yuanbao, pinduoduo, bilibili)")
    parser.add_argument("--cookie", "-c", help="要设置的 Cookie 字符串内容")
    parser.add_argument("--delete", action="store_true", help="删除指定平台的 Cookie")

    args = parser.parse_args()

    # 尝试按相对路径或当前目录定位数据库
    db_path = args.db
    if not os.path.exists(db_path):
        candidate = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "media_parser.db")
        if os.path.exists(candidate):
            db_path = candidate

    if not os.path.exists(db_path):
        print(f"❌ 数据库文件不存在: {db_path} (请使用 --db 指定正确的路径)")
        sys.exit(1)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 确保 system_settings 表存在
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS system_settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
    """)

    if args.list or (not args.platform and not args.cookie):
        cursor.execute("SELECT key, value FROM system_settings WHERE key LIKE '%_cookie'")
        rows = cursor.fetchall()
        print(f"\n📋 当前数据库 [{db_path}] 中已配置的平台 Cookie:")
        print("-" * 65)
        if not rows:
            print("  (暂无配置任何 Cookie，将走环境变量或默认匿名规则)")
        for k, v in rows:
            masked = (v[:15] + "..." + v[-10:]) if len(v) > 30 else v
            print(f"  • {k:<20}: {masked}")
        print("-" * 65)
        conn.close()
        return

    platform_key = args.platform.lower().strip()
    setting_key = SUPPORTED_PLATFORMS.get(
        platform_key,
        f"{platform_key}_cookie" if not platform_key.endswith("_cookie") else platform_key
    )

    if args.delete:
        cursor.execute("DELETE FROM system_settings WHERE key = ?", (setting_key,))
        conn.commit()
        print(f"✅ 已删除 {setting_key} 配置")
        conn.close()
        return

    if not args.cookie:
        cursor.execute("SELECT value FROM system_settings WHERE key = ?", (setting_key,))
        row = cursor.fetchone()
        if row:
            print(f"\n🔑 {setting_key} 当前值:\n{row[0]}\n")
        else:
            print(f"\n⚪ {setting_key} 当前未在数据库中配置。\n")
        conn.close()
        return

    cookie_value = args.cookie.strip()
    cursor.execute(
        "INSERT INTO system_settings (key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value = excluded.value",
        (setting_key, cookie_value)
    )
    conn.commit()
    conn.close()
    print(f"✅ 成功更新 {setting_key}！(长度: {len(cookie_value)} 字符)")


if __name__ == "__main__":
    main()
