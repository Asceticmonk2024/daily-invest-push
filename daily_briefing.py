#!/usr/bin/env python3
"""
💰 莎总你好 — 每日投资早报 + 外企求职 全能版
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
#  求职方向轮换（每天不同行业/方向，30天循环）
# ============================================================
JOB_ROTATIONS = [
    {"focus": "能源与电力行业外企", "companies": "施耐德电气、西门子能源、ABB、GE Vernova、伊顿电气、三菱电机", "roles": "电气工程师、项目工程师、技术销售工程师、售前/售后工程师"},
    {"focus": "新能源与清洁能源外企", "companies": "特斯拉、Vestas维斯塔斯、金风科技合资、隆基绿能合作企业、SMA Solar", "roles": "新能源项目经理、光伏/风电技术工程师、储能项目工程师、解决方案经理"},
    {"focus": "外企项目管理岗", "companies": "西门子、博世、霍尼韦尔、3M、强生、飞利浦、ABB", "roles": "项目经理PM、项目协调员、PMO专员、交付经理"},
    {"focus": "外企产品经理岗", "companies": "微软、苹果、谷歌、亚马逊、SAP、Oracle、Salesforce", "roles": "产品经理、产品运营、技术产品经理、解决方案产品经理"},
    {"focus": "工业自动化外企", "companies": "罗克韦尔自动化、欧姆龙、菲尼克斯电气、倍福Beckhoff、库卡KUKA", "roles": "自动化工程师、PLC工程师、工业4.0解决方案经理、技术支持工程师"},
    {"focus": "外企管培生/轮岗项目", "companies": "西门子、博世、壳牌、联合利华、宝洁、施耐德", "roles": "管培生、商业轮岗生、技术管培生、运营管培生"},
    {"focus": "汽车行业外企", "companies": "大众、宝马、奔驰、特斯拉、博世汽车、大陆集团Continental、采埃孚ZF", "roles": "电气系统工程师、项目经理、质量工程师、新能源汽车研发"},
    {"focus": "咨询与专业服务", "companies": "埃森哲、德勤、普华永道、安永、毕马威、麦肯锡、波士顿咨询", "roles": "管理咨询顾问、能源行业咨询师、数字化转型顾问、ESG咨询"},
    {"focus": "半导体与电子外企", "companies": "英特尔、德州仪器TI、英飞凌、恩智浦NXP、意法半导体ST、安森美", "roles": "应用工程师、FAE现场工程师、产品市场工程师、项目经理"},
    {"focus": "医疗器械外企", "companies": "美敦力、强生医疗、飞利浦医疗、西门子医疗、GE医疗、波士顿科学", "roles": "产品专员、注册专员、项目经理、市场专员、临床支持工程师"},
    {"focus": "外企销售与商务拓展", "companies": "施耐德、西门子、ABB、霍尼韦尔、3M、飞利浦", "roles": "大客户销售、行业销售经理、商务拓展BD、渠道经理"},
    {"focus": "数据与数字化转型岗", "companies": "微软、SAP、Siemens Digital、Oracle、IBM、Accenture", "roles": "数据分析师、数字化转型顾问、BI分析师、IT项目经理"},
    {"focus": "供应链与运营管理", "companies": "亚马逊、苹果、戴尔、施耐德、博世、西门子", "roles": "供应链管理、采购专员、运营经理、物流规划"},
    {"focus": "ESG与可持续发展", "companies": "施耐德电气、壳牌、BP、道达尔、联合利华、宜家", "roles": "ESG分析师、可持续发展专员、碳管理顾问、环境合规经理"},
    {"focus": "外企人力资源/行政", "companies": "各大外企均招HR", "roles": "HRBP、招聘专员、培训发展、行政主管、薪酬福利"},
    {"focus": "智能制造与工业互联网", "companies": "西门子MindSphere、PTC、达索系统、罗克韦尔、树根互联", "roles": "工业互联网工程师、数字孪生工程师、MES实施顾问、智能制造项目经理"},
    {"focus": "快消与零售外企", "companies": "宝洁、联合利华、欧莱雅、玛氏、雀巢、可口可乐", "roles": "品牌经理、市场专员、渠道管理、供应链、项目管理"},
    {"focus": "金融与投资外企", "companies": "高盛、摩根大通、汇丰、渣打、花旗、贝莱德", "roles": "分析师、风控、合规、运营、项目管理"},
    {"focus": "航空航天与国防外企", "companies": "空客、霍尼韦尔航空、Collins柯林斯、赛峰Safran", "roles": "系统工程师、电气设计工程师、项目经理、质量工程师"},
    {"focus": "检测认证行业外企", "companies": "SGS、TÜV莱茵、TÜV南德、BV必维、Intertek天祥", "roles": "电气安全工程师、项目工程师、审核员、技术专家"},
    {"focus": "互联网大厂（外企背景）", "companies": "微软中国、谷歌中国、亚马逊AWS、苹果中国、LinkedIn领英", "roles": "项目经理、产品经理、商务拓展、客户成功经理、技术方案架构师"},
    {"focus": "建筑工程与基础设施外企", "companies": "AECOM、奥雅纳Arup、WSP、雅各布斯Jacobs、柏诚Parsons", "roles": "电气设计工程师、项目经理、BIM工程师、可持续设计顾问"},
    {"focus": "物流与交通外企", "companies": "DHL、FedEx、马士基、UPS、嘉里大通", "roles": "运营管理、项目协调、物流规划、商务拓展"},
    {"focus": "化工与材料外企", "companies": "巴斯夫、陶氏、杜邦、3M、亨斯迈、科思创", "roles": "技术工程师、应用开发、项目管理、EHS安全管理"},
    {"focus": "电信与通信外企", "companies": "爱立信、诺基亚、高通、Keysight是德科技", "roles": "射频工程师、项目经理、解决方案销售、技术支持"},
    {"focus": "教育与培训行业", "companies": "培生Pearson、ETS、British Council、各外企培训部门", "roles": "培训师、课程设计、学习发展经理、教育产品经理"},
    {"focus": "外企市场营销", "companies": "各大外企市场部", "roles": "市场营销经理、数字营销、内容营销、品牌传播"},
    {"focus": "外企财务与审计", "companies": "四大、各大外企财务部", "roles": "财务分析师、审计、成本控制、FP&A"},
    {"focus": "创业公司与新兴外企", "companies": "各赛道头部初创、外资背景创业公司", "roles": "早期员工、业务拓展、产品经理、运营负责人"},
    {"focus": "远程/混合办公外企", "companies": "GitLab、Automattic、Shopify、各外企远程岗", "roles": "远程项目经理、远程产品经理、远程客户成功"},
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

def get_job_prompt(rotation):
    return f"""你是一位资深外企猎头顾问，今天为"莎总"推荐外企招聘机会。

