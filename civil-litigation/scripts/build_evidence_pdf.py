#!/usr/bin/env python3
"""证据卷合并 PDF 生成器（civil-litigation 举证编）

依赖：pip install pypdf reportlab pillow

用法：python3 build_evidence_pdf.py config.json

配置（JSON，示例见同目录 config.example.json）：
{
  "output": "输出 PDF 绝对路径",
  "tmp_dir": "页码映射等中间产物目录",
  "fonts": {"fangsong": "仿宋 ttf/ttc 路径", "songti": "宋体 ttf/ttc 路径"},   // 可省，省略时按 FONT_CANDIDATES 依次找
  "cover": {
    "title": "被告《XX》证据",
    "lines": ["案件名第一行", "案件名第二行", "案号：【待定】", "",
              "提交人：……", "委托诉讼代理人：……", "二〇二六年十月【】日"]
  },
  "items": [
    {"num": "1", "name": "证据名称（与目录docx一致）",      "pdfs": ["内容PDF路径", ...], "images": [["图片路径", "图下说明或null"], ...]}
  ]
}

结构：封面(1页) + 目录页(1页) + 每项[分隔页 + 内容页]，全卷连续页码「第 X 页，共 Y 页」底部居中。
页码映射写 tmp_dir/page_map.json（{"total": N, "map": {"1": [起,止], ...}}），供证据目录 docx 页码列回填。
特殊排版页（数据对照表等）：先自行生成单页 PDF（宋体，与仿宋标示区分），再列入该项 pdfs。
"""

import json
import os
import sys
from io import BytesIO

from PIL import Image
from pypdf import PdfReader, PdfWriter
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph, Table, TableStyle
from reportlab.lib.styles import ParagraphStyle

# 省略 fonts 时依次找：WPS 自带 → Windows → macOS 系统宋体（ttc 子字体序号）。
# macOS 系统「华文仿宋」在部分版本上只有少量字形，不列入。
FONT_CANDIDATES = {
    "fangsong": [
        ("/Applications/wpsoffice.app/Contents/Resources/office6/fonts/FangS-SC.ttf", 0),
        ("C:/Windows/Fonts/simfang.ttf", 0),
        ("/System/Library/Fonts/Supplemental/Songti.ttc", 4),
    ],
    "songti": [
        ("/Applications/wpsoffice.app/Contents/Resources/office6/fonts/ShuS-SC.ttf", 0),
        ("C:/Windows/Fonts/simsun.ttc", 0),
        ("/System/Library/Fonts/Supplemental/Songti.ttc", 4),
    ],
}

PW, PH = A4  # 595.27 x 841.89


def load_config(path):
    with open(path, encoding="utf-8") as f:
        cfg = json.load(f)
    for k in ("output", "tmp_dir", "cover", "items"):
        if k not in cfg:
            sys.exit(f"配置缺少必填项: {k}")
    fonts = {}
    for kind, cands in FONT_CANDIDATES.items():
        given = cfg.get("fonts", {}).get(kind)
        if given:
            if not os.path.isfile(given):
                sys.exit(f"字体文件不存在（{kind}）: {given}")
            fonts[kind] = (given, 0)
            continue
        found = next(((p, i) for p, i in cands if os.path.isfile(p)), None)
        if not found:
            sys.exit(f"找不到可用的{'仿宋' if kind == 'fangsong' else '宋体'}字体。\n"
                     f"请在配置 fonts.{kind} 中给出本机可用的 ttf 路径")
        fonts[kind] = found
    return cfg, fonts


def prep_image(path, max_side=1600, quality=82):
    im = Image.open(path)
    if im.mode != "RGB":
        im = im.convert("RGB")
    w, h = im.size
    if max(w, h) > max_side:
        r = max_side / max(w, h)
        im = im.resize((round(w * r), round(h * r)), Image.LANCZOS)
    buf = BytesIO()
    im.save(buf, "JPEG", quality=quality)
    buf.seek(0)
    return buf, im.size


def image_page_pdf(path, caption=None):
    buf, (iw, ih) = prep_image(path)
    b = BytesIO()
    c = canvas.Canvas(b, pagesize=A4)
    margin = 1.6 * cm
    cap_h = 1.2 * cm if caption else 0
    maxw, maxh = PW - 2 * margin, PH - 2 * margin - cap_h
    r = min(maxw / iw, maxh / ih)
    w, h = iw * r, ih * r
    c.drawImage(ImageReader(buf), (PW - w) / 2, (PH - h) / 2 + cap_h / 2, w, h)
    if caption:
        c.setFont("FS", 9)
        c.drawCentredString(PW / 2, margin * 0.7, caption)
    c.showPage()
    c.save()
    b.seek(0)
    return b


