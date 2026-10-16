# 本地与容器部署

运行时只需 Python 3.11+ 标准库，不自动安装依赖。完整开发回归另需已有 Node、.NET、Java；TypeScript 原生擦除不是完整 tsc 检查。

## Windows

双击 `start-learning.cmd`：默认本机 `http://127.0.0.1:8791/`，错误留在窗口。已有健康服务直接返回，不构建、不启动第二个进程。关闭前台窗口或 Ctrl+C 停止此次启动的实例。

保留本机已有 LAN origin 时运行：

```powershell
.\start-learning.cmd --host 192.168.0.200 --port 8791
# 兼容原 PowerShell 参数：
powershell -File .\start-learning.ps1 -ListenAddress 192.168.0.200 -Port 8791
```

默认本机入口不会自动探测另一个 LAN origin。原服务只绑定 LAN IP 时，请传相同 `--host`；不要用不同地址创建第二份浏览器缓存。数据库始终默认 data/learning.sqlite3，换入口不换数据。

## macOS / Linux

```sh
sh ./start-learning.sh
# 如需已批准的局域网地址：
sh ./start-learning.sh --host YOUR_PRIVATE_IP --port 8791
```

脚本定位自身目录，Python 检查、构建和服务与 Windows 共用同一实现。健康复用、端口冲突和启动锁均有可见提示。`local/start.lock` 含前台启动器 PID；先核实该进程不存在，才手动清理崩溃遗留锁。脚本不自动停止其他进程。

## Docker Compose

需要已经运行的 Docker Engine / Docker Desktop。可先 `docker version` 与 `docker compose config` 检查。仓库不提供自动安装、管理员提权、防火墙或公网部署脚本。

```sh
docker compose --env-file deploy.env.example config
docker compose --env-file deploy.env.example up --build -d
docker compose ps
docker compose logs --tail=50
```

默认仅发布 `127.0.0.1:8791`。原生服务占用同一端口时不要同时启动；可在本地复制配置并改 THINKLAB_PORT，例如 18881。不同 origin 的浏览器旧记录不能自动读取。容器内监听 0.0.0.0 仅用于 Docker 转发，Host/Origin 仍按精确配置校验；不把容器通配绑定当作公网授权。

镜像以 UID/GID 10001 运行，根目录只读、去掉 capabilities，SQLite 仅写 named volume `thinklab-data:/state`。健康检查读取真实 SQLite 的 `/api/progress`。镜像只复制公开源码，排除 local/data/.git/凭据及已有 dist，构建时从 content/solutions 生成 dist。

容器卷初次是**新档案**，不会自动复制或替换本机 SQLite。停止原生服务并完成 `python scripts/backup_progress.py UNIQUE_BACKUP.sqlite3` 后，才由维护者自行选择把一致性备份复制到卷中；保留原数据库和全部旧备份。不要直接复制运行中的 SQLite 文件，也不要把个人数据放进镜像。`docker compose down` 保留 named volume；不要使用 `down -v`，除非明确要删除那份容器档案。

仅容器重建镜像不会丢卷数据。新增题经审阅发布后重新 build 镜像；默认容器不开放内容导入端点，也不允许在线修改只读源码。

## 配置与验收边界

`LEARNING_HOST`、`LEARNING_PORT`、`LEARNING_DB` 为原生服务配置。容器额外使用 `LEARNING_PUBLIC_HOST` 与 `LEARNING_PUBLIC_PORT` 匹配宿主机映射的精确 Host；仅在通配监听时接受私有网络 Docker 转发连接。默认仅本机发布，不修改网络权限。

本批 Windows 已实际运行启动器、健康复用、端口占用、临时数据库持久化和 HTTP 导入测试。macOS/Linux 无实际执行环境，shell 入口仅静态检查。Docker 客户端可用，但 desktop-linux Engine 管道不存在；未运行容器构建/启动，不宣称多平台已验收。首次拉取 Python 基础镜像需要部署者允许网络；本批未拉取镜像。

新内容集成参见 content-integration.md；它不创建任何系统任务或更改已有自动化。


容器中的现有完整题也可直接复用原每日计划脚本，不必开启内容上传：

```sh
docker compose exec thinklab python scripts/add_daily_plan.py --host 127.0.0.1 --day 2030-01-02 206 21
```

此命令操作的是容器 named volume 的档案；本批没有实际执行容器命令。原生 Windows 启动器使用已有 Python 的基础解释器启动标准库服务，避免虚拟环境重定向器留下子进程；不安装或切换系统运行时。
