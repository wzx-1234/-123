# 知识编辑实验复现包

本目录对应课程方向 03 Knowledge Editing。默认代码使用轻量确定性后端复现 baseline、单事实编辑、批量编辑和 ES/PS/NS 评估流程。该后端便于在无 GPU 环境下完成流程验证、报告撰写和提交材料整理。实验结果、运行日志、CSV 表格和图像均可由 `run_all.py` 重新生成，完整 Word 报告由上一级目录的 `optimize_reports.py` 生成。后续如使用 Qwen2.5-0.5B 与 EasyEdit，可保留数据、指标和报告结构，仅替换模型编辑后端。

## 文件说明

- `data/fact_updates_10.jsonl`: 10 条事实更新数据。
- `generate_data.py`: 生成 500 条批量编辑数据。
- `baseline.py`: Task 1, 评估编辑前模型是否返回旧知识。
- `edit_rome.py`: Task 2, 逐条重置并执行 ROME 风格单事实编辑。
- `edit_memit.py`: Task 3, 执行 MEMIT 风格 500 条批量编辑。
- `evaluate.py`: Task 4, 汇总 ES、PS、NS、耗时和内存，并生成图像。
- `rag_compare.py`: 附加实验，构建轻量 RAG 对照，比较参数化编辑与检索式知识增强的工程差异。
- `run_all.py`: 一键运行四个任务，保存真实 stdout/stderr 日志和外层耗时。
- `easyedit_adapter.py`: 真实 EasyEdit 后端替换入口说明。
- `build_report_docx.py`: 早期 Word 报告生成脚本，最终版报告使用上一级目录的 `optimize_reports.py`。
- `report.md`: 实验报告。
- `知识编辑课程大作业报告.docx`: 课程大作业 Word 报告。
- `知识编辑实验报告.docx`: 同步保留的兼容命名版本。
- `results/`: 运行结果、指标表和生成图像。

## 运行方式

```bash
python baseline.py
python edit_rome.py
python edit_memit.py
python evaluate.py
python rag_compare.py
cd ..
python optimize_reports.py
```

运行后会生成:

- `results/baseline_results.json`
- `results/rome_results.json`
- `results/memit_results.json`
- `results/summary.csv`
- `results/rome_case_metrics.csv`
- `results/failure_cases.csv`
- `results/rag_compare.csv`
- `results/run_logs/*.txt`
- `results/figures/*.svg`
- `results/figures/*.png`
- `知识编辑课程大作业报告.docx`
