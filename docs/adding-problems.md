# 补题实际入口

1. 查content/catalog.json与content/problems/NNNN.json，区分收录和完整，不覆盖已有用户改动。
2. 新建/补齐一题JSON，按content-spec字段写原创教学、例子和来源。
3. solutions/csharp|python|java|javascript|typescript下放NNNN对应参考；每份独立Solution/函数，勿直接拼多题class同名。
4. 新算法在app/frontend/algorithms-extra.js注册trace与真实状态渲染；复用已有模板也要用该题数据核验语义。两数之和/括号原trace保留。
5. 更新catalog元数据和content/routes/routes.json；完整数由真正的LESSONS集合算，不手工伪标。
6. 扩展tests/test_content.cjs独立Oracle、边界/反例与语言runner；然后运行python scripts/build_content.py与python scripts/run_checks.py。
7. 如修改后端白名单，先SQLite一致性备份，只重启本服务；运行scripts/verify_live.py。数据目录不迁出，不换既有origin。
8. 记录content/batches批次清单及local测试报告。检查实际Git跟踪/待发布文件与权利后，按本次明确授权决定是否提交/推送，不能把日增任务当无限自动发布授权。

dist是生成物，非权威正文/代码入口；禁止重新用旧task目录的导入脚本覆盖项目。历史原件及hash索引位于忽略的local/imports，各来源完整保留，重复字节复用路径，不自动公开。
