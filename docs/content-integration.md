# 精选题目集成 v1

保留 `POST /api/plan/daily` 和 `scripts/add_daily_plan.py` 作为唯一每日计划合并实现。新接口复用它，不写 done、不重排旧计划、不把历史 records.list 当当前计划。

## 数据格式

UTF-8 JSON，最多 1 MiB、1–10 个不同整数题号。只接受下列顶层字段；批次 ID 仅字母数字、下划线和短横线，最长80字。内容摘要是排序键、无空白的 JSON UTF-8 SHA256，使用脚本生成，不手算。

```json
{
  "schemaVersion": 1,
  "batchId": "curated-2030-01-02",
  "day": "2030-01-02",
  "items": [{"id": 206, "sha256": "GENERATE_FROM_THE_LOCAL_SOURCE"}]
}
```

已有完整题内容摘要同时绑定 lesson JSON 与五语言参考文本（去首尾空白）。摘要不符返回409，不能静默使用变更后的教学。

新题条目改用 `{"id":90001,"candidate":{"rights":"original","lesson":{...},"solutions":{"csharp":"...","python":"...","java":"...","javascript":"...","typescript":"..."}}}`。lesson 遵循 content-spec，含 difficulty/topic/domain=`algorithm`/type=`algorithm_trace`、原题 permalink、原作者权利说明、至少3级提示、证明/复杂度/常错及真实例子。拒绝未知字段、HTML/entities、无效数组、缺语言和未装载的 trace。必须复用**语义一致**的已维护 trace；要写新 trace 的题按普通源码贡献流程处理，不上传可执行 trace。

代码作为文本保存和显示，导入/发布接口不执行代码、测试、shell、外部 URL 或传入路径。结构检查不能证明算法正确或版权许可；这正是新候选必须经过独立本地审阅的原因。

## 预检与暂存

```sh
python scripts/export_reference_batch.py --day 2030-01-02 --batch-id curated-2030-01-02 206 21 > batch.json
python scripts/import_batch.py batch.json
```

PowerShell 5 的 `>` 可能生成 UTF-16，请使用 PowerShell 7，或把输出按 UTF-8 保存。CLI 默认预检不写库、不入计划；也不把校验通过称为教学通过。

`POST /api/v1/content/import` 请求 `{"dryRun":true,"batch":{...}}`，dryRun 默认 true。200 返回批次 sha256/problemIds/pendingReview/status。`dryRun:false` 时，全是已完整且摘要吻合的题则返回 status=`planned` 与 planResult；包含新候选则整批 status=`pending_review`，保存在固定私有 `local/incoming/BATCH_ID.json`，这批中的任何题都不入计划。

```sh
python scripts/import_batch.py batch.json --apply --host YOUR_EXISTING_PRIVATE_IP --port 8791
```

接口默认 `LEARNING_CONTENT_IMPORT=0`，拒绝403。只有维护者本地明确启动 `LEARNING_CONTENT_IMPORT=1` 才启用；即使启用也仅接受 loopback 或与服务绑定 IP 相同的本机来源，其他 LAN 客户端403。仍须同源 JSON、X-Learning-Request:1、精确 Host/Origin，无 CORS、无长期凭据。当前正常服务不自动重启或启用此选项。使用既有 LAN 进程时，本机 CLI 的 --host 填同一地址。容器默认只读且关闭导入；不要通过打开网络/增加 token 绕过它。

同 batchId+相同内容可重试；同 batchId+不同内容409。按题号不覆盖现有教学或参考文件；新批次也不能绕过已有题冲突。每日计划继续按日期/题号去重，后来用户移除的题不会因同日重试被重新激活。预检和错误均不标记完成。

## 本地审阅后发布

复制 examples/content-intake/review.template.json 到 local/reviews/，实际完成权利、语义、独立 Oracle/逐帧、五语言和 UI 检查，记录报告路径/命令结果。将真实结果填入 checks，绑定预检 SHA256，保留 reviewer 和批准记录。传入候选的自称“已通过”不能作为审阅凭据；HTTP API 不接收 review 或 publish 参数。

```sh
python scripts/publish_reviewed_batch.py local/incoming/BATCH_ID.json --review-file local/reviews/BATCH_ID.json --expected-sha256 SHA256_FROM_PREFLIGHT
python scripts/import_batch.py local/incoming/BATCH_ID.json --apply --host YOUR_EXISTING_PRIVATE_IP
```

发布是维护者拥有文件系统权限的显式本地动作，不是公开 API。它只写固定的 content/problems/ID.json、solutions/五语言/ID.ext、catalog；拒绝路径和符号链接，保留备份并调用可信 build_content.py 生成 dist。它不运行传入代码，不伪造代码测试。构建失败回滚本次字节，不覆盖后来外部编辑；备份在 local/before-content-import-*。进程被强制杀死/机器断电时，先检查发布锁与备份，不自动重试覆盖；多文件发布不承诺跨断电原子性。

当前15题已维护；新题发布后须维护相应Oracle、语言、UI测试和题数断言，再按贡献流程构建/回归。示例 skill 位于 examples/content-intake/SKILL.md，供现有外部调度器调用，不创建系统定时任务，不更改 dot 自动化。首次仅建议先对已有完整题预检，确认选题质量与流程再引入候选。


完整的已有题示例：examples/content-intake/existing-batch.example.json。先运行 `python scripts/import_batch.py examples/content-intake/existing-batch.example.json`，它不会写入或规划示例日期。

若维护者决定启用本机上传：先用原终端 Ctrl+C 正常停止旧实例，再在 PowerShell 设置 `$env:LEARNING_CONTENT_IMPORT='1'` 并运行原 LAN 启动命令；macOS/Linux 可用 `LEARNING_CONTENT_IMPORT=1 sh ./start-learning.sh`。不要在旧服务仍健康时另起实例。该开关不创建凭据、不扩大网络权限，但启用后本机进程可调用暂存和计划接口。正常服务本批未重启，所以当前进程还未装载新增路由；源代码与隔离测试服务已支持它。恢复默认时停止该实例，清除此环境变量，再正常启动。新路由加载后关闭状态为403；未重新加载的旧进程可能返回404。
