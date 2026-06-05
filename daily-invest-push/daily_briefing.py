#!/usr/bin/env python3
"""
💰 莎总你好 — 每日投资早报生成 + 微信推送
基于 Day1Global-Skills 的三大日常分析模块，使用 DeepSeek API

推送渠道：Server酱 / PushPlus / 企业微信Webhook
"""

import os
import sys
import json
import requests
from datetime import datetime, timezone, timedelta

# ============================================================
#  配置（从环境变量读取，在 GitHub Secrets 中设置）
# ============================================================
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
DEEPSEEK_BASE_URL = os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
DEEPSEEK_MODEL = os.environ.get("DEEPSEEK_MODEL", "deepseek-chat")
PUSH_CHANNEL = os.environ.get("PUSH_CHANNEL", "serverchan")  # serverchan / pushplus / wecom
PUSH_TOKEN = os.environ.get("PUSH_TOKEN", "")
GF_NAME = os.environ.get("GF_NAME", "莎总")
ENABLE_BTC = os.environ.get("ENABLE_BTC", "true").lower() == "true"

# ============================================================
#  三大分析模块的 System Prompt
# ============================================================

PROMPT_MARKET_SENTIMENT = """你是一位专业但亲切的美股市场分析师，正在给一位对投资感兴趣但没有金融背景的女生写每日早报。她的昵称叫"莎总"。

请分析当前美股市场情绪，覆盖以下方面：
1. 市场整体涨跌和主要指数表现（标普500、纳斯达克、道琼斯）
2. 市场恐惧/贪婪程度判断
3. 科技股近期走势亮点
4. 值得关注的行业轮动信号

要求：
- 用大白话解释，像在和好朋友聊天
- 每个要点1-2句话就够，不要长篇大论
- 用 emoji 让内容生动
- 最后给一句简短的操作建议（观望/关注/谨慎）
- 总字数控制在300字以内"""

PROMPT_MACRO_LIQUIDITY = """你是一位宏观经济分析师，正在给一位没有金融背景的女生"莎总"写通俗易懂的流动性日报。

请分析当前全球流动性环境：
1. 美联储最近的态度是鹰派还是鸽派？对市场意味着什么？
2. 利率环境：当前利率水平对股市是利好还是利空？
3. 美元走势：强势还是弱势？对投资有什么影响？
4. 有没有什么需要注意的风险信号？

要求：
- 把"流动性"翻译成"市场上的钱多不多"这种大白话
- 用生活化的比喻解释复杂概念
- 用 emoji 增加趣味
- 最后用一句话总结：现在是"水多鱼好抓"还是"水少要小心"
- 总字数控制在250字以内"""

PROMPT_BTC = """你是一位加密货币分析师，正在给一位对BTC感兴趣但完全不懂区块链的女生"莎总"写日报。

请分析比特币当前状态：
1. BTC近期价格走势和关键价位
2. 市场情绪是偏贪婪还是偏恐惧？
3. 机构资金（ETF）是在买入还是卖出？
4. 当前处于周期的哪个阶段？

要求：
- 零术语，用最直白的话
- 把链上数据翻译成"大户在干嘛""散户在干嘛"
- 用 emoji 增加趣味
- 最后给一个简单判断：现在是"可以关注""继续等待"还是"要小心"
- 总字数控制在250字以内"""

# ============================================================
#  调用 DeepSeek API（OpenAI 兼容格式）
# ============================================================

def call_deepseek(system_prompt: str, user_message: str) -> str:
    """调用 DeepSeek API 获取分析结果"""
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
    }
    payload = {
        "model": DEEPSEEK_MODEL,
        "max_tokens": 1024,
        "temperature": 0.7,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
    }
    resp = requests.post(
        f"{DEEPSEEK_BASE_URL}/v1/chat/completions",
        headers=headers,
        json=payload,
        timeout=90,
    )
    resp.raise_for_status()
    data = resp.json()
    return data["choices"][0]["message"]["content"]


# ============================================================
#  生成每日早报
# ============================================================

