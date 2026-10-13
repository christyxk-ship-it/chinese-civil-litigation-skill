#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""docx 排版自检——机械核对 references/Word排版.md。

用法：
    python3 check_docx_format.py 文件.docx [文件2.docx ...]
    python3 check_docx_format.py --type 质证意见 文件.docx
    python3 check_docx_format.py --type 质证意见 --template 范本.docx
    python3 check_docx_format.py --修订稿 --author "××律师团队" 修订稿.docx

--type 质证意见|代理意见 时，另按 Word排版.md 第 10 节校验首部四行与落款。
--author 给出批注与修订的统一署名；不给时只要求全文署名一致。
--修订稿 时允许修订标记，改判每处都有署名且符合上条；缺作者即 FAIL。
不加则按交付稿判，任何修订标记即 FAIL。修订标记含插删、移动、格式与表格修订，查遍 word/ 下全部部件。
修订稿转交付前须再跑一次不带该开关的自检。
本脚本只判机械项；最终显示效果由律师在 Word 或 WPS 里打开核验。
"""
import argparse, re, sys, zipfile

PAGE_W, PAGE_H = 11906, 16838          # A4
MAR_TB, MAR_LR = 1440, 1797            # 上下 2.54cm / 左右 3.17cm
BODY_W = PAGE_W - MAR_LR * 2           # 8312 版心
BODY_SZ, TITLE_SZ = 28, 44             # 四号 / 二号
OK_EASTASIA = {"宋体", "仿宋_GB2312", "仿宋"}
CN_DIGITS = "〇一二三四五六七八九十"


def paras(xml):
    return re.findall(r"<w:p[ >].*?</w:p>", xml, re.S)


def text(p):
    # 只认 <w:t> 本身，不吞 <w:tab/>、<w:topLinePunct …/> 等 t 开头的标签
    return "".join(re.findall(r"<w:t(?:\s[^>/]*)?>(.*?)</w:t>", p, re.S)).strip()


def attr(p, tag, name):
    m = re.search(r"<w:%s [^>]*w:%s=\"([^\"]+)\"" % (tag, name), p)
    return m.group(1) if m else None


class Report:
    def __init__(self, path):
        self.path, self.rows, self.bad = path, [], 0

    def add(self, ok, item, detail=""):
        self.rows.append((ok, item, detail))
        if not ok:
            self.bad += 1

    def dump(self):
        print("=" * 72)
        print(self.path)
        print("=" * 72)
        for ok, item, detail in self.rows:
            print(f"  [{'PASS' if ok else 'FAIL'}] {item}" + (f" —— {detail}" if detail else ""))
        print(f"  小计：{len(self.rows)} 项，未通过 {self.bad} 项\n")
        return self.bad


PLACEHOLDER = re.compile(r"\{\{[^}]*\}\}")

# 修订标记（OOXML）：插删、移动、格式、表格与编号修订逐个判作者；
# 移动／自定义 XML 的 RangeEnd 与 tblGridChange 按规范本无作者，只计存在。
REV_AUTHORED = ("ins|del|moveFrom|moveTo|moveFromRangeStart|moveToRangeStart|rPrChange|pPrChange|"
                "sectPrChange|tblPrChange|tblPrExChange|trPrChange|tcPrChange|cellIns|cellDel|cellMerge|"
                "numberingChange|customXml(?:Ins|Del|MoveFrom|MoveTo)RangeStart")
REV_MARKER = "moveFromRangeEnd|moveToRangeEnd|tblGridChange|customXml(?:Ins|Del|MoveFrom|MoveTo)RangeEnd"
REV_TAG = re.compile(r"<w:(?:(%s)|%s)(?=[\s/>])([^>]*)>" % (REV_AUTHORED, REV_MARKER))


def revisions(z):
    """word/ 下全部部件（正文、页眉页脚、脚注尾注、样式等）的修订标记：[(部件, 应带作者, 作者或 None)]。"""
    out = []
    for n in sorted(z.namelist()):
        if n.startswith("word/") and n.endswith(".xml"):
            for m in REV_TAG.finditer(z.read(n).decode("utf8", "replace")):
                a = re.search(r"""w:author=(["'])(.*?)\1""", m.group(2))
                out.append((n[5:], bool(m.group(1)), a.group(2) if a else None))
    return out


def check(path, doctype=None, is_template=False, tracked=False, author=None):
    r = Report(path)
    try:
        z = zipfile.ZipFile(path)
        doc = z.read("word/document.xml").decode("utf8")
    except Exception as e:
        r.add(False, "文件可读", str(e))
        return r
    ps = paras(doc)
    bodies = [p for p in ps if text(p) and "<w:tbl" not in p]

    # 审查三模式的交付前三项：批注署名、修订标记、残留高亮

    def signed_ok(names):
        return names <= {author} if author else len(names) <= 1
    who = f"「{author}」" if author else "全文一致"
    names = set(z.namelist())
    if "word/comments.xml" in names:
        authors = set(re.findall(r'w:author="([^"]*)"',
                                 z.read("word/comments.xml").decode("utf8")))
        r.add(signed_ok(authors), f"批注署名{who}",
              "、".join(sorted(authors)) or "无批注")
    else:
        r.add(True, "批注署名", "无批注")
    revs = revisions(z)
    per_part = {}
    for part, _, _ in revs:
        per_part[part] = per_part.get(part, 0) + 1
    where = "（%s）" % "、".join(f"{p} {c} 处" for p, c in per_part.items()) if revs else ""
    if tracked:
        # 每个应带作者的标记都要有署名；缺 w:author 单独计数，不能因取不到作者而放行
        missing = sum(1 for _, need, a in revs if need and a is None)
        authors = sorted({a or "（空）" for _, need, a in revs if need and a is not None})
        detail = "；".join(filter(None, [f"缺作者 {missing} 处" if missing else "",
                                        "作者：" + "、".join(authors) if authors else ""])) + where
        r.add(not missing and signed_ok(set(authors)), f"修订标记署名{who}",
              detail or "无修订标记")
    else:
        r.add(not revs, "交付稿无修订标记",
              f"{len(revs)} 处修订标记{where}；修订模式的稿加 --修订稿 另判，转交付前先接受或拒绝全部修订")
    hl = len(re.findall(r"<w:highlight ", doc))
    r.add(hl == 0, "无残留高亮", f"{hl} 处高亮")

    # 2 页面
    sect = re.search(r"<w:sectPr.*?</w:sectPr>", doc, re.S)
    sect = sect.group(0) if sect else ""
    w, h = attr(sect, "pgSz", "w"), attr(sect, "pgSz", "h")
    r.add((w, h) == (str(PAGE_W), str(PAGE_H)), "第2节 纸张 A4", f"实为 {w}×{h}")
    mar = {k: attr(sect, "pgMar", k) for k in ("top", "bottom", "left", "right")}
    ok = (mar["top"] == mar["bottom"] == str(MAR_TB) and mar["left"] == mar["right"] == str(MAR_LR))
    r.add(ok, "第2节 页边距 1440/1797", str(mar))

    # 3 字体统一
    ea = set(re.findall(r'w:eastAsia="([^"]+)"', doc)) - {"en-US", "zh-CN", "zh-TW"}
    r.add(ea <= OK_EASTASIA and len(ea) <= 1, "第3节 中文字体统一且为宋体/仿宋", "、".join(sorted(ea)) or "未显式指定")
    lat = set(re.findall(r'w:ascii="([^"]+)"', doc))
    r.add(lat <= {"Times New Roman"}, "第3节 西文 Times New Roman", "、".join(sorted(lat)))

    # 5 正文字号与行距
    szs = [int(s) for s in re.findall(r'<w:sz w:val="(\d+)"/>', doc)]
    n_body = sum(1 for s in szs if s == BODY_SZ)
    r.add(n_body > 0, "第5节 正文四号（sz=28）", f"{n_body} 处")
    lines = re.findall(r'<w:spacing[^>]*w:line="(\d+)" w:lineRule="(\w+)"', doc)
    bad_line = [l for l in lines if l != ("360", "auto") and l != ("240", "auto")]
    r.add(not bad_line, "第5节 行距 1.5 倍（360 auto；表格 240 auto 除外）", f"异常 {len(bad_line)} 处：{sorted(set(bad_line))[:4]}")

    # 5 首行缩进必须相对单位
    n_rel = len(re.findall(r'w:firstLineChars="200"', doc))
    hard = re.findall(r"<w:ind[^>]*/>", doc)
    n_hard = sum(1 for i in hard if 'w:firstLine="' in i and "firstLineChars" not in i)
    r.add(n_hard == 0, "第5节 首行缩进用 firstLineChars，无写死 twips", f"相对 {n_rel} 处，写死 {n_hard} 处")

    # 4 标题
    titles = [p for p in ps if attr(p, "jc", "val") == "center" and f'<w:sz w:val="{TITLE_SZ}"/>' in p and text(p)]
    r.add(bool(titles), "第4节 文书标题二号加粗居中", text(titles[0]) if titles else "未找到二号居中段")
    if titles:
        r.add("<w:b/>" in titles[0], "第4节 标题加粗", "")
        r.add(" " not in text(titles[0]) and "　" not in text(titles[0]), "第4节 标题不加字间距", text(titles[0]))

    # 8 页脚域
    ftr = [n for n in z.namelist() if re.match(r"word/footer\d*\.xml", n)]
    fx = "".join(z.read(n).decode("utf8") for n in ftr)
    r.add("PAGE" in fx and "NUMPAGES" in fx, "第8节 页脚含 PAGE/NUMPAGES 域", f"{len(ftr)} 个页脚")

    # 表宽
    tw = [int(x) for x in re.findall(r'<w:tblW w:w="(\d+)" w:type="dxa"/>', doc)]
    over = [x for x in tw if x > BODY_W]
    r.add(not over, f"表格宽度 ≤ 版心 {BODY_W}", f"{len(tw)} 张表，超宽 {over}")

    # 标点：不得出现 ASCII 直角引号
    body_text = "".join(text(p) for p in ps)
    n_q = body_text.count('"') + body_text.count("'")
    r.add(n_q == 0, "正文无 ASCII 引号（须全角）", f"{n_q} 处")

    holes = PLACEHOLDER.findall(body_text)
    if is_template:
        r.add(True, "范本模式：占位符不计为错", f"{len(holes)} 处待填")
    else:
        r.add(not holes, "无遗留占位符{{…}}", f"{len(holes)} 处：{holes[:3]}")

    if doctype:
        r.add(len(ps) >= 4, "第10节 首部至少四段", f"共 {len(ps)} 段")
        if len(ps) >= 4:
            p1, p2, p3, p4 = ps[:4]
            r.add(attr(p1, "jc", "val") == "center" and '<w:sz w:val="21"/>' in p1,
                  "第10节 第1行案号居中五号", text(p1)[:40])
            r.add(attr(p2, "jc", "val") == "center" and '<w:sz w:val="21"/>' in p2,
                  "第10节 第2行当事人居中五号", text(p2)[:40])
            r.add(attr(p3, "jc", "val") == "center" and f'<w:sz w:val="{TITLE_SZ}"/>' in p3
                  and doctype in text(p3), f"第10节 第3行标题为「{doctype}」", text(p3)[:40])
            r.add('w:firstLineChars="0"' in p4 and text(p4).endswith("："),
                  "第10节 第4行称谓不缩进且以全角冒号收尾", text(p4)[:20])
        cizhi = [i for i, p in enumerate(ps) if text(p) == "此致"]
        r.add(bool(cizhi), "第10节 落款含「此致」", "")
        if cizhi:
            i = cizhi[0]
            r.add(attr(ps[i], "spacing", "before") == "280", "第10节 「此致」段前 280",
                  str(attr(ps[i], "spacing", "before")))
            r.add('w:firstLineChars="200"' in ps[i], "第10节 「此致」缩进 2 字符", "")
            if i + 1 < len(ps):
                r.add(attr(ps[i + 1], "jc", "val") == "left", "第10节 受文机关顶格左对齐", text(ps[i + 1])[:30])
            tail = []
            for q in ps[i + 2:]:
                if not text(q):
                    continue
                if attr(q, "jc", "val") != "right":
                    break
                tail.append(q)
            r.add(bool(tail), "第10节 落款各行右对齐",
                  " / ".join(text(q)[:16] for q in tail) or "受文机关之后无右对齐段")
            if tail:
                last = text(tail[-1])
                if is_template and PLACEHOLDER.fullmatch(last):
                    r.add(True, "第10节 日期行（范本占位）", last[:24])
                else:
                    r.add(last.endswith("日") and any(c in CN_DIGITS for c in last),
                          "第10节 日期为中文数字", last[:24])
    return r


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="+")
    ap.add_argument("--type", dest="doctype", choices=["质证意见", "代理意见"], default=None)
    ap.add_argument("--template", action="store_true", help="范本模式：允许 {{…}} 占位符")
    ap.add_argument("--修订稿", dest="tracked", action="store_true",
                    help="审查修订模式的稿：允许修订标记，改判其署名")
    ap.add_argument("--author", default=None, help="批注与修订的统一署名，如「××律师团队」")
    a = ap.parse_args()
    bad = sum(check(f, a.doctype, a.template, a.tracked, a.author).dump() for f in a.files)
    print(f"合计未通过 {bad} 项。最终显示效果须在 Word 或 WPS 里打开核验。")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
