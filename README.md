# 民事诉讼技能包（civil-litigation）

Created By 徐潜川，个人网站：www.xuqianchuan.com

一个技能包，让 Agent 变身最靠谱的律师助理，专业准确地辅助律师处理民事诉讼每个环节。

*A skill for Claude Code, Codex, WorkBuddy, Kimi and other skill-capable agents that walks a Chinese litigation lawyer's AI agent through a civil case, from intake to appeal, in sixteen chapters.*

给中国诉讼律师用的 AI Agent 技能包：从收案、起诉、答辩，一路到质证、开庭、上诉，共十六编。律师点名哪一编，Agent 就按那一编的做法出活。

**它是通用的。** Claude Code、Codex、WorkBuddy、Kimi 都能用；技能包只是一个文件夹，里面是 Markdown 写的做法和几个 Python 脚本，其他支持 Skill（技能包）的 Agent 也能用。

**它不替律师做判断。** 全部产出都是工作底稿，提交法院、发给客户之前，必须由律师本人复核。

## 十六编

| 编 | 做什么 | 交付 |
|---|---|---|
| 收案 | 接案后出工作方案，准备委托材料清单，建案件目录 | 工作方案 .html、委托材料 .docx、README |
| 起诉 | 先定起诉策略，再写起诉状 | 起诉策略 .html、起诉状 .docx |
| 答辩 | 先定应诉策略（含管辖异议、反诉建议），再写答辩状 | 应诉策略 .html、答辩状 .docx |
| 焦点 | 和律师分轮讨论，定争议焦点与我方立场 | 争议焦点 .html |
| 检索 | 按焦点查现行法条与类案，审查时间效力 | 法律检索报告 .html |
| 举证 | 按要件体系分组，出证据目录与合并证据卷 | 证据目录 .docx、证据卷 .pdf |
| 搜证 | 上网穷尽检索公开证据，按证据价值分档 | 互联网检索报告 .html |
| 核证 | 给当事人出核实问卷，回收后对照证据 | 核证问卷 .docx、对照表 .md |
| 取证 | 把缺口变成存证公证、申请调查收集或书证提出命令、自行调取清单 | 取证清单 .md |
| 质证 | 按对方证据逐项写三性与证明目的意见 | 质证意见 .docx |
| 庭前 | 可离线搜索的开庭提纲，加按焦点写的代理意见 | 开庭提纲 .html、代理意见 .docx |
| 庭上 | 两个口令：「庭审速查」庭上只就现有材料即时作答，没有就说没有；「法条速查」先查数据库再答法条、案例、企业主体，一个会话说一次即持续有效 | 即时作答 |
| 庭后 | 给客户的庭审汇报，补充质证、补充代理意见 | 庭审汇报 .html、补充意见 .docx |
| 上诉 | 上诉状与详尽的内部上诉方案 | 上诉状 .docx、上诉方案 .html |
| 对方攻击 | 站在对方代理人位置拆文书，找致命弱点 | 对方攻击报告 .html |
| 法官冷读 | 扮演初次翻卷的法官，中立评估文书落地效果 | 法官冷读报告 .html |

另附两份通用规矩，各编都会用到：

- `references/起草与审查.md`：法条、案例、企业主体怎么核验；审查的三种模式；起草分寸。
- `references/Word排版.md`：提交法院文书的统一排版，配一个机械自检脚本。

## 安装

**最简单的办法：把下面这句话发给你的 Agent，让它自己装。** 它要能在你电脑上执行命令（Claude Code、Codex、WorkBuddy、Kimi 都可以）。

> 下载 https://github.com/christyxk-ship-it/chinese-civil-litigation-skill ，阅读 README 的「安装」一节，只安装到你自己的技能目录，装完告诉我装到了哪里。

下面是给 Agent 看的安装步骤，你也可以自己照着做。需要 macOS 或 Linux。

