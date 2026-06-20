#!/usr/bin/env python3
"""
💰 莎总你好 — 每日投资早报 全能版
双 Server酱推送：你 + 莎总（都用方糖服务号，稳定免费）
"""

import os, sys, requests
from datetime import datetime, timezone, timedelta

# ============================================================
#  配置
# ============================================================
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
DEEPSEEK_BASE_URL = os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
DEEPSEEK_MODEL = os.environ.get("DEEPSEEK_MODEL", "deepseek-chat")
GF_NAME = os.environ.get("GF_NAME", "莎总")
ENABLE_BTC = os.environ.get("ENABLE_BTC", "true").lower() == "true"

SERVERCHAN_KEY = os.environ.get("SERVERCHAN_KEY", "")
SERVERCHAN_KEY_GF = os.environ.get("SERVERCHAN_KEY_GF", "")

# ============================================================
#  30天循环课程表
# ============================================================
LESSONS = [
    {"topic": "K线图基础", "desc": "什么是K线？红绿代表什么？怎么看开盘价收盘价？用实际股票举例。"},
    {"topic": "常见K线形态", "desc": "大阳线、大阴线、十字星分别说明什么信号？结合案例。"},
    {"topic": "成交量怎么看", "desc": "放量缩量意味着什么？量价配合是什么？"},
    {"topic": "均线入门", "desc": "5日线、20日线、60日线代表什么？金叉死叉是什么？"},
    {"topic": "什么是市盈率PE", "desc": "高PE低PE说明什么？不同行业PE为什么差别大？"},
    {"topic": "什么是市净率PB", "desc": "PB<1意味着什么？什么行业适合看PB？"},
    {"topic": "基金的种类", "desc": "股票基金、债券基金、货币基金、指数基金、ETF区别？新手从哪种开始？"},
    {"topic": "什么是ETF", "desc": "ETF和普通基金区别？为什么推荐新手买ETF？举热门例子。"},
    {"topic": "什么是指数", "desc": "上证、沪深300、创业板、纳斯达克、标普500分别是什么？"},
    {"topic": "分散投资", "desc": "股票基金债券现金怎么搭配？给新手一个简单配置建议。"},
    {"topic": "定投是什么", "desc": "定投适合谁？微笑曲线是什么？给一个具体方案。"},
    {"topic": "MACD指标入门", "desc": "红柱绿柱代表什么？金叉死叉怎么看？"},
    {"topic": "RSI指标入门", "desc": "超买超卖是什么？RSI>70和<30说明什么？"},
    {"topic": "支撑位和压力位", "desc": "怎么找支撑压力位？突破和跌破意味着什么？"},
    {"topic": "什么是牛市和熊市", "desc": "怎么判断牛熊？当前市场处于什么阶段？"},
    {"topic": "股票和基金的区别", "desc": "风险收益特点？新手先买哪个？"},
    {"topic": "什么是北向资金", "desc": "北向资金为什么叫聪明钱？今天动向如何？"},
    {"topic": "股息和分红", "desc": "股息率是什么？高股息策略适合谁？"},
    {"topic": "什么是做空", "desc": "做空怎么赚钱？融券、反向ETF是什么？风险？"},
    {"topic": "止损和止盈", "desc": "为什么纪律重要？常见止损方法？"},
    {"topic": "什么是打新", "desc": "IPO打新怎么参与？真的稳赚吗？"},
    {"topic": "布林带入门", "desc": "上中下轨代表什么？缩口开口说明什么？"},
    {"topic": "什么是融资融券", "desc": "杠杆风险多大？为什么新手别碰？"},
    {"topic": "读懂利润表", "desc": "营收、净利润、毛利率分别说明什么？"},
    {"topic": "读懂资产负债表", "desc": "负债率多少健康？怎么判断会不会暴雷？"},
    {"topic": "什么是ROE", "desc": "巴菲特为什么最看重ROE？哪些公司ROE高？"},
    {"topic": "什么是护城河", "desc": "品牌、网络效应、成本优势分别是什么护城河？"},
    {"topic": "基金定投实战", "desc": "沪深300 vs 中证500 vs 纳斯达克100该选哪个？"},
    {"topic": "情绪与投资心理", "desc": "锚定效应、损失厌恶、羊群效应怎么克服？"},
    {"topic": "构建你的第一个投资组合", "desc": "1万块怎么分配？给新手具体方案。"},
]

