#!/usr/bin/env python3
"""
💰 莎总你好 — 每日投资早报 + 真实岗位推送
Tavily 联网搜索真实岗位 → DeepSeek 筛选分析 → Server酱推送
"""

import os, sys, json, requests
from datetime import datetime, timezone, timedelta

# ============================================================
#  配置
# ============================================================
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
DEEPSEEK_BASE_URL = os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
DEEPSEEK_MODEL = os.environ.get("DEEPSEEK_MODEL", "deepseek-chat")
TAVILY_API_KEY = os.environ.get("TAVILY_API_KEY", "")
GF_NAME = os.environ.get("GF_NAME", "莎总")
ENABLE_BTC = os.environ.get("ENABLE_BTC", "true").lower() == "true"
SERVERCHAN_KEY = os.environ.get("SERVERCHAN_KEY", "")

# ============================================================
#  30天投资课程表
# ============================================================
LESSONS = [
    {"topic": "K线图基础", "desc": "什么是K线？红绿代表什么？用实际股票举例。"},
    {"topic": "常见K线形态", "desc": "大阳线、大阴线、十字星分别说明什么信号？"},
    {"topic": "成交量怎么看", "desc": "放量缩量意味着什么？量价配合是什么？"},
    {"topic": "均线入门", "desc": "5日线、20日线、60日线代表什么？金叉死叉是什么？"},
    {"topic": "什么是市盈率PE", "desc": "高PE低PE说明什么？不同行业PE为什么差别大？"},
    {"topic": "什么是市净率PB", "desc": "PB<1意味着什么？什么行业适合看PB？"},
    {"topic": "基金的种类", "desc": "股票基金、债券基金、货币基金、ETF区别？新手从哪种开始？"},
    {"topic": "什么是ETF", "desc": "ETF和普通基金区别？为什么推荐新手买ETF？"},
    {"topic": "什么是指数", "desc": "上证、沪深300、创业板、纳斯达克、标普500分别是什么？"},
    {"topic": "分散投资", "desc": "股票基金债券现金怎么搭配？给新手一个简单配置建议。"},
    {"topic": "定投是什么", "desc": "定投适合谁？微笑曲线是什么？给一个具体方案。"},
    {"topic": "MACD指标入门", "desc": "红柱绿柱代表什么？金叉死叉怎么看？"},
    {"topic": "RSI指标入门", "desc": "超买超卖是什么？RSI>70和<30说明什么？"},
    {"topic": "支撑位和压力位", "desc": "怎么找支撑压力位？突破和跌破意味着什么？"},
    {"topic": "什么是牛市和熊市", "desc": "怎么判断牛熊？当前市场处于什么阶段？"},
    {"topic": "股票和基金的区别", "desc": "风险收益特点？新手先买哪个？"},
    {"topic": "什么是北向资金", "desc": "北向资金为什么叫聪明钱？"},
    {"topic": "股息和分红", "desc": "股息率是什么？高股息策略适合谁？"},
    {"topic": "什么是做空", "desc": "做空怎么赚钱？风险？"},
    {"topic": "止损和止盈", "desc": "为什么纪律重要？常见止损方法？"},
    {"topic": "什么是打新", "desc": "IPO打新怎么参与？真的稳赚吗？"},
    {"topic": "布林带入门", "desc": "上中下轨代表什么？缩口开口说明什么？"},
    {"topic": "什么是融资融券", "desc": "杠杆风险多大？为什么新手别碰？"},
    {"topic": "读懂利润表", "desc": "营收、净利润、毛利率分别说明什么？"},
    {"topic": "读懂资产负债表", "desc": "负债率多少健康？怎么判断暴雷？"},
    {"topic": "什么是ROE", "desc": "巴菲特为什么最看重ROE？"},
    {"topic": "什么是护城河", "desc": "品牌、网络效应、成本优势分别是什么护城河？"},
    {"topic": "基金定投实战", "desc": "沪深300 vs 中证500 vs 纳斯达克100该选哪个？"},
    {"topic": "情绪与投资心理", "desc": "锚定效应、损失厌恶、羊群效应怎么克服？"},
    {"topic": "构建你的第一个投资组合", "desc": "1万块怎么分配？给新手具体方案。"},
]