```bash
git clone https://github.com/christyxk-ship-it/chinese-civil-litigation-skill.git
cd chinese-civil-litigation-skill
./install.sh --target claude
```

`--target` 按你用的 Agent 选：

| Agent | 写 | 装到 |
|---|---|---|
| Claude Code | `claude` | `~/.claude/skills/civil-litigation` |
| Codex | `codex` | `~/.agents/skills/civil-litigation` |
| Kimi | `codex` | 同上：Kimi 也读这个目录，和 Codex 装一次就够 |
| WorkBuddy | `workbuddy` | `~/.workbuddy/skills/civil-litigation` |

几个都用，就写几次 `--target`。已有同名技能会先移到 `skill-backups` 目录备份，不会删除。

**其他 Agent**：把仓库里的 `civil-litigation/` 整个文件夹复制到该 Agent 的技能目录即可，文件夹名不要改。不支持技能包的 Agent，可以让它在用之前先读 `civil-litigation/SKILL.md`。

举证编的证据卷脚本还需要三个 Python 包，不用这个脚本可以不装：

```bash
python3 -m pip install -r requirements.txt
```

## 用法

**默认显式调用，不会自动加载。** 你只是聊到「证据」「开庭」「上诉」这些词，它不会自己跳出来；只有你点名，Agent 才会读它。这是有意的：诉讼工作要由律师决定什么时候用哪一编。

点名有两种方式，每次点一编。

### 方式一：斜杠命令

在对话框里打斜杠命令，后面跟编名，再接一句要做什么：

```text
/civil-litigation 质证 对方提交的证据在「对方证据」文件夹，按逐项三性写质证意见
/civil-litigation 庭前 下周三开庭，按已定的争议焦点出开庭提纲和代理意见
/civil-litigation 上诉 一审判决书已收到，先出上诉方案给我看
```

斜杠的写法是 `/civil-litigation`。

### 方式二：用自然语言点名

直接说「用 civil-litigation 的某某编」，并说清楚这次的材料和要求：

```text
用 civil-litigation 的核证编，按这份证据目录给客户出核实问卷
用 civil-litigation 的检索编查一下：借款合同约定的逾期利率上限，按现行司法解释怎么算
用 civil-litigation 的对方攻击编，站在被告代理人的角度拆一遍我写的起诉状
```

### 口令

有三个口令，说出口即可调用对应那一编：

- **庭审速查**（庭上编）：开庭时只就现有材料即时作答，材料里没有就说没有。
- **法条速查**（庭上编）：先查数据库再回答法条、案例、企业主体问题。一个会话说一次，之后持续有效；庭外也可以用。
- **核证回收**（核证编）：客户交回问卷后，逐条对照现有证据，标出矛盾，没答的列进下一轮问卷。

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
- 2026-10-15：开庭速查编扩为庭审助手编，新增「法条速查」一节；总则删去「迭代建议」。
- 2026-10-18：按一个二审案件实测后的整轮修订。开庭准备、庭审助手两编改名庭前、庭上，庭上速查包并入开庭提纲，庭前编新增代理意见产物；举证编改按要件体系分组，搜证、取证编改按证据价值分档并拆开调查收集与书证提出命令，质证编改写三性与证明目的，上诉编补程序违法，对方攻击编默认只读主文书；期限一节补诉讼费用与当庭指定期限；排版文件补标点国标、页码格式与例外说明。证据卷脚本四处修复：目录自动续页、照片按 EXIF 转正、旋转扫描页页码位置、只校验仿宋字体。安装脚本支持 WorkBuddy。
- 2026-10-20：搜证、质证编加「先与我方在卷证据逐项比对」，质证编加对账式与数字全量复核，搜证编来源评价只看证据价值与事实可信度；排版文件称谓区分合议庭与审判长。
- 2026-10-20：README 说明本技能包通用、加入 Kimi；安装改为可以把链接发给 Agent 自行安装；用法分斜杠命令与自然语言两种调用方式并举例。
