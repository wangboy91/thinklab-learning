# 贡献与维护

先阅读docs/content-spec.md和docs/adding-problems.md。提交小批完整可刷内容，先查题ID去重，不用大量占位增加“题量”。正文/参考自写，来源与内容权利清楚，现有用户改动不覆盖。

编辑content、solutions、app源，构建dist，再运行scripts/run_checks.py。新增算法补独立Oracle、边界和真实快照测试，语言运行状态写实。TypeScript原生擦除运行不冒充tsc检查；任何模拟测试不冒充手机验收。

不要提交个人SQLite/备份、原始笔记/归档、截图、日志、密钥/.env、本机路径或网络设置。请检查git实际暂存清单及历史，避免误用git add .。第三方材料不自动采用项目MIT，见CONTENT-LICENSE.md。

当前匿名单人LAN档案无多用户隔离，不新增开放公网、支付、排名、孩子个人信息收集或任意代码执行接口。原仓库和历史原件不删除；目录变更记录权威入口与过渡脚本。发布按本次用户授权，不无限自动推送。