def divider_pdf(num, name):
    # 分隔页只放证据编号与名称；来源说明不写上分隔页，来源信息在目录 docx 第三列首段
    b = BytesIO()
    c = canvas.Canvas(b, pagesize=A4)
    c.setFont("FS-B", 30)
    c.drawCentredString(PW / 2, PH - 6.5 * cm, f"证据{num}")
    c.setLineWidth(1)
    c.line(4 * cm, PH - 7.2 * cm, PW - 4 * cm, PH - 7.2 * cm)
    p = Paragraph(name, ParagraphStyle("n", fontName="FS-B", fontSize=15, leading=24, alignment=1))
    _, h = p.wrapOn(c, PW - 6 * cm, 12 * cm)
    p.drawOn(c, 3 * cm, PH - 8.2 * cm - h)
    c.showPage()
    c.save()
    b.seek(0)
    return b


def cover_pdf(title, lines):
    b = BytesIO()
    c = canvas.Canvas(b, pagesize=A4)
    c.setFont("FS-B", 26)
    c.drawCentredString(PW / 2, PH - 8 * cm, title)
    c.setFont("FS", 13)
    y = PH - 10.5 * cm
    for ln in lines:
        if ln:
            c.drawCentredString(PW / 2, y, ln)
        y -= 0.9 * cm
    c.showPage()
    c.save()
    b.seek(0)
    return b


def toc_pdf(items, page_map):
    b = BytesIO()
    c = canvas.Canvas(b, pagesize=A4)
    c.setFont("FS", 22)
    c.drawCentredString(PW / 2, PH - 3.5 * cm, "目　　录")
    left = ParagraphStyle("toc", fontName="FS", fontSize=12, leading=22)
    right = ParagraphStyle("tocr", fontName="FS", fontSize=12, leading=22, alignment=2)
    data = []
    for it in items:
        a, bb = page_map[it["num"]]
        pg = f"第{a}页" if a == bb else f"第{a}–{bb}页"
        data.append([Paragraph(f"证据{it['num']}　{it['name']}", left), Paragraph(pg, right)])
    tbl = Table(data, colWidths=[12.6 * cm, 3.0 * cm])
    tbl.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    _, h = tbl.wrapOn(c, 15.6 * cm, PH)
    tbl.drawOn(c, (PW - (12.6 + 3.0) * cm) / 2, PH - 5.2 * cm - h)
    c.showPage()
    c.save()
    b.seek(0)
    return b


def main(cfg_path):
    cfg, fonts = load_config(cfg_path)
    fs_path, fs_idx = fonts["fangsong"]
    print("仿宋字体:", fs_path)
    pdfmetrics.registerFont(TTFont("FS", fs_path, subfontIndex=fs_idx))
    pdfmetrics.registerFont(TTFont("FS-B", fs_path, subfontIndex=fs_idx))
    os.makedirs(cfg["tmp_dir"], exist_ok=True)

    # 第一遍：生成各项内容到缓冲（封面1页 + 目录1页，内容自第3页起）
    item_bufs = []
    for it in cfg["items"]:
        bufs = [divider_pdf(it["num"], it["name"])]
        for f in it.get("pdfs", []):
            if not os.path.isfile(f):
                sys.exit(f"内容 PDF 不存在: {f}")
            bufs.append(f)
        for entry in it.get("images", []):
            path, caption = entry[0], (entry[1] if len(entry) > 1 else None)
            if not os.path.isfile(path):
                sys.exit(f"图片不存在: {path}")
            bufs.append(image_page_pdf(path, caption))
        item_bufs.append((it["num"], bufs))

    page_map = {}
    cur = 2  # 第1页封面、第2页目录
    for num, bufs in item_bufs:
        start = cur + 1
        for b in bufs:
            cur += len(PdfReader(b).pages)
        page_map[num] = [start, cur]
    total = cur

    writer = PdfWriter()
    for src in [cover_pdf(cfg["cover"]["title"], cfg["cover"]["lines"]),
                toc_pdf(cfg["items"], page_map)]:
        for p in PdfReader(src).pages:
            writer.add_page(p)
    for _, bufs in item_bufs:
        for b in bufs:
            for p in PdfReader(b).pages:
                writer.add_page(p)

    # 连续页码 overlay
    final = PdfWriter()
    raw = BytesIO()
    writer.write(raw)
    raw.seek(0)
    for i, page in enumerate(PdfReader(raw).pages, start=1):
        ob = BytesIO()
        c = canvas.Canvas(ob, pagesize=(float(page.mediabox.width), float(page.mediabox.height)))
        c.setFont("FS", 9)
        c.drawCentredString(float(page.mediabox.width) / 2, 0.75 * cm, f"第 {i} 页，共 {total} 页")
        c.showPage()
        c.save()
        ob.seek(0)
        page.merge_page(PdfReader(ob).pages[0])
        final.add_page(page)

    with open(cfg["output"], "wb") as f:
        final.write(f)
    with open(os.path.join(cfg["tmp_dir"], "page_map.json"), "w", encoding="utf-8") as f:
        json.dump({"total": total, "map": page_map}, f, ensure_ascii=False, indent=1)

    print("saved:", cfg["output"])
    print("total pages:", total)
    for k, v in page_map.items():
        print(f"证据{k}: 第{v[0]}-{v[1]}页")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("用法: python3 build_evidence_pdf.py config.json")
    main(sys.argv[1])
