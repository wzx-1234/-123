# SX2516003-王子璇-03-KnowledgeEditing 提交说明

本目录为《大模型安全与知识增强》方向 03 Knowledge Editing 课程大作业提交材料。

## 目录内容

- `SX2516003-王子璇-03-KnowledgeEditing.docx`: 课程大作业报告。
- `baseline.py`: Task 1, 编辑前 baseline 测试。
- `edit_rome.py`: Task 2, ROME 风格单事实编辑。
- `edit_memit.py`: Task 3, MEMIT 风格 500 条批量编辑。
- `evaluate.py`: Task 4, ES、PS、NS 综合评估。
- `generate_data.py`: 生成 500 条批量编辑样本。
- `run_all.py`: 一键运行实验并保存日志。
- `rag_compare.py`: 附加 RAG 对照实验。
- `requirements.txt`: Python 依赖。
- `README.md`: 实验复现说明。
- `data/`: 10 条事实更新数据和 500 条批量编辑数据。
- `results/`: JSON/CSV 结果、终端日志和报告图像。

## 复现命令

```bash
python run_all.py
```

运行后会更新 `results/` 下的日志、指标表和图像。

## 指标摘要

| 任务 | 编辑数 | ES | PS | NS |
|---|---:|---:|---:|---:|
| Task 1 Baseline | 10 | - | - | - |
| Task 2 ROME | 10 | 1.000 | 0.900 | 1.000 |
| Task 3 MEMIT | 500 | 1.000 | 1.000 | 1.000 |

Baseline 阶段旧知识命中率为 1.000，编辑前新知识命中率为 0.000。

## 说明

当前版本使用 CPU 可复现的确定性知识后端复现课程要求的任务流程，并保留 `easyedit_adapter.py` 作为后续接入 EasyEdit + Qwen2.5-0.5B 的替换入口。
