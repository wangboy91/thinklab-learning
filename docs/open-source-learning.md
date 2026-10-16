# 开源学习项目参考与许可边界

核验记录日期：**2026-10-12**，来自此前父任务核验的一手仓库与许可文件。本批整理该记录，不表示重新安装、复制或获得第三方商业授权。当前ThinkLab没有依赖或集成以下项目。

| 项目与一手链接 | 已核验许可/未知 | 用途与本项目边界 |
| --- | --- | --- |
| [Algorithm Visualizer前端](https://github.com/algorithm-visualizer/algorithm-visualizer) | MIT | 借鉴算法事件与独立播放器分层；未整体搬入。独立algorithms仓未确认许可，不能套主仓MIT。 |
| [tracers.js](https://github.com/algorithm-visualizer/tracers.js) | MIT | [Commander.ts](https://github.com/algorithm-visualizer/tracers.js/blob/master/src/Commander.ts)存在条件外发行为，本项目不安装/运行，继续自主本地快照。 |
| [Hello Algo](https://github.com/krahets/hello-algo#license) | 文字、代码、图片、视频CC BY-NC-SA4.0 | 仅外链/教学思路参考，不复制教材或图，不将非商业材料混进MIT或未来商业版。 |
| [doocs/leetcode](https://github.com/doocs/leetcode/blob/main/LICENSE) | CC BY-SA4.0 | 借鉴一题多语言组织；不整库搬题干，原LeetCode第三方权利仍另核，改编会有署名/相同许可义务。 |
| [labuladong](https://github.com/labuladong/fucking-algorithm) | 根通用授权未确认 | 只链接，不推定代码/教材可公开复制或商业使用。 |
| [System Design Primer](https://github.com/donnemartin/system-design-primer/blob/master/LICENSE.txt) | CC BY4.0 | 未来逐文件署名改编候选；链接/第三方图不自动随主许可授权，当前不导入。 |
| [Datawhale llm-cookbook](https://github.com/datawhalechina/llm-cookbook) | CC BY-NC-SA4.0 | AI应用路线外链参考，未复制教程代码。 |
| [Datawhale hello-agents](https://github.com/datawhalechina/hello-agents) | CC BY-NC-SA4.0 | Agent案例外链参考；链接的HelloAgents框架亦有非商业边界，不预设已获商用权。 |

代码仓库许可不必等于题干、教材、图片或链接素材许可。将来复用须核对具体文件、版本、权利人和署名/再分发条件。来源未知保持外链，不用“开源”一词替代授权证据。

内容扩展设计：algorithm_trace是当前实现；ai_pipeline拟为案例/实验/评估；system_design拟为约束/权衡/设计图。后两类尚未实现可学题/渲染器，不列为已集成功能。
