# 当前架构与数据边界

现有栈仍是原生HTML/CSS/JS＋Python标准库HTTP＋SQLite，没有更换框架或加入平台后台。

## 源与构建

app/frontend是UI和trace源码；每题正文在content/problems/NNNN.json，五语言代码在solutions；catalog和routes单独维护。scripts/build_content.py只读取这些公开源，检查唯一ID、必填字段、五语言文件与路线ID，再生成dist的content.js、lessons.js、codes.js、routes.js并复制前端文件。生成输出不得逃出项目目录。local/imports与data从不参与构建。

## 类型与路由

当前真实支持algorithm_trace：数组/集合、原串双指针、读写覆盖补零、闭区间二分、股价时序最低记录、唯一前缀压缩和原有栈/哈希播放器。动画存不可变快照，可暂停、前后单步和重播。页面hash #/problem/<id>，路线 #/route/<route-id>。

ai_pipeline未来用于案例/实验/评价，system_design未来用于约束/权衡/设计图；目前只是可扩展内容设计，没有对应题库或完整渲染器，不得把这些声明当成功能已完成。

## HTTP

GET /api/progress读共享档案；POST同路径提交字段revision/操作id，过期409并整批回滚。POST /api/import由用户点击后追加旧浏览器记录，服务器已有值（含删除）优先。GET /api/routes读公开有序路线；POST /api/plan/route用事务将整条路线加入全局有序计划，重复/重叠去重，保留完成历史。/health为无JS连接页，/api/health只有驻内存已知路由计数，不存IP/UA/正文。

静态服务只允许dist明确文件名，不提供任意目录、源目录、DB或原件。Host/Origin精确检查、JSON＋自定义头、无泛化CORS。SQL均参数化。客户端请求6秒截止；SQLite busy_timeout1.5秒，锁失败503，界面明确未保存。

## SQLite与迁移

data/learning.sqlite3只放服务电脑本地磁盘，多端访问HTTP而非共享盘开DB。progress按日期保留字段历史；plan_items是跨日期有序计划，有全局revision和删除标记；一次性plan_migrated标记迁移旧计划。imports和operations保证导入/重试幂等，route_operations记录路线事务回执。短事务、foreign_keys开启、rollback journal；未来换数据库替换app/backend/storage.py仓储，当前尚未实现第二数据库。

备份必须SQLite backup接口，不在运行中仅复制.db。目录整理保留原data位置、端口/origin与localStorage键。资料原件只复制到local/imports，按hash复用相同字节并保留不同版本，不删除源文件，不纳入公共Git。