# ============================================================
#  求职搜索关键词轮换（30天循环）
# ============================================================
JOB_SEARCHES = [
    {"query": "施耐德电气 ABB 西门子 招聘 2025 2026 中国", "focus": "能源电力外企"},
    {"query": "外企 新能源 项目经理 招聘 中国 本科", "focus": "新能源项目管理"},
    {"query": "外企 产品经理 招聘 中国 应届 本科 2025 2026", "focus": "产品经理"},
    {"query": "西门子 博世 霍尼韦尔 招聘 中国 本科 工程", "focus": "工业自动化外企"},
    {"query": "外企 项目管理 PM 招聘 中国 本科 电气", "focus": "项目管理"},
    {"query": "特斯拉 宁德时代 比亚迪合资 外企 招聘 电气 能源", "focus": "新能源汽车"},
    {"query": "埃森哲 德勤 普华永道 咨询 招聘 本科 能源", "focus": "咨询行业"},
    {"query": "半导体 外企 招聘 中国 英特尔 德州仪器 英飞凌 本科", "focus": "半导体外企"},
    {"query": "医疗器械 外企 招聘 中国 飞利浦 西门子医疗 GE医疗", "focus": "医疗器械"},
    {"query": "外企 销售工程师 技术销售 招聘 中国 本科 电气", "focus": "技术销售"},
    {"query": "外企 管培生 2025 2026 招聘 中国 本科", "focus": "外企管培生"},
    {"query": "数字化转型 外企 招聘 SAP 微软 Oracle 中国", "focus": "数字化转型"},
    {"query": "供应链 运营 外企 招聘 中国 本科 亚马逊 苹果", "focus": "供应链运营"},
    {"query": "ESG 可持续发展 外企 招聘 中国 碳管理 绿色能源", "focus": "ESG可持续发展"},
    {"query": "智能制造 工业互联网 外企 招聘 中国 PTC 西门子", "focus": "智能制造"},
    {"query": "宝洁 联合利华 欧莱雅 快消 外企 招聘 中国 本科", "focus": "快消外企"},
    {"query": "检测认证 SGS TUV BV 招聘 中国 电气 工程师", "focus": "检测认证行业"},
    {"query": "微软中国 亚马逊AWS 谷歌 招聘 项目经理 产品经理", "focus": "互联网大厂"},
    {"query": "AECOM WSP Arup 建筑工程 外企 招聘 电气设计", "focus": "工程设计外企"},
    {"query": "外企 客户成功 客户经理 招聘 中国 本科 2025 2026", "focus": "客户管理"},
    {"query": "博世 大陆 采埃孚 汽车电子 招聘 中国 电气", "focus": "汽车零部件"},
    {"query": "外企 培训师 学习发展 招聘 中国 本科", "focus": "培训发展"},
    {"query": "巴斯夫 陶氏 杜邦 3M 化工 外企 招聘 中国 工程师", "focus": "化工材料外企"},
    {"query": "爱立信 诺基亚 高通 通信 外企 招聘 中国 电气", "focus": "通信外企"},
    {"query": "DHL FedEx 马士基 物流 外企 招聘 中国 运营", "focus": "物流外企"},
    {"query": "外企 市场营销 数字营销 招聘 中国 本科 2025 2026", "focus": "市场营销"},
    {"query": "外企 财务分析 审计 招聘 中国 本科", "focus": "财务审计"},
    {"query": "壳牌 BP 道达尔 能源 外企 招聘 中国 电气 工程", "focus": "石油能源外企"},
    {"query": "航空航天 空客 霍尼韦尔航空 外企 招聘 中国 电气", "focus": "航空航天"},
    {"query": "远程办公 外企 招聘 中国 项目经理 产品经理 2025 2026", "focus": "远程办公岗位"},
]

