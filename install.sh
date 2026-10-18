#!/usr/bin/env bash
set -euo pipefail

say() { printf '\n==> %s\n' "$*"; }
die() { printf '\n错误：%s\n' "$*" >&2; exit 1; }

usage() {
  cat <<'USAGE'
用法：./install.sh --target claude|codex|workbuddy [--target ...]

  claude     装到 ~/.claude/skills/civil-litigation（Claude Code）
  codex      装到 ~/.agents/skills/civil-litigation（Codex）
  workbuddy  装到 ~/.workbuddy/skills/civil-litigation（WorkBuddy）

已有同名 Skill 会先移到 skill-backups 目录备份，不会删除。
USAGE
}

targets=()
while [ "$#" -gt 0 ]; do
  case "$1" in
    --target)
      [ "$#" -ge 2 ] || die "--target 后缺少宿主名"
      targets+=("$2")
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      die "未知参数：$1"
      ;;
  esac
done

[ "${#targets[@]}" -gt 0 ] || { usage; die "请用 --target 明确选择装到哪里"; }

repo_dir="$(cd "$(dirname "$0")" && pwd)"
skill_source="$repo_dir/civil-litigation"
[ -f "$skill_source/SKILL.md" ] || die "找不到 Skill：$skill_source"

for target in "${targets[@]}"; do
  case "$target" in
    claude) dest="$HOME/.claude/skills/civil-litigation" ;;
    codex)  dest="$HOME/.agents/skills/civil-litigation" ;;
    workbuddy) dest="$HOME/.workbuddy/skills/civil-litigation" ;;
    *) die "不支持的宿主：$target（只支持 claude、codex、workbuddy）" ;;
  esac
  mkdir -p "$(dirname "$dest")"
  if [ -e "$dest" ] || [ -L "$dest" ]; then
    # 备份放到技能目录之外，免得宿主把旧版当成第二个同名技能加载
    backup_dir="$(dirname "$(dirname "$dest")")/skill-backups"
    mkdir -p "$backup_dir"
    backup="$backup_dir/civil-litigation-$(date +%Y%m%d-%H%M%S)"
    mv "$dest" "$backup"
    say "已有旧版，已备份到：$backup"
  fi
  cp -R "$skill_source" "$dest"
  say "已装好：$dest"
done

say "用法：在对话里说「/civil-litigation 质证」或「用质证编」点名某一编。"
say "要用证据卷脚本（举证编），另装依赖：python3 -m pip install -r \"$repo_dir/requirements.txt\""