# ============================================================
#  System Prompts
# ============================================================
PROMPT_US = f"""美股分析师，给零基础的"{GF_NAME}"写快讯。分析：1.三大指数 2.情绪 3.科技股亮点 4.建议。大白话+emoji，200字以内。"""
PROMPT_CN = f"""A股基金分析师，给零基础的"{GF_NAME}"写快讯。分析：1.A股指数 2.热门板块 3.基金ETF动态 4.北向资金 5.建议。大白话+emoji，250字以内。"""
PROMPT_GEO = f"""国际形势分析师，给零基础的"{GF_NAME}"解读大事对金融的影响。1.今天1-2条大事 2.对股汇商品影响 3.对中国投资者影响。像聊八卦，200字以内，emoji。"""
PROMPT_MACRO = f"""宏观分析师，给零基础的"{GF_NAME}"写流动性日报。1.美联储态度 2.利率 3.美元 4.风险。"钱多不多"大白话，200字以内，emoji。"""
PROMPT_BTC = f"""加密货币分析师，给零基础的"{GF_NAME}"写BTC日报。1.价格 2.情绪 3.ETF 4.周期。零术语，200字以内，emoji。"""

def get_lesson_prompt(lesson):
    return f"""投资教育专家，给零基础的"莎总"上课。课题：{lesson['topic']}。要求：{lesson['desc']}。大白话+比喻+emoji+实际案例+思考题，300字以内。"""

PROMPT_EN = f"""Bilingual financial analyst, create English Corner for "{GF_NAME}".
3-4 simple English sentences about today's market, bold key terms with Chinese: **rallied** (大涨).
Add Word of the Day + practice sentence. Simple English A2-B1, 150 words + Chinese."""

# ============================================================
#  DeepSeek API
# ============================================================
def call_deepseek(system_prompt, user_message):
    resp = requests.post(
        f"{DEEPSEEK_BASE_URL}/v1/chat/completions",
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {DEEPSEEK_API_KEY}"},
        json={"model": DEEPSEEK_MODEL, "max_tokens": 1200, "temperature": 0.7,
              "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_message}]},
        timeout=90)
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]