# ============================================================
#  System Prompts — 投资模块
# ============================================================
PROMPT_US = f"""美股分析师，给"{GF_NAME}"写快讯。
分析：1.三大指数涨跌 2.重点讲清楚：哪些板块涨了哪些跌了，是因为什么事件/消息导致的？（比如某公司发财报、美联储讲话、政策变化、行业新闻等）用"因为…所以…"的逻辑讲清因果关系 3.情绪判断 4.建议
大白话+emoji，300字以内。"""
PROMPT_CN = f"""A股基金分析师，给"{GF_NAME}"写快讯。
分析：1.A股主要指数涨跌 2.重点解释板块涨跌的原因：哪些板块涨了为什么涨？哪些跌了为什么跌？背后是什么政策/新闻/事件驱动的？（比如"新能源涨了是因为国家出了什么补贴政策"、"医药跌了是因为集采降价"这样的因果解释）3.基金ETF动态 4.北向资金 5.建议
大白话+emoji，通俗解释每个涨跌背后的逻辑，让完全不懂的人也能理解"为什么"，350字以内。"""
PROMPT_GEO = f"""国际形势分析师，给"{GF_NAME}"解读大事对金融的影响。1.今天1-2条大事 2.对股汇商品影响 3.对中国投资者影响。像聊八卦，200字以内，emoji。"""
PROMPT_MACRO = f"""宏观分析师，给"{GF_NAME}"写流动性日报。1.美联储态度 2.利率 3.美元 4.风险。"钱多不多"大白话，200字以内，emoji。"""
PROMPT_BTC = f"""加密货币分析师，给"{GF_NAME}"写BTC日报。1.价格 2.情绪 3.ETF 4.周期。零术语，200字以内，emoji。"""

def get_lesson_prompt(lesson):
    return f"""投资教育专家，给"{GF_NAME}"上课。课题：{lesson['topic']}。要求：{lesson['desc']}。大白话+比喻+emoji+实际案例+思考题，300字以内。"""

PROMPT_EN = f"""You are a bilingual storyteller creating a fun English learning section for "{GF_NAME}".

Pick ONE interesting, fun, or heartwarming story that happened recently in the world (NOT financial news). It could be:
- A cool science discovery, a viral social media moment, a funny cultural event
- An inspiring person's story, a weird world record, an adorable animal story
- A fascinating tech breakthrough, a travel destination trending, a food trend

Write it as a SHORT engaging story in simple English with Chinese annotations:
1. Tell the story in 4-5 simple English sentences
2. Bold key vocabulary with Chinese translations: The scientist **discovered** (发现) a new **species** (物种).
3. "Word of the Day": one useful English word from the story with meaning, pronunciation hint, and example
4. End with a fun discussion question in English for practice

Requirements: Simple English (A2-B1), make it genuinely fun and interesting, 150-200 words + Chinese annotations.
Title the section: 🌍 今日趣闻 | Story Time"""

# ============================================================
#  求职分析 Prompt（不含个人背景描述）
# ============================================================
JOB_SYSTEM_PROMPT = """你是一位资深外企猎头顾问。用户会给你一批从网上搜到的真实招聘信息，请你：

1. 从中筛选出**最适合本科学历、1-2年工作经验、电气/能源背景的候选人**的岗位
2. 也可以推荐跨行业的岗位（如项目管理、产品经理、销售等），只要学历和经验门槛匹配
3. **必须是中国境内的岗位**（接受短期出差但不接受常驻国外）
4. 不要推荐明确要求硕士或5年以上经验的岗位

对每个推荐的岗位，请提供：
- 🏢 公司名 + 岗位名
- 📍 工作地点
- 📋 核心职责（2-3条）
- ✅ 任职要求（学历、经验、技能、语言）
- 💰 薪资（如果搜索结果中有就写，没有就根据市场行情估算并标注"预估"）
- 🔗 申请链接（如果搜索结果中有URL就附上）
- 💡 一句话申请建议

如果搜索结果中没有完全匹配的岗位，可以基于搜索到的公司招聘页面信息，推荐该公司当前可能在招的适合岗位。

推荐3-5个岗位，用emoji让排版清晰好看。不要在推送中提及候选人的个人背景信息。"""

SKILL_SYSTEM_PROMPT = """你是一位职业发展导师。用户会给你今天推荐的岗位方向，请提供：

1. **🔥 这个方向最需要的3项核心技能** — 每项说明怎么学、推荐资源
2. **📚 推荐1个高含金量证书** — 是什么、备考周期、对求职帮助
3. **🌐 行业前沿趋势** — 最新动态、外企最看重什么人才
4. **🎯 本周行动计划** — 一个具体可执行的学习任务
5. **💬 面试必会英文表达** — 一个高频英文面试问题 + 参考回答

大白话+emoji，实用具体，350字以内。不要在内容中提及候选人的个人背景信息。"""