def generate_briefing() -> tuple:
    """生成完整的每日早报，返回 (标题, 正文Markdown)"""

    bj_time = datetime.now(timezone(timedelta(hours=8)))
    date_str = bj_time.strftime("%m月%d日")
    weekdays = "一二三四五六日"
    weekday = weekdays[bj_time.weekday()]

    greetings = [
        f"{GF_NAME}早安～新的一天元气满满！",
        f"{GF_NAME}今天也要开开心心的哦～",
        f"{GF_NAME}早！先看看市场再搞钱💪",
        f"{GF_NAME}你好！今天的投资日报来啦～",
        f"叮咚～{GF_NAME}的专属投资助手上线啦！",
        f"{GF_NAME}早上好！美好的早晨从了解市场开始～",
        f"{GF_NAME}今天也要做最棒的自己！先看看行情～",
    ]
    greeting = greetings[bj_time.timetuple().tm_yday % len(greetings)]

    title = f"💰 {GF_NAME}你好 | {date_str} 周{weekday}"

    parts = []
    parts.append(f"## {greeting}\n")
    parts.append(f"*{date_str} 星期{weekday}*\n")
    parts.append("---\n")

    # 模块1: 市场情绪
    print("📊 正在生成美股市场情绪分析...")
    try:
        sentiment = call_deepseek(
            PROMPT_MARKET_SENTIMENT,
            f"请给我今天（{bj_time.strftime('%Y年%m月%d日')}）的美股市场情绪分析。",
        )
        parts.append(f"### 📊 美股市场速览\n\n{sentiment}\n\n---\n")
    except Exception as e:
        print(f"  ⚠️ 市场情绪分析失败: {e}")
        parts.append("### 📊 美股市场速览\n\n> 今天数据获取遇到点小问题，莎总明天见～\n\n---\n")

    # 模块2: 流动性
    print("🌊 正在生成宏观流动性分析...")
    try:
        liquidity = call_deepseek(
            PROMPT_MACRO_LIQUIDITY,
            f"请分析当前（{bj_time.strftime('%Y年%m月%d日')}）的全球流动性环境。",
        )
        parts.append(f"### 🌊 资金面（钱多不多？）\n\n{liquidity}\n\n---\n")
    except Exception as e:
        print(f"  ⚠️ 流动性分析失败: {e}")
        parts.append("### 🌊 资金面\n\n> 数据开小差了，明天补上～\n\n---\n")

    # 模块3: BTC（可选）
    if ENABLE_BTC:
        print("₿ 正在生成比特币分析...")
        try:
            btc = call_deepseek(
                PROMPT_BTC,
                f"请分析当前（{bj_time.strftime('%Y年%m月%d日')}）比特币的状态。",
            )
            parts.append(f"### ₿ 比特币动态\n\n{btc}\n\n---\n")
        except Exception as e:
            print(f"  ⚠️ BTC分析失败: {e}")

    parts.append(f"\n> ⚠️ 以上分析仅供参考，投资要量力而行哦～\n>\n> 💕 {GF_NAME}今天也加油！\n")

    body = "\n".join(parts)
    return title, body


# ============================================================
#  微信推送渠道
# ============================================================

def push_serverchan(title: str, body: str):
    """Server酱推送 (https://sct.ftqq.com/)"""
    url = f"https://sctapi.ftqq.com/{PUSH_TOKEN}.send"
    resp = requests.post(url, json={"title": title, "desp": body}, timeout=15)
    resp.raise_for_status()
    result = resp.json()
    if result.get("code") == 0:
        print("✅ Server酱推送成功！莎总会在微信收到消息～")
    else:
        print(f"❌ Server酱推送失败: {result}")
        sys.exit(1)


def push_pushplus(title: str, body: str):
    """PushPlus推送 (https://www.pushplus.plus/)"""
    url = "https://www.pushplus.plus/send"
    payload = {
        "token": PUSH_TOKEN,
        "title": title,
        "content": body,
        "template": "markdown",
    }
    resp = requests.post(url, json=payload, timeout=15)
    resp.raise_for_status()
    result = resp.json()
    if result.get("code") == 200:
        print("✅ PushPlus推送成功！莎总会在微信收到消息～")
    else:
        print(f"❌ PushPlus推送失败: {result}")
        sys.exit(1)


def push_wecom(title: str, body: str):
    """企业微信Webhook推送"""
    url = PUSH_TOKEN
    payload = {
        "msgtype": "markdown",
        "markdown": {"content": f"## {title}\n\n{body}"},
    }
    resp = requests.post(url, json=payload, timeout=15)
    resp.raise_for_status()
    result = resp.json()
    if result.get("errcode") == 0:
        print("✅ 企业微信推送成功！莎总会在微信收到消息～")
    else:
        print(f"❌ 企业微信推送失败: {result}")
        sys.exit(1)


PUSH_HANDLERS = {
    "serverchan": push_serverchan,
    "pushplus": push_pushplus,
    "wecom": push_wecom,
}


# ============================================================
#  主函数
# ============================================================

def main():
    print("=" * 50)
    print(f"🌅 {GF_NAME}你好 — 每日投资早报生成器")
    print("=" * 50)

    if not DEEPSEEK_API_KEY:
        print("❌ 请设置 DEEPSEEK_API_KEY 环境变量")
        sys.exit(1)
    if not PUSH_TOKEN:
        print("❌ 请设置 PUSH_TOKEN 环境变量")
        sys.exit(1)
    if PUSH_CHANNEL not in PUSH_HANDLERS:
        print(f"❌ 不支持的推送渠道: {PUSH_CHANNEL}，支持: {', '.join(PUSH_HANDLERS.keys())}")
        sys.exit(1)

    print(f"🤖 AI 模型: DeepSeek ({DEEPSEEK_MODEL})")
    print(f"📱 推送渠道: {PUSH_CHANNEL}")
    print(f"💝 称呼: {GF_NAME}")
    print(f"₿  BTC分析: {'开启' if ENABLE_BTC else '关闭'}")
    print()

    title, body = generate_briefing()

    print()
    print("📝 早报预览:")
    print("-" * 40)
    print(f"标题: {title}")
    print(body[:600] + "..." if len(body) > 600 else body)
    print("-" * 40)
    print()

    print("📤 正在推送到微信...")
    PUSH_HANDLERS[PUSH_CHANNEL](title, body)

    print()
    print(f"🎉 今日早报已送达！{GF_NAME}打开微信就能看到～")


if __name__ == "__main__":
    main()
