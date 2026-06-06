#!/usr/bin/env python3
"""
💰 莎总你好 — 每日投资早报 全能版（双通道推送）
Server酱 → 你自己 | PushPlus → 莎总（都免费）
"""

import os
import sys
import json
import requests
from datetime import datetime, timezone, timedelta

# ============================================================
#  配置
# ============================================================
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
DEEPSEEK_BASE_URL = os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
DEEPSEEK_MODEL = os.environ.get("DEEPSEEK_MODEL", "deepseek-chat")
GF_NAME = os.environ.get("GF_NAME", "莎总")
ENABLE_BTC = os.environ.get("ENABLE_BTC", "true").lower() == "true"

# 双通道 Token
SERVERCHAN_KEY = os.environ.get("SERVERCHAN_KEY", "")   # 你的 Server酱 SendKey
PUSHPLUS_TOKEN = os.environ.get("PUSHPLUS_TOKEN", "")   # 莎总的 PushPlus Token

# ============================================================
#  新手课堂 — 30天循环课程表
# ============================================================
LESSONS = [
    {"topic": "K线图基础", "desc": "什么是K线（蜡烛图）？红绿分别代表什么？怎么看开盘价、收盘价、最高价、最低价？用今天的实际股票走势举例说明。"},
    {"topic": "常见K线形态", "desc": "讲解3种最常见的K线形态：大阳线、大阴线、十字星，分别说明什么信号？结合当天实际案例举例。"},
    {"topic": "成交量怎么看", "desc": "成交量是什么？放量和缩量分别意味着什么？'量价配合'是什么意思？用今天的市场数据举例。"},
    {"topic": "均线入门", "desc": "什么是均线（MA）？5日线、20日线、60日线分别代表什么？金叉和死叉是什么？用今天的例子说明。"},
    {"topic": "什么是市盈率PE", "desc": "PE是什么？高PE和低PE分别说明什么？不同行业的PE为什么差别很大？用当前热门股票的实际PE举例。"},
    {"topic": "什么是市净率PB", "desc": "PB是什么？PB<1意味着什么？什么行业适合看PB？结合当天A股银行股举例。"},
    {"topic": "基金的种类", "desc": "股票基金、债券基金、货币基金、指数基金、ETF有什么区别？各适合什么人？新手应该从哪种开始？"},
    {"topic": "什么是ETF", "desc": "ETF是什么？和普通基金有什么区别？为什么很多人推荐新手买ETF？举几个热门ETF例子。"},
    {"topic": "什么是指数", "desc": "上证指数、深证成指、沪深300、创业板指分别是什么？纳斯达克、标普500呢？"},
    {"topic": "分散投资", "desc": "为什么不能把鸡蛋放在一个篮子里？股票、基金、债券、现金怎么搭配？给新手一个简单的配置建议。"},
    {"topic": "定投是什么", "desc": "什么是定投？为什么说定投适合新手和上班族？微笑曲线是什么？给一个具体的定投方案示例。"},
    {"topic": "MACD指标入门", "desc": "MACD是什么？红柱绿柱代表什么？金叉死叉怎么看？用今天的图举例。"},
    {"topic": "RSI指标入门", "desc": "RSI是什么？超买超卖是什么意思？RSI>70和RSI<30分别说明什么？"},
    {"topic": "支撑位和压力位", "desc": "什么是支撑位和压力位？怎么找到它们？突破和跌破分别意味着什么？"},
    {"topic": "什么是牛市和熊市", "desc": "牛市和熊市的定义？怎么判断当前是牛还是熊？当前市场处于什么阶段？"},
    {"topic": "股票和基金的区别", "desc": "买股票和买基金有什么区别？各自的风险和收益特点？新手应该先买哪个？"},
    {"topic": "什么是北向资金", "desc": "北向资金是什么？为什么叫'聪明钱'？今天北向资金的动向如何？"},
    {"topic": "股息和分红", "desc": "什么是股息率？高股息策略适合什么人？A股有哪些经典的高股息股票？"},
    {"topic": "什么是做空", "desc": "做空是什么意思？融券、期权、反向ETF分别是什么？做空的风险是什么？"},
    {"topic": "止损和止盈", "desc": "什么是止损止盈？为什么纪律重要？常见的止损方法有哪些？"},
    {"topic": "什么是打新", "desc": "IPO打新是什么？A股打新怎么参与？打新真的稳赚吗？"},
    {"topic": "布林带入门", "desc": "布林带是什么？上轨中轨下轨代表什么？缩口和开口说明什么？"},
    {"topic": "什么是融资融券", "desc": "融资融券是什么？杠杆交易的风险有多大？为什么新手不建议碰？"},
    {"topic": "读懂财报：利润表", "desc": "利润表最重要的3个数字？营收、净利润、毛利率分别说明什么？"},
    {"topic": "读懂财报：资产负债表", "desc": "资产负债表看什么？负债率多少算健康？怎么判断公司会不会暴雷？"},
    {"topic": "什么是ROE", "desc": "ROE是什么？巴菲特为什么最看重ROE？A股哪些公司ROE常年很高？"},
    {"topic": "什么是护城河", "desc": "巴菲特说的'护城河'是什么？品牌、网络效应、成本优势分别是什么？"},
    {"topic": "基金定投实战", "desc": "沪深300 vs 中证500 vs 纳斯达克100定投，历史回报对比？该选哪个？"},
    {"topic": "情绪与投资心理", "desc": "追涨杀跌为什么是本能？锚定效应、损失厌恶、羊群效应怎么克服？"},
    {"topic": "构建你的第一个投资组合", "desc": "如果有1万块想开始投资，怎么分配？给一个适合新手的具体方案。"},
]