# ============================================================
#  Tavily 搜索 API
# ============================================================
def search_tavily(query, max_results=8):
    if not TAVILY_API_KEY:
        return []
    try:
        resp = requests.post("https://api.tavily.com/search",
                             json={"api_key": TAVILY_API_KEY,
                                   "query": query,
                                   "search_depth": "advanced",
                                   "max_results": max_results,
                                   "include_answer": False},
                             timeout=30)
        resp.raise_for_status()
        data = resp.json()
        results = []
        for r in data.get("results", []):
            results.append({
                "title": r.get("title", ""),
                "url": r.get("url", ""),
                "content": r.get("content", "")[:500],
            })
        return results
    except Exception as e:
        print(f"  ⚠️ Tavily搜索失败: {e}")
        return []

# ============================================================
#  DeepSeek API
# ============================================================
def call_deepseek(system_prompt, user_message):
    resp = requests.post(
        f"{DEEPSEEK_BASE_URL}/v1/chat/completions",
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {DEEPSEEK_API_KEY}"},
        json={"model": DEEPSEEK_MODEL, "max_tokens": 2000, "temperature": 0.7,
              "messages": [{"role": "system", "content": system_prompt},
                           {"role": "user", "content": user_message}]},
        timeout=120)
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
    job = JOB_SEARCHES[doy % len(JOB_SEARCHES)]

    greetings = [f"{GF_NAME}早安～元气满满！", f"{GF_NAME}今天开心搞钱鸭～", f"{GF_NAME}早！先看市场💪",
                 f"{GF_NAME}你好！日报来啦～", f"叮咚～{GF_NAME}的投资助手上线！",
                 f"{GF_NAME}早！知识就是力量💡", f"{GF_NAME}做最有钱的自己！"]

    title = f"{GF_NAME}你好 | {ds} 周{wd}"
    parts = [f"## {greetings[doy % len(greetings)]}\n",
             f"*{ds} 星期{wd} · 投资第{doy % len(LESSONS) + 1}课 · 求职第{doy % len(JOB_SEARCHES) + 1}期*\n",
             "---\n"]

    # ── 投资模块 ──
    invest_modules = [
        ("📊", "美股速览", PROMPT_US, f"分析{dq}美股。"),
        ("🇨🇳", "A股 & 基金", PROMPT_CN, f"分析{dq}A股基金。"),
        ("🌍", "国际大事", PROMPT_GEO, f"分析{dq}国际事件对金融影响。"),
        ("🌊", "资金面", PROMPT_MACRO, f"分析{dq}流动性。"),
    ]
    if ENABLE_BTC:
        invest_modules.append(("₿", "比特币", PROMPT_BTC, f"分析{dq}BTC。"))

    total = len(invest_modules) + 4

    for i, (icon, name, prompt, query) in enumerate(invest_modules, 1):
        print(f"{icon} [{i}/{total}] {name}...")
        try:
            r = call_deepseek(prompt, query)
            parts.append(f"### {icon} {name}\n\n{r}\n\n---\n")
        except Exception as e:
            print(f"  ⚠️ 失败: {e}")
            parts.append(f"### {icon} {name}\n\n> 数据获取中～\n\n---\n")

    # ── 投资课堂 ──
    idx = len(invest_modules) + 1
    print(f"📖 [{idx}/{total}] 课堂：{lesson['topic']}...")
    try:
        r = call_deepseek(get_lesson_prompt(lesson), f"今天是{dq}，结合市场来教。")
        parts.append(f"### 📖 投资课堂 · 第{doy % len(LESSONS) + 1}课\n\n**{lesson['topic']}**\n\n{r}\n\n---\n")
    except Exception as e:
        print(f"  ⚠️ 失败: {e}")

    # ── 英语角 ──
    idx += 1
    print(f"🌍 [{idx}/{total}] 英语趣闻...")
    try:
        r = call_deepseek(PROMPT_EN, f"Today is {bj.strftime('%B %d, %Y')}. Tell an interesting recent world story.")
        parts.append(f"### 🌍 今日趣闻 · Story Time\n\n{r}\n\n---\n")
    except Exception as e:
        print(f"  ⚠️ 失败: {e}")

    # ══════════════════════════════════════
    #  求职专区（Tavily 联网搜索 + DeepSeek 分析）
    # ══════════════════════════════════════
    parts.append("---\n\n# 💼 求职专区\n\n---\n")

    # 搜索真实岗位
    idx += 1
    print(f"🔍 [{idx}/{total}] 搜索岗位：{job['focus']}...")
    search_results = search_tavily(job["query"])

    if search_results:
        # 把搜索结果格式化给 DeepSeek 分析
        search_text = f"以下是从网上搜索到的关于「{job['focus']}」的最新招聘信息：\n\n"
        for j, sr in enumerate(search_results, 1):
            search_text += f"【结果{j}】\n标题：{sr['title']}\n链接：{sr['url']}\n内容：{sr['content']}\n\n"

        try:
            r = call_deepseek(JOB_SYSTEM_PROMPT, search_text)
            parts.append(f"### 🏢 今日岗位 · {job['focus']}\n\n{r}\n\n")

            # 附上所有搜索来源链接
            parts.append("**📎 信息来源：**\n\n")
            for sr in search_results:
                if sr['url']:
                    parts.append(f"- [{sr['title'][:40]}]({sr['url']})\n")
            parts.append("\n---\n")

        except Exception as e:
            print(f"  ⚠️ DeepSeek分析失败: {e}")
            # 退回显示原始搜索结果
            parts.append(f"### 🏢 今日岗位 · {job['focus']}\n\n")
            for sr in search_results:
                parts.append(f"- **{sr['title']}**\n  {sr['url']}\n\n")
            parts.append("---\n")
    else:
        print("  ⚠️ 搜索无结果，使用AI推荐")
        try:
            fallback_prompt = f"""你是外企猎头顾问。今天的推荐方向是「{job['focus']}」。
请推荐3-4个该方向真实存在的外企在中国的典型招聘岗位，要求本科、1-2年经验可申请，工作地点在中国。
每个岗位包含：公司名、岗位名、地点、职责、要求、预估薪资、申请建议。
最后附上这些公司的招聘官网链接。不要提及候选人个人背景。"""
            r = call_deepseek(fallback_prompt, f"推荐{job['focus']}方向的岗位。")
            parts.append(f"### 🏢 今日岗位 · {job['focus']}\n\n{r}\n\n---\n")
        except Exception as e:
            print(f"  ⚠️ 失败: {e}")

    # ── 技能成长指南 ──
    idx += 1
    print(f"🎯 [{idx}/{total}] 技能指南...")
    try:
        r = call_deepseek(SKILL_SYSTEM_PROMPT,
                          f"今天推荐的岗位方向是「{job['focus']}」，请给出技能学习建议。")
        parts.append(f"### 🎯 技能成长指南\n\n{r}\n\n---\n")
    except Exception as e:
        print(f"  ⚠️ 失败: {e}")

    parts.append(f"\n> ⚠️ 投资分析仅供参考 | 岗位信息来自网络搜索，请以官网为准\n>\n> 💕 {GF_NAME}今天也加油！你一定行的 ❤️\n")
    return title, "\n".join(parts)

