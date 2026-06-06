#!/usr/bin/env python3
"""
💰 莎总你好 — 每日投资早报 全能版
模块：美股 | A股基金 | 国际形势 | 流动性 | BTC | 新手课堂 | English Corner
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
PUSH_CHANNEL = os.environ.get("PUSH_CHANNEL", "serverchan")
PUSH_TOKEN = os.environ.get("PUSH_TOKEN", "")
GF_NAME = os.environ.get("GF_NAME", "莎总")
ENABLE_BTC = os.environ.get("ENABLE_BTC", "true").lower() == "true"

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
    {"topic": "什么是ETF", "desc": "ETF是什么？和普通基金有什么区别？为什么很多人推荐新手买ETF？举几个热门ETF例子（沪深300ETF、纳斯达克100ETF等）。"},
    {"topic": "什么是指数", "desc": "上证指数、深证成指、沪深300、创业板指分别是什么？纳斯达克、标普500呢？它们之间有什么关系？"},
    {"topic": "分散投资", "desc": "为什么不能把鸡蛋放在一个篮子里？资产配置是什么意思？股票、基金、债券、现金怎么搭配？给新手一个简单的配置建议。"},
    {"topic": "定投是什么", "desc": "什么是定投？为什么说定投适合新手和上班族？微笑曲线是什么？定投多久能看到效果？给一个具体的定投方案示例。"},
    {"topic": "MACD指标入门", "desc": "MACD是什么？红柱绿柱代表什么？金叉死叉怎么看？零轴上方和下方有什么区别？用今天的图举例。"},
    {"topic": "RSI指标入门", "desc": "RSI是什么？超买超卖是什么意思？RSI>70和RSI<30分别说明什么？用今天的实际数据举例。"},
    {"topic": "支撑位和压力位", "desc": "什么是支撑位和压力位？怎么找到它们？突破和跌破分别意味着什么？用今天的市场举例。"},
    {"topic": "什么是牛市和熊市", "desc": "牛市和熊市的定义是什么？怎么判断当前是牛还是熊？历史上有哪些著名的牛熊？当前市场处于什么阶段？"},
    {"topic": "股票和基金的区别", "desc": "买股票和买基金有什么区别？各自的风险和收益特点？新手应该先买哪个？为什么？"},
    {"topic": "什么是北向资金", "desc": "北向资金是什么？为什么叫'聪明钱'？北向资金流入流出对A股有什么影响？今天北向资金的动向如何？"},
    {"topic": "股息和分红", "desc": "什么是股息率？高股息策略适合什么人？A股有哪些经典的高股息股票？和银行存款比哪个划算？"},
    {"topic": "什么是做空", "desc": "做空是什么意思？为什么有人能在股票下跌时赚钱？融券、期权、反向ETF分别是什么？做空的风险是什么？"},
    {"topic": "止损和止盈", "desc": "什么是止损？什么是止盈？为什么这两个纪律这么重要？常见的止损方法有哪些？给一个实用的建议。"},
    {"topic": "什么是打新", "desc": "IPO打新是什么？A股打新怎么参与？中签率一般多少？打新真的稳赚吗？有什么风险？"},
    {"topic": "布林带入门", "desc": "布林带是什么？上轨、中轨、下轨分别代表什么？缩口和开口说明什么？用今天的例子讲解。"},
    {"topic": "什么是融资融券", "desc": "融资融券是什么？杠杆交易的风险有多大？为什么新手不建议碰杠杆？举个简单的例子说明。"},
    {"topic": "读懂财报：利润表", "desc": "利润表上最重要的3个数字是什么？营收、净利润、毛利率分别说明什么？怎么判断一家公司赚不赚钱？"},
    {"topic": "读懂财报：资产负债表", "desc": "资产负债表看什么？负债率多少算健康？流动比率是什么？怎么判断一家公司会不会暴雷？"},
    {"topic": "什么是ROE", "desc": "ROE是什么？巴菲特为什么最看重ROE？ROE>15%意味着什么？A股哪些公司ROE常年很高？"},
    {"topic": "什么是护城河", "desc": "巴菲特说的'护城河'是什么？品牌、专利、网络效应、成本优势分别是什么护城河？举几个中外公司的例子。"},
    {"topic": "基金定投实战", "desc": "沪深300定投 vs 中证500定投 vs 纳斯达克100定投，历史回报对比如何？该选哪个？什么时候开始定投最好？"},
    {"topic": "情绪与投资心理", "desc": "为什么追涨杀跌是人的本能？锚定效应、损失厌恶、羊群效应分别是什么？怎么克服这些心理陷阱？"},
    {"topic": "构建你的第一个投资组合", "desc": "如果莎总有1万块想开始投资，怎么分配？给一个具体的、适合新手的组合方案，包括具体的基金/ETF推荐和比例。"},
]

# ============================================================
#  各模块 System Prompt
# ============================================================

PROMPT_US_MARKET = f"""你是一位美股分析师，给没有金融背景的女生"{GF_NAME}"写每日快讯。
分析当前美股：1.三大指数涨跌 2.情绪判断 3.科技股亮点 4.操作建议
要求：大白话+emoji，每点1-2句，总共200字以内。"""

PROMPT_CN_MARKET = f"""你是一位A股和基金分析师，给没有金融背景的女生"{GF_NAME}"写中国市场快讯。
分析内容：
1. A股主要指数（上证、深证、创业板）今日/近期表现
2. 热门板块和概念（新能源、AI、消费、医药等）
3. 基金市场动态（明星基金表现、ETF资金流向）
4. 北向资金动向（外资在买还是卖？）
5. 简单的操作建议

