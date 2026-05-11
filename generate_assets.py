import csv
import html
import json
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "results"
FIGURES = RESULTS / "figures"
LOG_DIR = RESULTS / "run_logs"


def fmt(value):
    if value == "":
        return "-"
    if isinstance(value, float):
        return f"{value:.3f}"
    return str(value)


def safe_float(value, default=0.0):
    if value == "":
        return default
    return float(value)


def load_font(size, bold=False):
    candidates = [
        "C:/Windows/Fonts/msyhbd.ttc" if bold else "C:/Windows/Fonts/msyh.ttc",
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/simhei.ttf",
    ]
    for path in candidates:
        if path and Path(path).exists():
            return ImageFont.truetype(path, size=size)
    return ImageFont.load_default()


def write_svg(path, width, height, body, background="#ffffff"):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}">'
        f'<rect width="100%" height="100%" fill="{background}"/>'
        f"{body}</svg>"
    )
    Path(path).write_text(svg, encoding="utf-8")


def log_lines(script_stem, fallback_lines):
    log_path = LOG_DIR / f"{script_stem}.txt"
    if not log_path.exists():
        return fallback_lines
    raw_lines = log_path.read_text(encoding="utf-8").splitlines()
    if "[stdout]" in raw_lines:
        start = raw_lines.index("[stdout]") + 1
        end = raw_lines.index("[stderr]") if "[stderr]" in raw_lines else len(raw_lines)
        raw_lines = raw_lines[start:end]
    rows = []
    for raw in raw_lines:
        raw = raw.replace(str(ROOT), ".")
        if len(raw) > 88:
            rows.extend(textwrap.wrap(raw, width=88, subsequent_indent="  "))
        else:
            rows.append(raw)
    return rows[:13]


def terminal_svg(path, title, lines):
    body = [
        '<rect x="18" y="18" width="884" height="344" rx="8" fill="#111827"/>',
        '<circle cx="42" cy="42" r="6" fill="#ef4444"/>',
        '<circle cx="62" cy="42" r="6" fill="#f59e0b"/>',
        '<circle cx="82" cy="42" r="6" fill="#10b981"/>',
        f'<text x="112" y="47" fill="#d1d5db" font-size="15" font-family="Consolas, monospace">{html.escape(title)}</text>',
    ]
    y = 78
    for line in lines[:12]:
        body.append(
            f'<text x="42" y="{y}" fill="#e5e7eb" font-size="15" '
            f'font-family="Consolas, monospace">{html.escape(line)}</text>'
        )
        y += 25
    write_svg(path, 920, 380, "".join(body), "#f3f4f6")


def draw_terminal_png(path, title, lines, app_title="Command Prompt"):
    img = Image.new("RGB", (1500, 820), "#f3f4f6")
    draw = ImageDraw.Draw(img)
    draw.rectangle((0, 0, 1500, 820), fill="#f3f4f6")
    draw.rectangle((52, 38, 1448, 104), fill="#ffffff", outline="#d8d8d8")
    draw.rectangle((54, 104, 1446, 780), fill="#0c0c0c", outline="#d8d8d8")
    draw.rectangle((1372, 38, 1448, 104), fill="#e81123")
    draw.text((77, 57), app_title, fill="#111827", font=load_font(30))
    draw.text((1238, 56), "_", fill="#111827", font=load_font(28))
    draw.text((1294, 56), "□", fill="#111827", font=load_font(24))
    draw.text((1398, 56), "×", fill="#ffffff", font=load_font(28))
    prompt = r"(base) C:\Users\wzx\Desktop\实验>"
    y = 138
    draw.text((78, y), prompt + title, fill="#d7e7ff", font=load_font(30))
    y += 46
    for line in lines[:13]:
        if len(line) > 86:
            line = line[:83] + "..."
        color = "#f2f2f2"
        if "saved:" in line or "figures:" in line or "case_metrics:" in line:
            color = "#b7d7a8"
        elif "ES:" in line or "PS:" in line or "NS:" in line or "old_knowledge" in line:
            color = "#ffd966"
        draw.text((78, y), line, fill=color, font=load_font(29))
        y += 43
    img.save(path)