# ============================================================
#  Server酱推送
# ============================================================
def send_serverchan(key, label, title, body):
    if not key:
        print(f"⏭️  {label}未配置，跳过"); return
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
    print(f"🌅 {GF_NAME}你好 — 每日投资 + 求职 全能版")
    print("=" * 50)
    if not DEEPSEEK_API_KEY:
        print("❌ 请设置 DEEPSEEK_API_KEY"); sys.exit(1)
    if not SERVERCHAN_KEY:
        print("❌ 请设置 SERVERCHAN_KEY"); sys.exit(1)
    if not TAVILY_API_KEY:
        print("⚠️ TAVILY_API_KEY 未设置，求职模块将使用AI推荐而非联网搜索")

    bj = datetime.now(timezone(timedelta(hours=8)))
    doy = bj.timetuple().tm_yday
    job = JOB_SEARCHES[doy % len(JOB_SEARCHES)]

    print(f"🤖 DeepSeek ({DEEPSEEK_MODEL})")
    print(f"🔍 Tavily: {'✅' if TAVILY_API_KEY else '❌'}")
    print(f"📖 投资课: {LESSONS[doy % len(LESSONS)]['topic']}")
    print(f"🏢 求职方向: {job['focus']}")
    print()

    title, body = generate_briefing()
    print(f"\n📝 早报 {len(body)} 字\n📤 推送中...\n")
    send_serverchan(SERVERCHAN_KEY, f"Server酱 → {GF_NAME}", title, body)
    print(f"\n🎉 完毕！")

if __name__ == "__main__":
    main()