要求：大白话+emoji，通俗易懂，总共250字以内。这是给中国投资者看的，重点关注A股和国内基金。"""

PROMPT_GEOPOLITICS = f"""你是一位国际形势分析师，给没有金融背景的女生"{GF_NAME}"解读今天的国际大事对金融市场的影响。
分析内容：
1. 今天最重要的1-2条国际新闻（中美关系、地缘冲突、贸易政策、央行动态等）
2. 这些事件对股市/汇市/大宗商品意味着什么？
3. 对中国市场和普通投资者有什么具体影响？

要求：
- 像在和朋友聊八卦一样讲国际大事，不要用外交辞令
- 重点解释"这件事跟我的钱有什么关系"
- 用 emoji 增加趣味
- 总共200字以内"""

PROMPT_MACRO = f"""你是一位宏观分析师，给没有金融背景的女生"{GF_NAME}"写流动性日报。
分析：1.美联储态度 2.利率环境 3.美元走势 4.风险信号
用"钱多不多"这种大白话，总共200字以内，带emoji。最后一句话总结。"""

PROMPT_BTC = f"""你是一位加密货币分析师，给不懂区块链的女生"{GF_NAME}"写BTC日报。
分析：1.价格走势 2.情绪 3.ETF动向 4.周期阶段
零术语，200字以内，带emoji，最后给判断。"""

def get_lesson_prompt(lesson):
    return f"""你是一位投资教育专家，正在给完全零基础的女生"莎总"上投资小课堂。

今天的课题是：**{lesson['topic']}**

教学要求：{lesson['desc']}

格式要求：
- 用最通俗的大白话，就像在教闺蜜
- 可以用生活中的比喻来解释金融概念
- 用 emoji 增加趣味性
- 如果涉及图表（如K线），用文字描述形状，比如"像一根长长的红色柱子，上下各伸出一小截线"
- 结合当天的实际市场案例来教学
- 最后出一道简单的思考题让莎总想想
- 总字数控制在300字以内"""

PROMPT_ENGLISH = f"""You are a bilingual financial analyst creating an English learning section for a Chinese girl "{GF_NAME}" who wants to practice English through investment news.

Take today's key market events and write a short English summary with Chinese annotations:

Format:
1. Write 3-4 sentences in simple English about today's market highlights
2. After each sentence, put key financial terms in parentheses with Chinese translation, like: The S&P 500 **rallied** (大涨) 1.2% on strong **earnings reports** (财报).
3. Add a "Word of the Day" section: pick ONE useful financial English word/phrase, give pronunciation hint, meaning, and example sentence
4. End with a simple English sentence {GF_NAME} can practice saying