# ============================================================
#  System Prompts
# ============================================================

PROMPT_US_MARKET = f"""你是美股分析师，给零基础的"{GF_NAME}"写每日快讯。
分析：1.三大指数涨跌 2.情绪判断 3.科技股亮点 4.操作建议
大白话+emoji，每点1-2句，200字以内。"""

PROMPT_CN_MARKET = f"""你是A股和基金分析师，给零基础的"{GF_NAME}"写中国市场快讯。
分析：1.A股主要指数表现 2.热门板块（新能源/AI/消费/医药）3.基金和ETF动态 4.北向资金 5.操作建议
大白话+emoji，250字以内。"""

PROMPT_GEOPOLITICS = f"""你是国际形势分析师，给零基础的"{GF_NAME}"解读国际大事对金融的影响。
分析：1.今天最重要的1-2条国际新闻 2.对股市/汇市/商品的影响 3.对中国投资者的具体影响
像聊八卦一样讲，重点是"跟我的钱有什么关系"，200字以内，带emoji。"""

PROMPT_MACRO = f"""你是宏观分析师，给零基础的"{GF_NAME}"写流动性日报。
分析：1.美联储态度 2.利率环境 3.美元走势 4.风险信号
用"钱多不多"这种大白话，200字以内，带emoji。"""

PROMPT_BTC = f"""你是加密货币分析师，给不懂区块链的"{GF_NAME}"写BTC日报。
分析：1.价格走势 2.情绪 3.ETF动向 4.周期阶段
零术语，200字以内，带emoji。"""

def get_lesson_prompt(lesson):
    return f"""你是投资教育专家，给零基础的"莎总"上投资小课堂。
今日课题：**{lesson['topic']}**
教学要求：{lesson['desc']}
格式：大白话+生活比喻+emoji+当天实际案例+最后出一道思考题。300字以内。"""

PROMPT_ENGLISH = f"""You are a bilingual financial analyst creating an English learning section for "{GF_NAME}".
Write a short English summary of today's market with Chinese annotations:
1. 3-4 simple English sentences about market highlights
2. Bold key terms with Chinese in parentheses: The S&P 500 **rallied** (大涨) 1.2%
3. "Word of the Day": one financial term with meaning and example
4. End with a practice sentence
Use simple English (A2-B1). 150-200 words + Chinese annotations."""

# ============================================================
#  DeepSeek API
# ============================================================

def call_deepseek(system_prompt: str, user_message: str) -> str:
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
    }
    payload = {
        "model": DEEPSEEK_MODEL,
        "max_tokens": 1200,
        "temperature": 0.7,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
    }
    resp = requests.post(
        f"{DEEPSEEK_BASE_URL}/v1/chat/completions",
        headers=headers, json=payload, timeout=90,
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]

# ============================================================
#  生成早报
# ============================================================

