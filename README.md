# 民事诉讼技能包（civil-litigation）

*A Claude Code / Codex / WorkBuddy skill that walks a Chinese litigation lawyer's AI agent through a civil case, from intake to appeal, in sixteen chapters.*

给中国诉讼律师用的 AI Agent 技能包：从收案、起诉、答辩，一路到质证、开庭、上诉，共十六编。律师点名哪一编，Agent 就按那一编的做法出活。

**它不替律师做判断。** 全部产出都是工作底稿，提交法院、发给客户之前，必须由律师本人复核。

## 十六编

| 编 | 做什么 | 交付 |
|---|---|---|
| 收案 | 接案后出工作方案，准备委托材料清单，建案件目录 | 工作方案 .html、委托材料 .docx、README |
| 起诉 | 先定起诉策略，再写起诉状 | 起诉策略 .html、起诉状 .docx |
| 答辩 | 先定应诉策略（含管辖异议、反诉建议），再写答辩状 | 应诉策略 .html、答辩状 .docx |
| 焦点 | 和律师分轮讨论，定争议焦点与我方立场 | 争议焦点 .html |
| 检索 | 按焦点查现行法条与类案，审查时间效力 | 法律检索报告 .html |
| 举证 | 按抗辩体系分组，出证据目录与合并证据卷 | 证据目录 .docx、证据卷 .pdf |
| 搜证 | 上网穷尽检索公开证据 | 互联网检索报告 .html |
| 取证 | 把缺口变成公证保全、申请调查、自行调取清单 | 取证清单 .md |
| 核证 | 给当事人出核实问卷，回收后对照证据 | 核证问卷 .docx、对照表 .md |
| 质证 | 按对方证据逐项写四性意见 | 质证意见 .docx |
| 开庭准备 | 开庭提纲与可离线搜索的庭上速查包 | 开庭提纲、庭上速查包 .html |
| 开庭速查 | 庭上只就现有材料即时作答，没有就说没有 | 即时作答 |
| 庭后 | 给客户的庭审汇报，补充质证、补充代理意见 | 庭审汇报 .html、补充意见 .docx |
| 上诉 | 上诉状与详尽的内部上诉方案 | 上诉状 .docx、上诉方案 .html |
| 对方攻击 | 站在对方代理人位置拆文书，找致命弱点 | 对方攻击报告 .html |
| 法官冷读 | 扮演初次翻卷的法官，中立评估文书落地效果 | 法官冷读报告 .html |

另附两份通用规矩，各编都会用到：

- `references/起草与审查.md`：法条、案例、企业主体怎么核验；审查的三种模式；起草分寸。
- `references/Word排版.md`：提交法院文书的统一排版，配一个机械自检脚本。

## 安装

需要 macOS 或 Linux，以及 [Claude Code](https://claude.com/claude-code)、Codex 或 WorkBuddy。

```bash
git clone https://github.com/christyxk-ship-it/chinese-civil-litigation-skill.git
cd chinese-civil-litigation-skill
./install.sh --target claude
```

用 Codex 的把 `claude` 换成 `codex`；两个都用，就写两次 `--target`。已有同名技能会先移到 `skill-backups` 目录备份，不会删除。

用 WorkBuddy 的，把仓库里的 `civil-litigation` 目录整个放进 `~/.workbuddy/skills/`：

```bash
cp -R civil-litigation ~/.workbuddy/skills/
```

也可以把本仓库链接直接发给你的 Agent，让它自己装。

举证编的证据卷脚本还需要三个 Python 包，不用这个脚本可以不装：

```bash
python3 -m pip install -r requirements.txt
```

## 用法

在对话里点名某一编：

```text
/civil-litigation 质证
用核证编给客户出问卷
```

本技能包**只在点名时加载**。你只是聊到「证据」「开庭」这些词，它不会自己跳出来。

## 要你自己准备的

- **文书范本**：本包暂不附范本。质证意见、代理意见、起诉状等，用你自己或律所的范本；没有的，按 `Word排版.md` 从空白文档排。
- **法律数据库**：核验法条、案例与企业主体，建议用北大法宝、华宇元典、启信慧眼、天眼查，也可以用其他数据库。没有接入数据库的，Agent 会把查不到的内容标「待核验」，不会凭记忆编条号。

## 在路上

- 起诉状、答辩状的范本
- 收案编工作方案的标准骨架

## 免责声明

本项目是律师工作流程的辅助工具，不构成法律意见，也不建立律师与委托人关系。AI 生成的内容可能有错，引用的法条、案例和事实须由执业律师独立核验。使用者自行承担使用后果。

## 致谢

- 对方攻击、法官冷读两编改编自 Larissa Meredith-Flister 的 [opposing-counsel-review 与 judicial-first-impression](https://github.com/lawvable/awesome-legal-skills)（Apache-2.0），并参考了 [matematicsolutions](https://github.com/matematicsolutions/awesome-matematic-skills-en) 的英文改写版。
- 焦点编的分轮讨论法借鉴 Matt Pocock 的 [grilling](https://github.com/mattpocock/skills)，核证编的问卷写法借鉴其 to-questionnaire。

## 许可

Apache License 2.0，见 [LICENSE](LICENSE) 与 [NOTICE](NOTICE)。

## 进展日志

- 2026-10-13：首次公开发布，十六编。
- 2026-10-15：依赖下限升级到 pypdf 6.20、reportlab 5.0、pillow 12.3，证据卷脚本实测可用。
