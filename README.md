# ThinkLab

中文技术学习工具：先独立思考，再看提示、真实状态推演和五语言参考。自由题库、预置路线、跨日期个人计划与单人局域网SQLite进度。

当前44道索引，**15道完整可学**：1、20、217、283、121、26、125、704、35、3、167、219、206、21、104。入门路线6题全部完整。其余明确为待完善，不表示用户已完成。AI应用与架构题型目前仅预留设计，尚无可学内容。

## 快速运行

已有Python3.11+标准库即可，无需安装依赖。在项目根目录：

```
python scripts/build_content.py
python server.py
```

默认127.0.0.1:8791。Windows局域网：`powershell -File .\start-learning.ps1 -ListenAddress <电脑LAN-IP> -Port 8791`。本机具体设置在忽略的local/start-lan.ps1。保持与既有地址同origin可继续读原浏览器记录；不要为换目录改网址或清空进度。

同LAN可访问设备均可读写同一份匿名档案，无多人身份隔离；不要将服务开放公网。无账号、收费、排名、个人信息采集或任意代码执行后台。五题是每日新增内容目标，不限制浏览或计划。

## 目录和维护

```
app/frontend/        界面、播放器与算法trace源码
app/backend/         HTTP与SQLite仓储
content/catalog.json 44题索引与来源链接
content/problems/    一题一份原创教学JSON（权威）
content/routes/      有序路线定义（权威）
solutions/<语言>/    一题一份参考代码（权威）
docs/                项目、架构、内容/发布规约、开源参考
tests/               算法、状态、语言、同步/路线/HTTP回归
scripts/             构建、测试与SQLite备份工具
dist/                可再生成的白名单网站文件，勿直接改正文/代码
local/               仅本机的原资料归档、报告、运行设置和测试产物
data/                仅本机的SQLite与一致性备份
```

server.py、storage.py、backup-progress.py、tests.cjs是少量过渡入口。补题改content/problems、solutions和必要trace源码，然后构建和验证；不再往app.js塞大段题库文字/代码。目录变更记录见本机local/CONTENT-BATCH-REPORT.md。

## 验证与备份

```
python scripts/run_checks.py
python scripts/backup_progress.py <目标备份文件>
python scripts/verify_live.py --host <电脑LAN-IP>
```

运行检查会使用已有Node、Python、C#、Java；TypeScript通过现有Node原生类型擦除运行，不代替tsc类型检查。不会安装SDK。真实手机、真实Chrome布局、模拟DOM和HTTP测试分别记录，不混称真机验收。

## 文档导航

- [内容规约](docs/content-spec.md)：完成态、动画语义、五语言、边界与去重
- [架构与API](docs/architecture.md)：目录、路由、SQLite和导入/冲突边界
- [请求/响应规约](docs/api-contract.md)：载荷、版本、幂等与失败状态
- [补题指南](docs/adding-problems.md)：权威源与构建/测试
- [开源学习项目参考](docs/open-source-learning.md)：链接、用途、许可与未集成状态
- [发布检查](docs/release-checklist.md) 与 [贡献指南](CONTRIBUTING.md)
- [内容权利](CONTENT-LICENSE.md) 与 [MIT](LICENSE)

GitHub：https://github.com/wangboy91/thinklab-learning 。MIT只覆盖本项目自有代码/自写教学，不覆盖第三方题干、教材或素材。历史原代码/文档在local/imports，仅本地归档，不公开。此批内容和目录修改尚未提交或推送。

## 一键启动、容器与外部精选导入

Windows 双击 `start-learning.cmd`；保留原 LAN 地址使用 `start-learning.cmd --host 192.168.0.200 --port 8791`。macOS/Linux 使用 `sh ./start-learning.sh`。依赖检查、构建、健康复用和端口冲突由同一个 Python 启动器处理。

容器配置见 [部署说明](docs/deployment.md)：默认仅本机端口，数据使用持久 named volume。现有 Docker Engine 未启动，本批没有运行容器构建/启动；其他系统仅静态检查。

[精选内容集成 v1](docs/content-integration.md) 提供预检、摘要/批次去重、私有候选暂存及明确本地审阅发布；HTTP 默认关闭且仅允许本机来源。五语言代码是数据，不在接口执行。复用每日计划 API，不创建系统定时任务或更改现有自动化。