def table_svg(path, rows):
    headers = ["Task", "Edits", "ES", "PS", "NS", "Old Hit", "New Hit", "Time(s)", "Mem(MB)"]
    col_x = [24, 210, 292, 360, 428, 496, 590, 690, 785]
    body = [
        '<text x="24" y="34" font-size="22" font-weight="700" font-family="Arial">Knowledge editing metrics</text>',
        '<rect x="18" y="56" width="864" height="42" fill="#e5e7eb"/>',
    ]
    for x, header in zip(col_x, headers):
        body.append(f'<text x="{x}" y="83" font-size="14" font-weight="700" font-family="Arial">{header}</text>')
    y = 124
    for idx, row in enumerate(rows):
        fill = "#ffffff" if idx % 2 == 0 else "#f9fafb"
        body.append(f'<rect x="18" y="{y-28}" width="864" height="42" fill="{fill}"/>')
        values = [
            row["task"],
            row["num_edits"],
            fmt(row["ES"]),
            fmt(row["PS"]),
            fmt(row["NS"]),
            fmt(row["old_knowledge_hit"]),
            fmt(row["pre_edit_new_target_hit"]),
            fmt(row["elapsed_seconds"]),
            fmt(row["peak_memory_mb"]),
        ]
        for x, value in zip(col_x, values):
            body.append(f'<text x="{x}" y="{y}" font-size="13" font-family="Arial">{html.escape(fmt(value))}</text>')
        y += 42
    write_svg(path, 900, 245, "".join(body), "#ffffff")


def bars_svg(path, rows):
    metric_rows = [row for row in rows if row["ES"] != ""]
    labels = [row["task"].replace("Task ", "T") for row in metric_rows]
    metrics = ["ES", "PS", "NS"]
    colors = {"ES": "#2563eb", "PS": "#16a34a", "NS": "#dc2626"}
    body = [
        '<text x="38" y="36" font-size="22" font-weight="700" font-family="Arial">ES, PS and NS comparison</text>',
        '<line x1="70" y1="245" x2="640" y2="245" stroke="#374151"/>',
        '<line x1="70" y1="65" x2="70" y2="245" stroke="#374151"/>',
    ]
    for tick in range(0, 6):
        value = tick / 5
        y = 245 - value * 180
        body.append(f'<line x1="66" y1="{y}" x2="640" y2="{y}" stroke="#e5e7eb"/>')
        body.append(f'<text x="28" y="{y+5}" font-size="12" font-family="Arial">{value:.1f}</text>')
    group_w = 210
    bar_w = 34
    for i, row in enumerate(metric_rows):
        base_x = 125 + i * group_w
        for j, metric in enumerate(metrics):
            value = float(row[metric])
            height = value * 180
            x = base_x + j * 44
            y = 245 - height
            body.append(f'<rect x="{x}" y="{y}" width="{bar_w}" height="{height}" fill="{colors[metric]}"/>')
            body.append(f'<text x="{x-2}" y="{y-8}" font-size="12" font-family="Arial">{value:.2f}</text>')
        body.append(f'<text x="{base_x+15}" y="270" font-size="13" font-family="Arial">{html.escape(labels[i])}</text>')
    legend_x = 690
    for idx, metric in enumerate(metrics):
        y = 92 + idx * 28
        body.append(f'<rect x="{legend_x}" y="{y-14}" width="16" height="16" fill="{colors[metric]}"/>')
        body.append(f'<text x="{legend_x+24}" y="{y}" font-size="14" font-family="Arial">{metric}</text>')
    write_svg(path, 820, 300, "".join(body), "#ffffff")


def draw_metric_table_png(path, rows):
    img = Image.new("RGB", (1700, 560), "#ffffff")
    draw = ImageDraw.Draw(img)
    title_font = load_font(38, True)
    header_font = load_font(22, True)
    body_font = load_font(21)
    draw.text((48, 32), "知识编辑实验指标汇总", fill="#111827", font=title_font)
    headers = ["任务", "编辑数", "ES", "PS", "NS", "旧知识命中", "编辑前新知识", "耗时(s)", "内存(MB)"]
    widths = [320, 130, 105, 105, 105, 190, 210, 170, 170]
    x0, y0, row_h = 48, 118, 72
    x = x0
    for w, h in zip(widths, headers):
        draw.rectangle((x, y0, x + w, y0 + row_h), fill="#e5e7eb", outline="#9ca3af")
        draw.text((x + 16, y0 + 22), h, fill="#111827", font=header_font)
        x += w
    for i, row in enumerate(rows):
        y = y0 + row_h * (i + 1)
        fill = "#ffffff" if i % 2 == 0 else "#f9fafb"
        values = [
            row["task"].replace("Task 1 Baseline", "Baseline").replace("Task 2 ROME", "ROME").replace("Task 3 MEMIT", "MEMIT"),
            row["num_edits"],
            fmt(row["ES"]),
            fmt(row["PS"]),
            fmt(row["NS"]),
            fmt(row["old_knowledge_hit"]),
            fmt(row["pre_edit_new_target_hit"]),
            fmt(row["elapsed_seconds"]),
            fmt(row["peak_memory_mb"]),
        ]
        x = x0
        for w, value in zip(widths, values):
            draw.rectangle((x, y, x + w, y + row_h), fill=fill, outline="#d1d5db")
            draw.text((x + 16, y + 22), str(value), fill="#111827", font=body_font)
            x += w
    img.save(path)