**莎总的背景：**
- 2024年一本院校电气工程专业本科毕业
- 目前在南方电网工作，有1-2年工作经验
- 优势：电力/能源行业背景、工程思维、央企工作经验、执行力强
- 求职意向：外企，坐标中国（接受短期出差不接受常驻国外）
- 不限岗位方向，对项目管理、产品经理等方向也感兴趣

**今日推荐方向：{rotation['focus']}**
**重点关注公司：{rotation['companies']}**
**参考岗位类型：{rotation['roles']}**

请推荐 **3-4个具体岗位**，每个岗位必须包含：
1. 🏢 **公司名** + 岗位名称
2. 📍 **工作地点**（必须在中国）
3. 📋 **岗位职责**（3-4条核心职责）
4. ✅ **任职要求**（学历、专业、经验年限、技能、语言等，要详细）
5. 💰 **预估薪资范围**（根据市场行情估算）
6. 🎯 **莎总匹配度分析**（她的哪些优势匹配，哪些需要补强）
7. 💡 **申请建议**（简历怎么写、面试准备重点）

要求：
- 岗位必须是这些公司真实存在的典型招聘方向（基于你对这些公司的了解）
- 要贴合莎总的背景，学历和经验年限要合理（本科、1-2年经验）
- 不要推荐需要硕士或5年以上经验的岗位
- 薪资范围要合理，标明月薪或年薪
- 用emoji让内容清晰好看
- 每个岗位信息要完整详细"""

def get_skill_prompt(rotation):
    return f"""你是一位职业发展导师，根据今天推荐的岗位方向，为"莎总"制定学习建议。

**莎总背景：**2024年电气工程本科毕业，在南方电网工作1-2年，想跳槽到外企。
**今日岗位方向：{rotation['focus']}**
**涉及公司：{rotation['companies']}**
**岗位类型：{rotation['roles']}**

请提供：

1. **🔥 这个方向最需要的3项核心技能**
   - 每项技能说明为什么重要、怎么学、推荐什么资源（网课/书/认证）
   
2. **📚 推荐1个含金量高的证书/认证**
   - 是什么、考试难度、备考周期、对求职的帮助

3. **🌐 行业前沿趋势**
   - 这个方向最新的技术/商业趋势是什么
   - 外企最看重什么样的人才特质

4. **🎯 本周行动计划**
   - 给莎总一个具体的、可执行的本周学习任务（不要泛泛而谈）

5. **💬 面试必会的1个英文表达**
   - 给一个该方向面试高频英文问题 + 参考回答模板

