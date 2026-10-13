#!/usr/bin/env python3
"""隐私扫描：拦下不该进公开仓库的个人信息。

用法：
    python3 tools/privacy_scan.py                 # 只扫通用格式（CI 用）
    python3 tools/privacy_scan.py --words 词表.txt  # 另加维护者本机的私有词表（不入库）

通用格式：本机绝对路径、手机号、身份证号、邮箱、银行卡号、案号。
词表每行一个词；写成「词|文件名」表示该词只允许出现在那个文件里（如 NOTICE 的版权行）。
查到即退出码 1。
"""
import argparse
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SKIP_DIRS = {".git", "__pycache__", ".venv"}
SKIP_FILES = {"LICENSE"}  # Apache 协议原文
TEXT_EXT = {".md", ".py", ".sh", ".json", ".yaml", ".yml", ".txt", ""}

PATTERNS = {
    # 拆开写，免得本文件自己命中
    "本机绝对路径": re.compile(r"/" + r"Users/[^/\s]+|/" + r"home/[^/\s]+|[A-Za-z]:\\" + r"Users\\"),
    "手机号": re.compile(r"(?<!\d)1[3-9]\d{9}(?!\d)"),
    "身份证号": re.compile(r"(?<!\d)\d{17}[\dXx](?![\dXx])"),
    "邮箱": re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+"),
    "银行卡号": re.compile(r"(?<!\d)\d{16,19}(?!\d)"),
    "案号": re.compile(r"[（(]\s*(19|20)\d{2}\s*[）)][^\s，。、；]{1,12}?号"),
}


def files():
    for p in sorted(ROOT.rglob("*")):
        if p.is_file() and not SKIP_DIRS & set(p.relative_to(ROOT).parts) \
                and p.name not in SKIP_FILES and p.suffix in TEXT_EXT:
            yield p


def load_words(path):
    words = []
    for line in pathlib.Path(path).read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            word, _, allow = line.partition("|")
            words.append((word, allow or None))
    return words


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--words", help="私有词表路径（放在仓库外）")
    a = ap.parse_args()
    words = load_words(a.words) if a.words else []
    hits = 0
    for p in files():
        rel = p.relative_to(ROOT).as_posix()
        for n, line in enumerate(p.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            found = [k for k, rx in PATTERNS.items() if rx.search(line)]
            found += [f"私有词「{w}」" for w, allow in words if w in line and allow != rel]
            for f in found:
                hits += 1
                print(f"{rel}:{n}: {f}")
    print(f"扫描完毕，命中 {hits} 处。" if hits else "扫描完毕，未发现个人信息。")
    sys.exit(1 if hits else 0)


if __name__ == "__main__":
    main()