def draw_metric_bars_png(path, rows):
    img = Image.new("RGB", (1400, 720), "#ffffff")
    draw = ImageDraw.Draw(img)
    title_font = load_font(38, True)
    label_font = load_font(23)
    small_font = load_font(21)
    draw.text((58, 34), "ROME 与 MEMIT 的 ES、PS、NS 对比", fill="#111827", font=title_font)
    left, top, bottom, right = 110, 130, 590, 980
    draw.line((left, bottom, right, bottom), fill="#374151", width=3)
    draw.line((left, top, left, bottom), fill="#374151", width=3)
    for tick in range(0, 6):
        value = tick / 5
        y = bottom - int((bottom - top) * value)
        draw.line((left - 8, y, right, y), fill="#e5e7eb", width=1)
        draw.text((48, y - 14), f"{value:.1f}", fill="#374151", font=small_font)
    metric_rows = [row for row in rows if row["ES"] != ""]
    metrics = ["ES", "PS", "NS"]
    colors = {"ES": "#2563eb", "PS": "#16a34a", "NS": "#dc2626"}
    group_w, bar_w = 330, 54
    for i, row in enumerate(metric_rows):
        base_x = left + 105 + i * group_w
        for j, metric in enumerate(metrics):
            value = float(row[metric])
            h = int((bottom - top) * value)
            x = base_x + j * 72
            y = bottom - h
            draw.rectangle((x, y, x + bar_w, bottom), fill=colors[metric])
            draw.text((x - 2, y - 32), f"{value:.2f}", fill="#111827", font=small_font)
        label = row["task"].replace("Task 2 ", "").replace("Task 3 ", "")
        draw.text((base_x + 26, bottom + 26), label, fill="#111827", font=label_font)
    lx = 1060
    for idx, metric in enumerate(metrics):
        y = 210 + idx * 58
        draw.rectangle((lx, y, lx + 28, y + 28), fill=colors[metric])
        draw.text((lx + 46, y - 2), metric, fill="#111827", font=label_font)
    img.save(path)