要求：大白话+emoji，实用具体，350字以内。"""

# ============================================================
#  DeepSeek API
# ============================================================
def call_deepseek(system_prompt, user_message):
    resp = requests.post(
        f"{DEEPSEEK_BASE_URL}/v1/chat/completions",
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {DEEPSEEK_API_KEY}"},
        json={"model": DEEPSEEK_MODEL, "max_tokens": 2000, "temperature": 0.7,
              "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_message}]},
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
    rotation = JOB_ROTATIONS[doy % len(JOB_ROTATIONS)]

    greetings = [f"{GF_NAME}早安～元气满满！", f"{GF_NAME}今天开心搞钱鸭～", f"{GF_NAME}早！先看市场💪",
                 f"{GF_NAME}你好！日报来啦～", f"叮咚～{GF_NAME}的投资助手上线！",
                 f"{GF_NAME}早！知识就是力量💡", f"{GF_NAME}做最有钱的自己！"]

    title = f"{GF_NAME}你好 | {ds} 周{wd}"
    parts = [f"## {greetings[doy % len(greetings)]}\n",
             f"*{ds} 星期{wd} · 投资第{doy % len(LESSONS) + 1}课 · 求职第{doy % len(JOB_ROTATIONS) + 1}期*\n",
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

    total = len(invest_modules) + 4  # +课堂+英语角+岗位+技能

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
        parts.append(f"### 📖 莎总课堂 · 第{doy % len(LESSONS) + 1}课\n\n**{lesson['topic']}**\n\n{r}\n\n---\n")
    except Exception as e:
        print(f"  ⚠️ 失败: {e}")

    # ── 英语角 ──
    idx += 1
    print(f"🇬🇧 [{idx}/{total}] 英语角...")
    try:
        r = call_deepseek(PROMPT_EN, f"Today is {bj.strftime('%B %d, %Y')}. Create English Corner.")
        parts.append(f"### 🇬🇧 英语角\n\n{r}\n\n---\n")
    except Exception as e:
        print(f"  ⚠️ 失败: {e}")

    # ── 外企岗位推荐（新模块）──
    parts.append("---\n\n# 💼 求职专区\n\n---\n")
    idx += 1
    print(f"🏢 [{idx}/{total}] 外企岗位：{rotation['focus']}...")
    try:
        r = call_deepseek(get_job_prompt(rotation),
                          f"今天是{dq}，请推荐今日方向「{rotation['focus']}」的具体岗位。重点关注国内岗位，不接受常驻国外。")
        parts.append(f"### 🏢 今日岗位推荐 · {rotation['focus']}\n\n{r}\n\n---\n")
    except Exception as e:
        print(f"  ⚠️ 失败: {e}")
        parts.append(f"### 🏢 今日岗位推荐\n\n> 岗位信息获取中～\n\n---\n")

    # ── 技能成长指南（新模块）──
    idx += 1
    print(f"🎯 [{idx}/{total}] 技能指南...")
    try:
        r = call_deepseek(get_skill_prompt(rotation),
                          f"今天是{dq}，基于今天推荐的「{rotation['focus']}」方向，给莎总学习建议。")
        parts.append(f"### 🎯 今日技能成长指南\n\n{r}\n\n---\n")
    except Exception as e:
        print(f"  ⚠️ 失败: {e}")

    parts.append(f"\n> ⚠️ 投资分析仅供学习参考 | 岗位信息基于行业认知，请以官网为准\n>\n> 💕 {GF_NAME}今天也加油！你一定行的 ❤️\n")
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
    print(f"🌅 {GF_NAME}你好 — 每日投资早报 + 求职助手")
    print("=" * 50)
    if not DEEPSEEK_API_KEY:
        print("❌ 请设置 DEEPSEEK_API_KEY"); sys.exit(1)
    if not SERVERCHAN_KEY:
        print("❌ 请设置 SERVERCHAN_KEY"); sys.exit(1)

    bj = datetime.now(timezone(timedelta(hours=8)))
    doy = bj.timetuple().tm_yday
    rotation = JOB_ROTATIONS[doy % len(JOB_ROTATIONS)]

    print(f"🤖 DeepSeek ({DEEPSEEK_MODEL})")
    print(f"📖 投资课: {LESSONS[doy % len(LESSONS)]['topic']}")
    print(f"🏢 求职方向: {rotation['focus']}")
    print()

    title, body = generate_briefing()
    print(f"\n📝 早报 {len(body)} 字\n📤 推送中...\n")
    send_serverchan(SERVERCHAN_KEY, f"Server酱 → {GF_NAME}", title, body)
    print(f"\n🎉 完毕！")

if __name__ == "__main__":
    main()
