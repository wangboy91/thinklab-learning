# HTTP请求与响应规约（当前实现）

所有API同源，匿名单人LAN档案。客户端请求截止6秒，成功必须收到服务端确认；离线/冲突不得显示已保存。请求正文为JSON对象，写操作必须Content-Type: application/json、X-Learning-Request: 1，并通过精确Host/Origin检查；不提供泛化CORS。

## GET /api/progress

返回records（日历历史）、revisions（日字段版本）、plan（全局有序计划）、planRevisions（全局计划版本）、version（档案版本）。例如下列合成结构，不是用户真实数据：

```json
{"records":{"2030-1-1":{"list":[1],"done":[]}},"revisions":{"2030-1-1|1|planned":1},"plan":[1,20],"planRevisions":{"1":1,"20":1},"version":2}
```

当前计划必须使用plan顺序，不能把历史records.list当成当前全局计划。已理解计数按所有日期done的不同题号计算，不能与仅当天计数混用。

## POST /api/progress

```json
{"operations":[{"id":"unique-operation-id","day":"2030-1-1","problem":1,"field":"done","value":true,"revision":0}]}
```

field是done或planned。planned使用全局planRevisions，done使用该day/problem/field的revisions。事务比较版本；成功返回最新档案，重复操作id幂等。409返回error及snapshot，保留客户端待提交值，用户选择共享或本机版本后再提交，不整份覆盖。

## POST /api/import

用户点击后发送 {"records": ...}。只补服务端缺失字段，服务器已有值/删除优先，整包摘要去重。旧localStorage键和备份保留；不同origin不能自动读取另一地址的存储。成功返回档案。

## 路线

GET /api/routes返回公开路线数组（id/title/audience/scope/problemIds有序）。POST /api/plan/route请求：

```json
{"routeId":"thinking-basics","operationId":"unique-route-request"}
```

成功返回 {"snapshot": 档案, "result": {"routeId": 路线ID, "added": 新增题号, "already": 已有题号, "addedCount": 数量, "alreadyCount": 数量, "replayed": 布尔值}}。以服务器定义为准，不接受客户端任意题号列表替代路线。一个事务完成，重复/重叠去重，原计划顺序和完成状态保留。

## 状态与诊断

200为实际成功；400为支持处理的无效参数；403为Host/Origin/自定义头拒绝；404为非允许路由/文件；415为写请求非JSON；409为版本冲突；503为数据库忙/不可用，须保留待提交数据。/health返回不依赖JS的HTML，/api/health仅驻内存已知路由计数/状态/时间，无IP、UA或正文。静态/API响应no-store，JS/CSS使用正确MIME并nosniff。

内容源码、原件归档、SQL文件与日志不是静态资源；服务仅允许生成的dist文件名。学习代码展示不等于服务器执行用户代码。


## POST /api/plan/daily

请求 `{"day":"2026-10-14","problemIds":[206,21]}`。仅接受已有完整教学与五语言参考的题号，使用与其他写入相同的JSON、Origin及X-Learning-Request校验。

SQLite事务按规范化日期/题号去重并追加缺失题；已有有效计划项保持顺序与revision，所有done状态保持。返回 `{"snapshot":...,"result":{"day":...,"added":[],"already":[],"replayed":[]}}`，三个数组分别为新增、首次请求已在计划、当天已处理。重复请求不重新激活后来被用户移除的题，不增加version。新日期可重新安排已移除项。不会把加入计划标成已理解。客户端不要用历史records.list重建全局plan。

复用命令：`python scripts/add_daily_plan.py --host 192.168.0.200 --day 2026-10-14 206 21`。仅调用既有服务，不启动第二个进程；失败保持未确认，重试相同日期/题号安全。


## POST /api/v1/content/import（默认关闭）

完整 schemaVersion 1、CLI、审阅流程及限制见 [内容集成](content-integration.md)。请求 `{"dryRun":true,"batch":{"schemaVersion":1,"batchId":"example","day":"2030-1-2","items":[{"id":206,"sha256":"由export_reference_batch生成"}]}}`。

结构错误400、同批次或已有题内容冲突409、关闭/非本机403。预检不写入；新候选只能私有暂存为 pending_review，不能由HTTP发布或执行代码。只有全部题已完整且摘要吻合时，apply 复用 join_daily 返回 planned 与 planResult。计划和 done 语义不变。所有写操作同样检查JSON/Host/Origin/自定义头，重复JSON键与非对象正文返回400。