Requirements:
- Use simple English (A2-B1 level)
- Bold the key financial terms
- Make it fun and practical
- Total length: 150-200 English words + Chinese annotations
- Write the section header in Chinese: "🇬🇧 莎总的英语角 | English Corner"
"""

# ============================================================
#  调用 DeepSeek API
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
    bj_time = datetime.now(timezone(timedelta(hours=8)))
    date_str = bj_time.strftime("%m月%d日")
    weekdays = "一二三四五六日"
    weekday = weekdays[bj_time.weekday()]
    day_of_year = bj_time.timetuple().tm_yday
    date_query = bj_time.strftime('%Y年%m月%d日')

    greetings = [
        f"{GF_NAME}早安～新的一天元气满满！",
        f"{GF_NAME}今天也要开开心心搞钱鸭～",
        f"{GF_NAME}早！先看看市场再搞钱💪",
        f"{GF_NAME}你好！今天的投资日报来啦～",
        f"叮咚～{GF_NAME}的专属投资助手上线！",
        f"{GF_NAME}早上好！知识就是力量💡",
        f"{GF_NAME}今天也要做最有钱的自己！",
    ]
    greeting = greetings[day_of_year % len(greetings)]

    # 今天的课程
    lesson = LESSONS[day_of_year % len(LESSONS)]

    title = f"💰 {GF_NAME}你好 | {date_str} 周{weekday}"

    parts = []
    parts.append(f"## {greeting}\n")
    parts.append(f"*{date_str} 星期{weekday} · 第{day_of_year % len(LESSONS) + 1}课*\n")
    parts.append("---\n")

    # ── 模块1: 美股 ──
    print("📊 [1/7] 美股市场...")
    try:
        result = call_deepseek(PROMPT_US_MARKET, f"分析{date_query}的美股市场。")
        parts.append(f"### 📊 美股速览\n\n{result}\n\n---\n")
    except Exception as e:
        print(f"  ⚠️ 失败: {e}")
        parts.append("### 📊 美股速览\n\n> 数据获取中，稍后补上～\n\n---\n")

    # ── 模块2: A股&基金 ──
    print("🇨🇳 [2/7] A股基金...")
    try:
        result = call_deepseek(PROMPT_CN_MARKET, f"分析{date_query}的A股和基金市场。")
        parts.append(f"### 🇨🇳 A股 & 基金\n\n{result}\n\n---\n")
    except Exception as e:
        print(f"  ⚠️ 失败: {e}")
        parts.append("### 🇨🇳 A股 & 基金\n\n> 数据获取中～\n\n---\n")

    # ── 模块3: 国际形势 ──
    print("🌍 [3/7] 国际形势...")
    try:
        result = call_deepseek(PROMPT_GEOPOLITICS, f"分析{date_query}最重要的国际事件及其对金融市场的影响。")
        parts.append(f"### 🌍 国际大事 & 对钱包的影响\n\n{result}\n\n---\n")
    except Exception as e:
        print(f"  ⚠️ 失败: {e}")
        parts.append("### 🌍 国际形势\n\n> 今天国际线安静，明天见～\n\n---\n")

    # ── 模块4: 流动性 ──
    print("🌊 [4/7] 流动性...")
    try:
        result = call_deepseek(PROMPT_MACRO, f"分析{date_query}的全球流动性环境。")
        parts.append(f"### 🌊 资金面（钱多不多？）\n\n{result}\n\n---\n")
    except Exception as e:
        print(f"  ⚠️ 失败: {e}")

    # ── 模块5: BTC（可选）──
    if ENABLE_BTC:
        print("₿  [5/7] 比特币...")
        try:
            result = call_deepseek(PROMPT_BTC, f"分析{date_query}比特币的状态。")
            parts.append(f"### ₿ 比特币动态\n\n{result}\n\n---\n")
        except Exception as e:
            print(f"  ⚠️ 失败: {e}")
    else:
        print("₿  [5/7] 比特币...跳过")

    # ── 模块6: 新手课堂 ──
    print(f"📖 [6/7] 莎总课堂：{lesson['topic']}...")
    try:
        result = call_deepseek(
            get_lesson_prompt(lesson),
            f"今天是{date_query}，请结合今天的市场情况来教这节课。"
        )
        parts.append(f"### 📖 莎总课堂 · 第{day_of_year % len(LESSONS) + 1}课\n\n")
        parts.append(f"**今日课题：{lesson['topic']}**\n\n{result}\n\n---\n")
    except Exception as e:
        print(f"  ⚠️ 失败: {e}")

    # ── 模块7: English Corner ──
    print("🇬🇧 [7/7] 英语角...")
    try:
        result = call_deepseek(
            PROMPT_ENGLISH,
            f"Today is {bj_time.strftime('%B %d, %Y')}. Create the English Corner based on today's market."
        )
        parts.append(f"### 🇬🇧 莎总的英语角\n\n{result}\n\n---\n")
    except Exception as e:
        print(f"  ⚠️ 失败: {e}")

    # ── 结尾 ──
    parts.append(f"\n> ⚠️ 以上分析仅供学习参考，不构成投资建议\n>\n> 💕 {GF_NAME}今天也加油！爱你 ❤️\n")

    body = "\n".join(parts)
    return title, body


# ============================================================
#  微信推送
# ============================================================

def push_serverchan(title: str, body: str):
    url = f"https://sctapi.ftqq.com/{PUSH_TOKEN}.send"
    resp = requests.post(url, json={"title": title, "desp": body}, timeout=15)
    resp.raise_for_status()
    result = resp.json()
    if result.get("code") == 0:
        print(f"✅ Server酱推送成功！{GF_NAME}会在微信收到～")
    else:
        print(f"❌ 推送失败: {result}")
        sys.exit(1)

def push_pushplus(title: str, body: str):
    url = "https://www.pushplus.plus/send"
    payload = {"token": PUSH_TOKEN, "title": title, "content": body, "template": "markdown"}
    resp = requests.post(url, json=payload, timeout=15)
    resp.raise_for_status()
    result = resp.json()
    if result.get("code") == 200:
        print(f"✅ PushPlus推送成功！{GF_NAME}会在微信收到～")
    else:
        print(f"❌ 推送失败: {result}")
        sys.exit(1)

def push_wecom(title: str, body: str):
    payload = {"msgtype": "markdown", "markdown": {"content": f"## {title}\n\n{body}"}}
    resp = requests.post(PUSH_TOKEN, json=payload, timeout=15)
    resp.raise_for_status()
    result = resp.json()
    if result.get("errcode") == 0:
        print(f"✅ 企业微信推送成功！")
    else:
        print(f"❌ 推送失败: {result}")
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
    print(f"🌅 {GF_NAME}你好 — 每日投资早报 全能版")
    print("=" * 50)

    if not DEEPSEEK_API_KEY:
        print("❌ 请设置 DEEPSEEK_API_KEY"); sys.exit(1)
    if not PUSH_TOKEN:
        print("❌ 请设置 PUSH_TOKEN"); sys.exit(1)
    if PUSH_CHANNEL not in PUSH_HANDLERS:
        print(f"❌ 不支持: {PUSH_CHANNEL}"); sys.exit(1)

    day_of_year = datetime.now(timezone(timedelta(hours=8))).timetuple().tm_yday
    lesson = LESSONS[day_of_year % len(LESSONS)]

    print(f"🤖 模型: DeepSeek ({DEEPSEEK_MODEL})")
    print(f"📱 渠道: {PUSH_CHANNEL}")
    print(f"💝 称呼: {GF_NAME}")
    print(f"📖 今日课程: {lesson['topic']}")
    print(f"₿  BTC: {'开启' if ENABLE_BTC else '关闭'}")
    print()

    title, body = generate_briefing()

    print(f"\n📝 早报预览 ({len(body)} 字):")
    print("-" * 40)
    print(f"标题: {title}")
    print(body[:800] + "..." if len(body) > 800 else body)
    print("-" * 40)

    print("\n📤 推送中...")
    PUSH_HANDLERS[PUSH_CHANNEL](title, body)
    print(f"\n🎉 今日早报已送达！{GF_NAME}打开微信就能看～")

if __name__ == "__main__":
    main()
