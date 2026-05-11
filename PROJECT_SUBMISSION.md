# 课程大作业提交说明

## 选题登记建议

Issue 标题可写为:

```text
[选题登记] 学号 姓名 - Knowledge Editing - ROME/MEMIT 知识编辑复现实验
```

Issue 内容建议:

```text
选题方向: 03-KnowledgeEditing
项目题目: ROME/MEMIT 知识编辑复现实验
计划内容:
1. 构建 10 条事实更新数据，完成编辑前 baseline。
2. 实现 ROME 风格单事实编辑流程，逐条编辑并评估 ES/PS/NS。
3. 实现 MEMIT 风格 500 条批量编辑流程，记录耗时和内存。
4. 汇总逐案例指标、失败案例和运行日志。
5. 增加 SimpleRAG 附加对照，讨论参数化编辑与检索式知识增强的差异。
```

## PR 标题建议

```text
[作业03-KnowledgeEditing] 学号 姓名 - ROME/MEMIT 知识编辑复现实验
```

## PR 描述建议

```text
本次提交完成 Knowledge Editing 方向课程大作业。项目包含 10 条事实更新数据、500 条批量编辑数据生成脚本、baseline、ROME 风格单事实编辑、MEMIT 风格批量编辑和 ES/PS/NS 综合评估。
同时补充 SimpleRAG 附加对照，用于分析参数化编辑与非参数化知识增强在建库、查询延迟和可撤回性上的差异。

主要文件:
- data/fact_updates_10.jsonl
- baseline.py
- edit_rome.py
- edit_memit.py
- evaluate.py
- run_all.py
- rag_compare.py
- generate_assets.py
- build_report_docx.py
- 知识编辑课程大作业报告.docx

复现方式:
python run_all.py
python ..\optimize_reports.py

结果摘要:
- Baseline: old_knowledge_hit=1.000, pre_edit_new_target_hit=0.000
- ROME: ES=1.000, PS=0.900, NS=1.000
- MEMIT: ES=1.000, PS=1.000, NS=1.000

说明:
当前版本使用 CPU 可复现的确定性知识后端，保留 easyedit_adapter.py 作为 EasyEdit + Qwen2.5-0.5B 的替换入口。
```

## 建议提交文件

建议将整个 `实验` 文件夹作为课程大作业项目目录提交。若仓库要求放入特定子目录，可将该文件夹内容复制到对应路径。
