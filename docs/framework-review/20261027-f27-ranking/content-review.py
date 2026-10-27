#!/usr/bin/env python3
"""Author self-review with structural/evidence assertions, not independent review."""
import datetime,html,json,pathlib,re
R=pathlib.Path(__file__).resolve().parents[3];D=pathlib.Path(__file__).resolve().parent
P=R/"projects/travel-search";page=(R/"framework/f27.html").read_text()
text=re.sub(r"<pre\b[\s\S]*?</pre>","",page);text=re.sub(r"<[^>]+>","",text)
assert len(re.findall(r"[\u4e00-\u9fff]",text))==5304
for section in ["goal","lesson","drills","pitfalls","recap"]:assert f'<section class="{section}">' in page
assert page.count('<div class="callout warn">')==4
drills=page.split('<section class="drills">')[1].split("</section>")[0];assert drills.count("<details>")==8
assert len(re.findall(r'data-d2-light=',page))==2
assert not re.search(r'data-source="[^"]*(shell-|\.js")',page)
assert not (R/"framework/f28.html").exists()
for pre in re.finditer(r'<pre\b([^>]*)><code[^>]*>([\s\S]*?)</code></pre>',page):
    attrs,body=pre.groups();source=re.search(r'data-source="([^"]+)"',attrs)
    if not source:continue
    original=(R/source.group(1)).read_text().rstrip("\n").splitlines();ranges=re.search(r'data-lines="(\d+)-(\d+)"',attrs)
    if ranges:original=original[int(ranges.group(1))-1:int(ranges.group(2))]
    assert html.unescape(body)=="\n".join(original),source.group(1)
table=json.loads((P/"data/f27/stay-table.json").read_text())
assert len(table["hotels"])==8 and len(table["offers"])==19
assert sum(len(h["offers"]) for h in table["hotels"])==19
assert len({o["summary"]["offer_id"] for o in table["offers"]})==19
assert table["reference_time"]=="2026-10-27T08:00:00+08:00" and table["max_inventory_age_seconds"]==300
assert json.loads((P/"search/f27/relevance-price.json").read_text())==json.loads((P/"search/f27/relevance-preferred.json").read_text())
rounds=[]
for n in [1,2]:
    receipts={name:json.loads((P/f"review/f27/round{n}/{name}.json").read_text()) for name in ["prepare","hotels","rooms","boundary","errors"]}
    assert sum(receipts[name]["http_requests"] for name in ["prepare","hotels","rooms","boundary"])==27
    assert receipts["errors"]["http_requests"]==51
    assert json.loads((P/f"review/f27/round{n}-cleanup/cleanup.json").read_text())["http_requests"]==2
    rounds.append(dict(round=n,teaching_http=27,additional_http=51,initial_cleanup_http=2,
        receipts=f"projects/travel-search/review/f27/round{n}"))
checks=[
    ("业务与职责","F26最低价不能代替酒店意图；ES排酒店，Java逐晚核对并排酒店内房型，Pages教程与本机观察窗分开。","framework/f27.html#problem"),
    ("模型边界","本课一个根文档一酒店，nested只用于同报价条件；明确根total数酒店、更新根文档代价，未把F26报价计数搬来。","framework/f27.html#sample"),
    ("酒店主键","三种模式独立主键；track_scores不改显式sort；品质缺值_last/距离缺值Infinity、同值hotel_id稳定。","projects/travel-search/review/f27/round2/hotels.json"),
    ("两层相互关系","两组房型模式完整DSL相同；默认酒店最终次序相同，h01所选60000变80000但最低仍60000。","projects/travel-search/review/f27/round2/rooms.json"),
    ("偏好与硬条件","含早→可退→总价为显式词典序，不是通用最优；两个require在同nested中独立，默认不缩集合。","projects/travel-search/review/f27/round2/errors.json"),
    ("逐晚与时效","同offer/币种/日期，缺价不补0；固定上海参考时刻与300秒人为规则。Duration直接比较，不截断小数秒。","projects/travel-search/backend/src/main/java/dev/esweb/travel/HotelRankingService.java"),
    ("业务拒绝与资料异常","a05缺价/c01旧库存/c02缺晚/c03售罄逐条拒绝；根投影不等于固定表时整个请求502，两者区分。","projects/travel-search/review/f27/round2/errors.jsonl"),
    ("范围","完整与top2、根与inner两层完整性检查；107/100实际502先于未知source检查；组内>20不冒称注入。","framework/f27.html#coverage"),
    ("独立能力","运河新需求h07/g01、h08/i01，均65000分；同品质由hotel_id，g02不可退/i02 USD硬排除。","projects/travel-search/review/f27/round2/boundary.json"),
    ("输入与失败","本课DTO严格JSON布尔；10输入错误400，strict/重复/Bulk冲突、源错配与截断502恢复，连接503另由浏览器实际验证。","projects/travel-search/review/f27/round2/errors.json"),
    ("可复现与片段","本课独立19227/tut-f27-hotels，固定schema/数据/refresh；JSON/Java片段逐字来自工程，关键查询/资格/投影/错误可见。","framework/f27.html"),
    ("因果与练习","图源/正文/表格/8练习答案/4陷阱/速记使用同ID、金额和规则，next只引出F28，未提前实施。","framework/diagrams/f27")
]
r=dict(at=datetime.datetime.now(datetime.timezone.utc).isoformat(),status="passed",reviewer="root author self-review",
    independent_review=False,reasoning_runtime="See reasoning.json; requested model/effort cannot be set or read back here.",
    chinese_chars_outside_code=5304,cases=3,teaching_http=27,diagrams=2,players=0,drills=8,pitfalls=4,
    rounds=rounds,checks=[dict(topic=a,finding=b,evidence=c) for a,b,c in checks],
    limitations=["No global quality claim; fixed synthetic signal and tiny presegmented corpus.",
        "No production quote/booking, multi-node, performance or concurrent snapshot protocol.",
        "Future inventory timestamps, exactly 300 seconds, MIN_STAY, inner group >20, timeouts/partial shard failure not separately injected.",
        "Browser, visual, build, diagram and ES receipts are separate evidence categories."])
(D/"content-review.json").write_text(json.dumps(r,ensure_ascii=False,indent=2)+"\n")
print("F27 author content self-review passed; independent review not claimed")