# ============================================================
#  生成早报
# ============================================================
def generate_briefing():
    bj = datetime.now(timezone(timedelta(hours=8)))
    ds = bj.strftime("%m月%d日")
    wd = "一二三四五六日"[bj.weekday()]
    doy = bj.timetuple().tm_yday
    dq = bj.strftime('%Y年%m月%d日')
    lesson = LESSONS[doy % len(LESSONS)]
    greetings = [f"{GF_NAME}早安～元气满满！", f"{GF_NAME}今天开心搞钱鸭～", f"{GF_NAME}早！先看市场💪",
                 f"{GF_NAME}你好！日报来啦～", f"叮咚～{GF_NAME}的投资助手上线！",
                 f"{GF_NAME}早！知识就是力量💡", f"{GF_NAME}做最有钱的自己！"]
    title = f"{GF_NAME}你好 | {ds} 周{wd}"
    parts = [f"## {greetings[doy % len(greetings)]}\n", f"*{ds} 星期{wd} · 第{doy % len(LESSONS) + 1}课*\n", "---\n"]

    modules = [("📊", "美股速览", PROMPT_US, f"分析{dq}美股。"),
               ("🇨🇳", "A股 & 基金", PROMPT_CN, f"分析{dq}A股基金。"),
               ("🌍", "国际大事", PROMPT_GEO, f"分析{dq}国际事件对金融影响。"),
               ("🌊", "资金面", PROMPT_MACRO, f"分析{dq}流动性。")]
    if ENABLE_BTC:
        modules.append(("₿", "比特币", PROMPT_BTC, f"分析{dq}BTC。"))
    total = len(modules) + 2

    for i, (icon, name, prompt, query) in enumerate(modules, 1):
        print(f"{icon} [{i}/{total}] {name}...")
        try:
            r = call_deepseek(prompt, query)
            parts.append(f"### {icon} {name}\n\n{r}\n\n---\n")
        except Exception as e:
            print(f"  ⚠️ 失败: {e}")
            parts.append(f"### {icon} {name}\n\n> 数据获取中～\n\n---\n")

    print(f"📖 [{len(modules) + 1}/{total}] 课堂：{lesson['topic']}...")
    try:
        r = call_deepseek(get_lesson_prompt(lesson), f"今天是{dq}，结合市场来教。")
        parts.append(f"### 📖 莎总课堂 · 第{doy % len(LESSONS) + 1}课\n\n**{lesson['topic']}**\n\n{r}\n\n---\n")
    except Exception as e:
        print(f"  ⚠️ 失败: {e}")

    print(f"🇬🇧 [{total}/{total}] 英语角...")
    try:
        r = call_deepseek(PROMPT_EN, f"Today is {bj.strftime('%B %d, %Y')}. Create English Corner.")
        parts.append(f"### 🇬🇧 英语角\n\n{r}\n\n---\n")
    except Exception as e:
        print(f"  ⚠️ 失败: {e}")

    parts.append(f"\n> ⚠️ 仅供学习参考，不构成投资建议\n>\n> 💕 {GF_NAME}今天也加油！爱你 ❤️\n")
    return title, "\n".join(parts)

# ============================================================
#  Server酱推送
# ============================================================
def send_serverchan(key, label, title, body):
    if not key:
        print(f"⏭️  {label}未配置，跳过")
        return
    try:
        resp = requests.post(f"https://sctapi.ftqq.com/{key}.send",
                             json={"title": title, "desp": body}, timeout=15)
        resp.raise_for_status()
        r = resp.json()
        if r.get("code") == 0:
            print(f"✅ {label}：推送成功！")
        else:
            print(f"⚠️ {label}推送失败: {r}")
    except Exception as e:
        print(f"⚠️ {label}推送异常: {e}")

# ============================================================
#  主函数
# ============================================================
def main():
    print("=" * 50)
    print(f"🌅 {GF_NAME}你好 — 每日投资早报 全能版")
    print("=" * 50)
    if not DEEPSEEK_API_KEY:
        print("❌ 请设置 DEEPSEEK_API_KEY"); sys.exit(1)
    if not SERVERCHAN_KEY and not SERVERCHAN_KEY_GF:
        print("❌ 至少配置一个 SERVERCHAN_KEY"); sys.exit(1)

    doy = datetime.now(timezone(timedelta(hours=8))).timetuple().tm_yday
    print(f"🤖 DeepSeek ({DEEPSEEK_MODEL})")
    print(f"📱 你的Server酱: {'✅' if SERVERCHAN_KEY else '❌'}")
    print(f"📱 {GF_NAME}的Server酱: {'✅' if SERVERCHAN_KEY_GF else '❌'}")
    print(f"📖 今日课程: {LESSONS[doy % len(LESSONS)]['topic']}\n")

    title, body = generate_briefing()
    print(f"\n📝 早报 {len(body)} 字\n📤 推送中...\n")

    send_serverchan(SERVERCHAN_KEY, "Server酱 → 你自己", title, body)
    send_serverchan(SERVERCHAN_KEY_GF, f"Server酱 → {GF_NAME}", title, body)

    print(f"\n🎉 完毕！")

if __name__ == "__main__":
    main()