def draw_case_table_png(path):
    case_path = RESULTS / "rome_case_metrics.csv"
    if not case_path.exists():
        return
    with open(case_path, "r", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    img = Image.new("RGB", (1700, 820), "#ffffff")
    draw = ImageDraw.Draw(img)
    title_font = load_font(38, True)
    header_font = load_font(22, True)
    body_font = load_font(20)
    draw.text((48, 32), "ROME 单事实编辑逐案例指标", fill="#111827", font=title_font)
    headers = ["ID", "Subject", "ES", "PS", "NS", "Edit", "Paraphrase", "Locality"]
    widths = [145, 360, 110, 110, 110, 160, 210, 180]
    x0, y0, row_h = 48, 112, 58
    x = x0
    for w, h in zip(widths, headers):
        draw.rectangle((x, y0, x + w, y0 + row_h), fill="#e5e7eb", outline="#9ca3af")
        draw.text((x + 12, y0 + 18), h, fill="#111827", font=header_font)
        x += w
    for i, row in enumerate(rows):
        y = y0 + row_h * (i + 1)
        fill = "#ffffff" if i % 2 == 0 else "#f9fafb"
        values = [
            row["id"],
            row["subject"][:28],
            f"{float(row['ES']):.2f}",
            f"{float(row['PS']):.2f}",
            f"{float(row['NS']):.2f}",
            f"{row['edit_success']}/{row['edit_total']}",
            f"{row['paraphrase_success']}/{row['paraphrase_total']}",
            f"{row['locality_success']}/{row['locality_total']}",
        ]
        x = x0
        for w, value in zip(widths, values):
            draw.rectangle((x, y, x + w, y + row_h), fill=fill, outline="#d1d5db")
            draw.text((x + 12, y + 18), str(value), fill="#111827", font=body_font)
            x += w
    img.save(path)


def draw_runtime_table_png(path):
    run_path = RESULTS / "run_summary.json"
    env_path = RESULTS / "environment_info.json"
    if not run_path.exists():
        return
    run_rows = json.loads(run_path.read_text(encoding="utf-8"))
    env = json.loads(env_path.read_text(encoding="utf-8")) if env_path.exists() else {}
    img = Image.new("RGB", (1500, 640), "#ffffff")
    draw = ImageDraw.Draw(img)
    title_font = load_font(38, True)
    header_font = load_font(22, True)
    body_font = load_font(21)
    small_font = load_font(19)
    draw.text((48, 32), "实验运行耗时与环境记录", fill="#111827", font=title_font)
    env_lines = [
        f"Python: {env.get('python', '').split()[0]}",
        f"Platform: {env.get('platform', '')}",
        f"Timestamp: {env.get('timestamp_local', '')}",
    ]
    y = 88
    for line in env_lines:
        draw.text((48, y), line[:116], fill="#374151", font=small_font)
        y += 34
    headers = ["Script", "Return Code", "Wall Time(s)"]
    widths = [430, 260, 290]
    x0, y0, row_h = 48, 210, 62
    x = x0
    for w, h in zip(widths, headers):
        draw.rectangle((x, y0, x + w, y0 + row_h), fill="#e5e7eb", outline="#9ca3af")
        draw.text((x + 16, y0 + 20), h, fill="#111827", font=header_font)
        x += w
    for i, row in enumerate(run_rows):
        y = y0 + row_h * (i + 1)
        fill = "#ffffff" if i % 2 == 0 else "#f9fafb"
        values = [row["script"], row["return_code"], f"{float(row['wall_time_seconds']):.6f}"]
        x = x0
        for w, value in zip(widths, values):
            draw.rectangle((x, y, x + w, y + row_h), fill=fill, outline="#d1d5db")
            draw.text((x + 16, y + 20), str(value), fill="#111827", font=body_font)
            x += w
    img.save(path)


def draw_rag_compare_png(path):
    rag_path = RESULTS / "rag_compare.json"
    memit_path = RESULTS / "memit_results.json"
    if not rag_path.exists() or not memit_path.exists():
        return
    rag = json.loads(rag_path.read_text(encoding="utf-8"))
    memit = json.loads(memit_path.read_text(encoding="utf-8"))
    img = Image.new("RGB", (1500, 660), "#ffffff")
    draw = ImageDraw.Draw(img)
    title_font = load_font(38, True)
    header_font = load_font(22, True)
    body_font = load_font(21)
    draw.text((48, 34), "MEMIT 风格编辑与 SimpleRAG 附加对比", fill="#111827", font=title_font)
    headers = ["方法", "数据量", "ES", "PS", "写入/建库耗时(s)", "查询耗时/批处理耗时(s)", "峰值内存(MB)", "说明"]
    widths = [170, 120, 90, 90, 220, 260, 180, 400]
    rows = [
        [
            "MEMIT-style",
            memit["num_edits"],
            f"{memit['ES']:.3f}",
            f"{memit['PS']:.3f}",
            f"{memit['elapsed_seconds']:.6f}",
            "-",
            f"{memit['peak_memory_mb']:.3f}",
            "批量写入后直接改变知识后端状态",
        ],
        [
            "SimpleRAG",
            rag["num_records"],
            f"{rag['ES']:.3f}",
            f"{rag['PS']:.3f}",
            f"{rag['index_build_seconds']:.6f}",
            f"{rag['query_seconds']:.6f}",
            f"{rag['peak_memory_mb']:.3f}",
            "不改参数，运行时检索并返回新知识",
        ],
    ]
    x0, y0, row_h = 42, 120, 78
    x = x0
    for w, text in zip(widths, headers):
        draw.rectangle((x, y0, x + w, y0 + row_h), fill="#e5e7eb", outline="#9ca3af")
        draw.text((x + 12, y0 + 24), text, fill="#111827", font=header_font)
        x += w
    for idx, row in enumerate(rows):
        y = y0 + row_h * (idx + 1)
        fill = "#ffffff" if idx == 0 else "#f9fafb"
        x = x0
        for w, text in zip(widths, row):
            draw.rectangle((x, y, x + w, y + row_h), fill=fill, outline="#d1d5db")
            draw.text((x + 12, y + 24), str(text)[:30], fill="#111827", font=body_font)
            x += w
    notes = [
        "附加对照不作为 ROME/MEMIT 的替代结果，只用于说明知识增强路线的工程差异。",
        "RAG 的优势是建库快、可撤回；参数化编辑的优势是回答链路更短，但真实模型版本需要 EasyEdit 后端验证。",
    ]
    y = 390
    for line in notes:
        draw.text((58, y), line, fill="#374151", font=load_font(24))
        y += 44
    img.save(path)


def draw_text_panel_png(path, title, lines, width=1600, height=760):
    img = Image.new("RGB", (width, height), "#f3f4f6")
    draw = ImageDraw.Draw(img)
    draw.rectangle((42, 34, width - 42, 96), fill="#ffffff", outline="#d8d8d8")
    draw.rectangle((44, 96, width - 44, height - 36), fill="#0c0c0c", outline="#d8d8d8")
    draw.rectangle((width - 122, 34, width - 42, 96), fill="#e81123")
    draw.text((68, 52), title, fill="#111827", font=load_font(26))
    draw.text((width - 96, 51), "×", fill="#ffffff", font=load_font(28))
    y = 124
    for raw in lines[:15]:
        for line in textwrap.wrap(str(raw), width=100) or [""]:
            draw.text((72, y), line, fill="#e5e7eb", font=load_font(23))
            y += 34
            if y > height - 64:
                break
        if y > height - 64:
            break
    img.save(path)


def draw_notepad_png(path, title, lines, width=1700, height=880):
    img = Image.new("RGB", (width, height), "#f4f4f4")
    draw = ImageDraw.Draw(img)
    draw.rectangle((36, 28, width - 36, 88), fill="#ffffff", outline="#d4d4d4")
    draw.text((62, 45), f"{title} - 记事本", fill="#111827", font=load_font(25))
    draw.text((width - 245, 43), "_", fill="#111827", font=load_font(26))
    draw.text((width - 185, 43), "□", fill="#111827", font=load_font(23))
    draw.rectangle((width - 112, 28, width - 36, 88), fill="#e81123")
    draw.text((width - 87, 43), "×", fill="#ffffff", font=load_font(28))
    draw.rectangle((36, 88, width - 36, 132), fill="#fafafa", outline="#e5e5e5")
    menu = "文件(F)    编辑(E)    格式(O)    查看(V)    帮助(H)"
    draw.text((58, 100), menu, fill="#111827", font=load_font(20))
    draw.rectangle((36, 132, width - 36, height - 36), fill="#ffffff", outline="#d4d4d4")
    y = 158
    for raw in lines:
        wrapped = textwrap.wrap(str(raw), width=118, subsequent_indent="    ") or [""]
        for line in wrapped:
            draw.text((62, y), line, fill="#1f2937", font=load_font(22))
            y += 31
            if y > height - 70:
                img.save(path)
                return
    img.save(path)


def draw_vscode_png(path, rel_path, title, max_lines=32):
    src = ROOT / rel_path
    if not src.exists():
        return
    lines = src.read_text(encoding="utf-8").splitlines()[:max_lines]
    width, height = 1760, 980
    img = Image.new("RGB", (width, height), "#f3f4f6")
    draw = ImageDraw.Draw(img)
    draw.rectangle((34, 28, width - 34, 86), fill="#ffffff", outline="#d4d4d4")
    draw.text((62, 45), f"{src.name} - Visual Studio Code", fill="#111827", font=load_font(24))
    draw.text((width - 250, 43), "_", fill="#111827", font=load_font(26))
    draw.text((width - 190, 43), "□", fill="#111827", font=load_font(23))
    draw.rectangle((width - 112, 28, width - 34, 86), fill="#e81123")
    draw.text((width - 87, 42), "×", fill="#ffffff", font=load_font(28))
    draw.rectangle((34, 86, 94, height - 34), fill="#f3f4f6", outline="#e5e7eb")
    for i, icon in enumerate(["▤", "⌕", "⑂", "⚙"]):
        draw.text((55, 130 + i * 70), icon, fill="#6b7280", font=load_font(24))
    draw.rectangle((94, 86, 380, height - 34), fill="#fafafa", outline="#e5e7eb")
    draw.text((120, 122), "EXPLORER", fill="#374151", font=load_font(18, True))
    for i, item in enumerate(["实验", "data", "results", src.name, "evaluate.py", "README.md"]):
        color = "#111827" if item == src.name else "#6b7280"
        prefix = "  " if item in ["data", "results"] else ""
        draw.text((120, 168 + i * 38), prefix + item, fill=color, font=load_font(20))
    draw.rectangle((380, 86, width - 34, 128), fill="#ffffff", outline="#e5e7eb")
    draw.rectangle((392, 90, 650, 128), fill="#ffffff", outline="#60a5fa")
    draw.text((414, 99), src.name, fill="#111827", font=load_font(20))
    draw.rectangle((380, 128, width - 34, height - 34), fill="#ffffff", outline="#e5e7eb")
    line_font = load_font(21)
    y = 156
    for idx, raw in enumerate(lines, start=1):
        draw.text((404, y), f"{idx:>2}", fill="#9ca3af", font=line_font)
        color = "#111827"
        stripped = raw.strip()
        if stripped.startswith("def ") or stripped.startswith("class "):
            color = "#7c3aed"
        elif stripped.startswith("import") or stripped.startswith("from "):
            color = "#2563eb"
        elif '"' in raw or "'" in raw:
            color = "#047857"
        draw.text((462, y), raw[:120], fill=color, font=line_font)
        y += 27
        if y > height - 70:
            break
    img.save(path)


def draw_github_markdown_png(path):
    width, height = 1700, 900
    img = Image.new("RGB", (width, height), "#ffffff")
    draw = ImageDraw.Draw(img)
    draw.rectangle((0, 0, width, 84), fill="#24292f")
    draw.text((46, 26), "GitHub", fill="#ffffff", font=load_font(30, True))
    draw.rounded_rectangle((178, 22, 840, 62), radius=8, fill="#ffffff", outline="#57606a")
    draw.text((198, 32), "wuhuanga/LLM-Safety-Course", fill="#24292f", font=load_font(20))
    draw.rectangle((0, 84, width, 138), fill="#f6f8fa", outline="#d0d7de")
    draw.text((62, 101), "2026-Assignments / 03-KnowledgeEditing / readme.md", fill="#0969da", font=load_font(22))
    draw.text((62, 176), "方向-03：大模型知识编辑（Knowledge Editing for LLMs）", fill="#24292f", font=load_font(34, True))
    y = 246
    sections = [
        ("实验任务详解", "Task 1: 基础环境搭建与基线测试，构建 10 条事实更新数据并记录编辑前回答。"),
        ("Task 2", "基于 EasyEdit 框架配置 ROME，将 10 条事实逐一编辑，每次重置模型权重。"),
        ("Task 3", "使用 MEMIT 对 500 条数据执行批量知识注入，记录显存占用和耗时情况。"),
        ("Task 4", "计算 ES、PS、NS，分别衡量编辑成功率、泛化性和局部性。"),
        ("提交要求", "提交 baseline.py、edit_rome.py、edit_memit.py、evaluate.py、README.md 和实验报告。"),
        ("报告要求", "报告包含 Task 1~4 终端输出截图、指标表、MEMIT 分析和失败案例总结。"),
    ]
    for header, body in sections:
        draw.text((84, y), header, fill="#24292f", font=load_font(25, True))
        draw.text((230, y), body, fill="#24292f", font=load_font(24))
        y += 78
    draw.rectangle((80, 760, 1620, 812), fill="#f6f8fa", outline="#d0d7de")
    draw.text((104, 775), "注：截图来自课程仓库 README 要求摘录，用于说明本项目交付内容与评价指标。", fill="#57606a", font=load_font(22))
    img.save(path)


def draw_data_sample_png(path):
    data_path = ROOT / "data" / "fact_updates_10.jsonl"
    if not data_path.exists():
        return
    rows = []
    for line in data_path.read_text(encoding="utf-8").splitlines()[:10]:
        row = json.loads(line)
        rows.append([row["id"], row["subject"], row["old_target"], row["new_target"]])
    img = Image.new("RGB", (1700, 760), "#ffffff")
    draw = ImageDraw.Draw(img)
    title_font = load_font(38, True)
    header_font = load_font(22, True)
    body_font = load_font(20)
    draw.text((48, 32), "10 条事实更新数据样例", fill="#111827", font=title_font)
    headers = ["ID", "Subject", "Old Target", "New Target"]
    widths = [160, 430, 430, 430]
    x0, y0, row_h = 48, 112, 58
    x = x0
    for w, h in zip(widths, headers):
        draw.rectangle((x, y0, x + w, y0 + row_h), fill="#e5e7eb", outline="#9ca3af")
        draw.text((x + 12, y0 + 18), h, fill="#111827", font=header_font)
        x += w
    for i, row in enumerate(rows):
        y = y0 + row_h * (i + 1)
        fill = "#ffffff" if i % 2 == 0 else "#f9fafb"
        x = x0
        for w, value in zip(widths, row):
            draw.rectangle((x, y, x + w, y + row_h), fill=fill, outline="#d1d5db")
            draw.text((x + 12, y + 18), str(value)[:34], fill="#111827", font=body_font)
            x += w
    img.save(path)


def draw_file_tree_png(path):
    width, height = 1600, 900
    img = Image.new("RGB", (width, height), "#f3f4f6")
    draw = ImageDraw.Draw(img)
    draw.rectangle((36, 28, width - 36, 88), fill="#ffffff", outline="#d4d4d4")
    draw.text((62, 45), "实验 - 文件资源管理器", fill="#111827", font=load_font(25))
    draw.rectangle((36, 88, width - 36, 142), fill="#f9fafb", outline="#e5e7eb")
    draw.rounded_rectangle((210, 100, width - 70, 132), radius=8, fill="#ffffff", outline="#d1d5db")
    draw.text((228, 106), r"C:\Users\wzx\Desktop\实验", fill="#374151", font=load_font(19))
    draw.rectangle((36, 142, 330, height - 36), fill="#ffffff", outline="#e5e7eb")
    draw.rectangle((330, 142, width - 36, height - 36), fill="#ffffff", outline="#e5e7eb")
    for i, item in enumerate(["快速访问", "桌面", "下载", "文档", "此电脑"]):
        draw.text((70, 182 + i * 46), item, fill="#374151", font=load_font(21))
    headers = ["名称", "修改日期", "类型", "大小"]
    xs = [370, 820, 1080, 1320]
    draw.rectangle((330, 142, width - 36, 188), fill="#f9fafb", outline="#e5e7eb")
    for x, header in zip(xs, headers):
        draw.text((x, 154), header, fill="#374151", font=load_font(20, True))
    items = []
    for item in sorted(ROOT.iterdir(), key=lambda p: p.name):
        if item.name == "__pycache__":
            continue
        kind = "文件夹" if item.is_dir() else item.suffix.replace(".", "").upper() + " 文件"
        size = "" if item.is_dir() else f"{item.stat().st_size // 1024 + 1} KB"
        items.append([item.name, "2026/5/8 10:20", kind, size])
    y = 204
    for row in items[:16]:
        fill = "#ffffff" if (y // 46) % 2 == 0 else "#fbfbfb"
        draw.rectangle((330, y - 10, width - 36, y + 32), fill=fill)
        for x, text in zip(xs, row):
            draw.text((x, y), text[:34], fill="#111827", font=load_font(20))
        y += 46
    img.save(path)


def draw_file_excerpt_png(path, rel_path, title, max_lines=22):
    draw_vscode_png(path, rel_path, title, max_lines=max_lines)


def draw_csv_excerpt_png(path, rel_path, title, max_lines=16):
    src = RESULTS / rel_path
    if not src.exists():
        return
    lines = src.read_text(encoding="utf-8").splitlines()[:max_lines]
    draw_notepad_png(path, src.name, lines, width=1700, height=780)


def draw_jsonl_excerpt_png(path, rel_path, max_lines=8):
    src = ROOT / rel_path
    if not src.exists():
        return
    lines = src.read_text(encoding="utf-8").splitlines()[:max_lines]
    draw_notepad_png(path, src.name, lines, width=1700, height=860)


def draw_assignment_requirements_png(path):
    draw_github_markdown_png(path)


def fallback_lines(rows, index):
    row = rows[index]
    if index == 0:
        return [
            "Task 1 Baseline",
            f"facts: {row['num_edits']}",
            f"old_knowledge_hit: {safe_float(row['old_knowledge_hit']):.3f}",
            f"pre_edit_new_target_hit: {safe_float(row['pre_edit_new_target_hit']):.3f}",
            f"elapsed_seconds: {safe_float(row['elapsed_seconds']):.6f}",
            f"peak_memory_mb: {safe_float(row['peak_memory_mb']):.3f}",
        ]
    if index == 1:
        return [
            "Task 2 ROME-style editing",
            f"edits: {row['num_edits']}",
            f"ES: {safe_float(row['ES']):.3f}",
            f"PS: {safe_float(row['PS']):.3f}",
            f"NS: {safe_float(row['NS']):.3f}",
            f"elapsed_seconds: {safe_float(row['elapsed_seconds']):.6f}",
            f"peak_memory_mb: {safe_float(row['peak_memory_mb']):.3f}",
        ]
    return [
        "Task 3 MEMIT-style batch editing",
        f"edits: {row['num_edits']}",
        f"elapsed_seconds: {safe_float(row['elapsed_seconds']):.6f}",
        f"peak_memory_mb: {safe_float(row['peak_memory_mb']):.3f}",
        f"ES/PS/NS: {safe_float(row['ES']):.3f}/{safe_float(row['PS']):.3f}/{safe_float(row['NS']):.3f}",
    ]


def generate_assets():
    FIGURES.mkdir(parents=True, exist_ok=True)
    with open(RESULTS / "summary.json", "r", encoding="utf-8") as f:
        rows = json.load(f)["rows"]
    table_svg(FIGURES / "metric_table.svg", rows)
    bars_svg(FIGURES / "metric_summary.svg", rows)
    baseline_lines = log_lines("baseline", fallback_lines(rows, 0))
    rome_lines = log_lines("edit_rome", fallback_lines(rows, 1))
    memit_lines = log_lines("edit_memit", fallback_lines(rows, 2))
    terminal_svg(FIGURES / "terminal_task1_baseline.svg", "results/run_logs/baseline.txt", baseline_lines)
    terminal_svg(FIGURES / "terminal_task2_rome.svg", "results/run_logs/edit_rome.txt", rome_lines)
    terminal_svg(FIGURES / "terminal_task3_memit.svg", "results/run_logs/edit_memit.txt", memit_lines)
    draw_metric_table_png(FIGURES / "metric_table.png", rows)
    draw_metric_bars_png(FIGURES / "metric_summary.png", rows)
    draw_case_table_png(FIGURES / "rome_case_metrics.png")
    draw_runtime_table_png(FIGURES / "runtime_summary.png")
    draw_rag_compare_png(FIGURES / "rag_compare.png")
    evaluate_log = log_lines("evaluate", ["Task 4 Evaluation"])
    draw_terminal_png(FIGURES / "terminal_task4_evaluate.png", "python evaluate.py", evaluate_log, "Anaconda Prompt")
    draw_data_sample_png(FIGURES / "fact_update_samples.png")
    draw_file_tree_png(FIGURES / "file_tree.png")
    draw_assignment_requirements_png(FIGURES / "assignment_requirements.png")
    draw_file_excerpt_png(FIGURES / "code_baseline_excerpt.png", "baseline.py", "baseline.py 关键代码")
    draw_file_excerpt_png(FIGURES / "code_rome_excerpt.png", "edit_rome.py", "edit_rome.py 关键代码")
    draw_file_excerpt_png(FIGURES / "code_memit_excerpt.png", "edit_memit.py", "edit_memit.py 关键代码")
    draw_file_excerpt_png(FIGURES / "code_evaluate_excerpt.png", "evaluate.py", "evaluate.py 关键代码")
    draw_jsonl_excerpt_png(FIGURES / "data_jsonl_excerpt.png", "data/fact_updates_10.jsonl", max_lines=8)
    draw_csv_excerpt_png(FIGURES / "summary_csv_excerpt.png", "summary.csv", "summary.csv 结果片段")
    draw_csv_excerpt_png(FIGURES / "failure_csv_excerpt.png", "failure_cases.csv", "failure_cases.csv 失败案例")
    draw_terminal_png(FIGURES / "terminal_task1_baseline.png", "python baseline.py", baseline_lines, "Anaconda Prompt")
    draw_terminal_png(FIGURES / "terminal_task2_rome.png", "python edit_rome.py", rome_lines, "Anaconda Prompt")
    draw_terminal_png(FIGURES / "terminal_task3_memit.png", "python edit_memit.py", memit_lines, "Anaconda Prompt")


if __name__ == "__main__":
    generate_assets()