def generate_briefing() -> tuple:
    bj = datetime.now(timezone(timedelta(hours=8)))
    date_str = bj.strftime("%m月%d日")
    weekday = "一二三四五六日"[bj.weekday()]
    doy = bj.timetuple().tm_yday
    dq = bj.strftime('%Y年%m月%d日')
    lesson = LESSONS[doy % len(LESSONS)]

    greetings = [
        f"{GF_NAME}早安～新的一天元气满满！",
        f"{GF_NAME}今天也要开开心心搞钱鸭～",
        f"{GF_NAME}早！先看看市场再搞钱💪",
        f"{GF_NAME}你好！投资日报来啦～",
        f"叮咚～{GF_NAME}的专属投资助手上线！",
        f"{GF_NAME}早上好！知识就是力量💡",
        f"{GF_NAME}今天也做最有钱的自己！",
    ]

    title = f"{GF_NAME}你好 | {date_str} 周{weekday}"
    parts = [f"## {greetings[doy % len(greetings)]}\n", f"*{date_str} 星期{weekday} · 第{doy % len(LESSONS) + 1}课*\n", "---\n"]

    modules = [
        ("📊", "美股速览",           PROMPT_US_MARKET,    f"分析{dq}的美股。"),
        ("🇨🇳", "A股 & 基金",       PROMPT_CN_MARKET,    f"分析{dq}的A股和基金。"),
        ("🌍", "国际大事 & 钱包影响", PROMPT_GEOPOLITICS,  f"分析{dq}最重要的国际事件对金融的影响。"),
        ("🌊", "资金面（钱多不多？）", PROMPT_MACRO,       f"分析{dq}的全球流动性。"),
    ]
    if ENABLE_BTC:
        modules.append(("₿", "比特币动态", PROMPT_BTC, f"分析{dq}比特币的状态。"))

    total = len(modules) + 2  # +lesson +english
    for i, (icon, name, prompt, query) in enumerate(modules, 1):
        print(f"{icon} [{i}/{total}] {name}...")
        try:
            r = call_deepseek(prompt, query)
            parts.append(f"### {icon} {name}\n\n{r}\n\n---\n")
        except Exception as e:
            print(f"  ⚠️ 失败: {e}")
            parts.append(f"### {icon} {name}\n\n> 数据获取中～\n\n---\n")

    # 新手课堂
    idx = len(modules) + 1
    print(f"📖 [{idx}/{total}] 莎总课堂：{lesson['topic']}...")
    try:
        r = call_deepseek(get_lesson_prompt(lesson), f"今天是{dq}，结合今天的市场来教。")
        parts.append(f"### 📖 莎总课堂 · 第{doy % len(LESSONS) + 1}课\n\n**今日课题：{lesson['topic']}**\n\n{r}\n\n---\n")
    except Exception as e:
        print(f"  ⚠️ 失败: {e}")

    # 英语角
    print(f"🇬🇧 [{total}/{total}] 英语角...")
    try:
        r = call_deepseek(PROMPT_ENGLISH, f"Today is {bj.strftime('%B %d, %Y')}. Create English Corner.")
        parts.append(f"### 🇬🇧 莎总的英语角\n\n{r}\n\n---\n")
    except Exception as e:
        print(f"  ⚠️ 失败: {e}")

    parts.append(f"\n> ⚠️ 以上分析仅供学习参考，不构成投资建议\n>\n> 💕 {GF_NAME}今天也加油！爱你 ❤️\n")
    return title, "\n".join(parts)

# ============================================================
#  双通道推送
# ============================================================

def push_serverchan(title: str, body: str):
    """推给你自己"""
    if not SERVERCHAN_KEY:
        print("⏭️  Server酱未配置，跳过")
        return
    url = f"https://sctapi.ftqq.com/{SERVERCHAN_KEY}.send"
    resp = requests.post(url, json={"title": title, "desp": body}, timeout=15)
    resp.raise_for_status()
    result = resp.json()
    if result.get("code") == 0:
        print("✅ Server酱 → 你自己：推送成功！")
    else:
        print(f"⚠️ Server酱推送失败: {result}")

def push_pushplus(title: str, body: str):
    """推给莎总"""
    if not PUSHPLUS_TOKEN:
        print("⏭️  PushPlus未配置，跳过")
        return
    url = "https://www.pushplus.plus/send"
    payload = {"token": PUSHPLUS_TOKEN, "title": title, "content": body, "template": "markdown"}
    resp = requests.post(url, json=payload, timeout=15)
    resp.raise_for_status()
    result = resp.json()
    if result.get("code") == 200:
        print(f"✅ PushPlus → {GF_NAME}：推送成功！")
    else:
        print(f"⚠️ PushPlus推送失败: {result}")

# ============================================================
#  主函数
# ============================================================

def main():
    print("=" * 50)
    print(f"🌅 {GF_NAME}你好 — 每日投资早报 全能版")
    print("=" * 50)

    if not DEEPSEEK_API_KEY:
        print("❌ 请设置 DEEPSEEK_API_KEY"); sys.exit(1)
    if not SERVERCHAN_KEY and not PUSHPLUS_TOKEN:
        print("❌ 至少设置一个推送渠道（SERVERCHAN_KEY 或 PUSHPLUS_TOKEN）"); sys.exit(1)

    doy = datetime.now(timezone(timedelta(hours=8))).timetuple().tm_yday
    lesson = LESSONS[doy % len(LESSONS)]

    print(f"🤖 模型: DeepSeek ({DEEPSEEK_MODEL})")
    print(f"📱 Server酱: {'✅ 已配置' if SERVERCHAN_KEY else '❌ 未配置'}")
    print(f"📱 PushPlus: {'✅ 已配置' if PUSHPLUS_TOKEN else '❌ 未配置'}")
    print(f"💝 称呼: {GF_NAME}")
    print(f"📖 今日课程: {lesson['topic']}")
    print()

    title, body = generate_briefing()

    print(f"\n📝 早报生成完毕（{len(body)} 字）")
    print("\n📤 开始推送...\n")

    # 双通道：同时推两个
    push_serverchan(title, body)
    push_pushplus(title, body)

    print(f"\n🎉 推送完毕！")

if __name__ == "__main__":
    main()
