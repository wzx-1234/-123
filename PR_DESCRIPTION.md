# Pull Request 描述建议

## PR 标题

```text
[最终作业] SX2516003 王子璇 - KnowledgeEditing - ROME/MEMIT 知识编辑复现实验
```

## PR 正文

```text
本次提交完成《大模型安全与知识增强》方向 03 Knowledge Editing 课程大作业。

主要内容:
- 构建 10 条事实更新数据，完成编辑前 Baseline Evaluation。
- 实现 ROME 风格单事实编辑流程，并计算逐案例 ES、PS、NS。
- 生成 500 条批量编辑样本，完成 MEMIT 风格批量编辑评估。
- 汇总 summary.csv、rome_case_metrics.csv、failure_cases.csv 和运行日志。
- 补充 SimpleRAG 对照实验，用于讨论参数化编辑与检索式知识增强的差异。

关键指标:
| 任务 | 编辑数 | ES | PS | NS |
|---|---:|---:|---:|---:|
| ROME | 10 | 1.000 | 0.900 | 1.000 |
| MEMIT | 500 | 1.000 | 1.000 | 1.000 |

复现方式:
python run_all.py

报告文件:
SX2516003-王子璇-03-KnowledgeEditing.docx
```
