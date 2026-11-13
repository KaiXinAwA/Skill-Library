#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
douyin_pipeline.py — 抖音链接 → 知识卡片 → Open WebUI 知识库 全自动流水线
纯标准库实现，任何 Python 3.8+ 均可运行。

用法:
  python douyin_pipeline.py <抖音链接> [模型名]            # 单个链接
  python douyin_pipeline.py --file links.txt [模型名]       # 批量（每行一个链接）

依赖的外部工具（已安装）:
  - uv        : C:/Users/richa/AppData/Local/Microsoft/WinGet/Packages/astral-sh.uv_Microsoft.Winget.Source_8wekyb3d8bbwe/uv.exe
  - ffmpeg    : C:/Users/richa/AppData/Local/Microsoft/WinGet/Packages/Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe/ffmpeg-9.0.2-full_build/bin
  - likebeans : D:/AI/douyin_text_extraction（SenseVoiceSmall 本地转写）
  - Ollama    : http://localhost:11434（qwen3.5:4b / qwen3:8b 本地整理）
  - Open WebUI: http://localhost:8080（知识库入库）
"""
import json
import os
import re
import subprocess
import sys
import time
from datetime import date
from pathlib import Path

try:
    import requests
except ImportError:
    requests = None  # 退化提示在 upload_to_knowledge 里给出

# ---------- 路径与常量 ----------
PROJECT_DIR = Path(r"D:/AI/douyin_text_extraction")
UV_EXE = r"C:/Users/richa/AppData/Local/Microsoft/WinGet/Packages/astral-sh.uv_Microsoft.Winget.Source_8wekyb3d8bbwe/uv.exe"
FFMPEG_BIN = r"C:/Users/richa/AppData/Local/Microsoft/WinGet/Packages/Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe/ffmpeg-9.0.2-full_build/bin"
OUTPUT_DIR = PROJECT_DIR / "output"
KNOWLEDGE_ID = "1c84643c-02d3-452e-9336-1718b10acafd"   # 个人综合知识库
OWUI_URL = "http://localhost:8080"
OLLAMA_URL = "http://localhost:11434/api/chat"
DEFAULT_MODEL = "qwen3.5:4b"
TODAY = date.today().isoformat()

def read_api_key():
    """从 OpenWebUI-Sync/.env 读取 API key，避免硬编码"""
    env_path = Path(r"D:\AI\Skill-Library\OpenWebUI-Sync\.env")
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line.startswith("OPENWEBUI_API_KEY="):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    return ""

API_KEY = read_api_key()

def log(msg):
    print(msg, flush=True)

def run_cli(args, timeout=900):
    """运行 likebeans CLI 提取逐字稿"""
    env = os.environ.copy()
    env["PATH"] = FFMPEG_BIN + os.pathsep + env.get("PATH", "")
    cmd = [UV_EXE, "run", "--extra", "local-chinese", "douyin-extract", "extract"] + args
    log(f"  [CLI] {' '.join(cmd[:8])}...")
    result = subprocess.run(cmd, cwd=str(PROJECT_DIR), env=env,
                            capture_output=True, text=True, timeout=timeout)
    if result.returncode != 0:
        raise RuntimeError(f"CLI 失败 ({result.returncode}): {result.stderr[-800:]}")
    return result

def extract_script(url):
    """提取逐字稿，返回 JSON dict"""
    safe_id = re.sub(r"[^\w\-]", "_", url)[-40:]
    out_path = OUTPUT_DIR / f"dy_{int(time.time())}_{safe_id}.json"
    run_cli([url, "--format", "json", "--output", str(out_path)])
    if not out_path.exists():
        raise RuntimeError("CLI 声称成功但输出文件不存在")
    data = json.loads(out_path.read_text(encoding="utf-8"))
    data["_path"] = str(out_path)
    return data

def call_ollama(model, prompt, system):
    body = {
        "model": model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
        "stream": False,
    }
    r = requests.post(OLLAMA_URL, json=body, timeout=900)
    r.raise_for_status()
    return r.json()["message"]["content"]

SYSTEM_PROMPT = """你是一名知识管理专家。用户会给你一段从抖音视频提取的逐字稿（含元数据）。请把它整理成一份结构化的 Markdown 知识卡片，遵循以下规范：

# 知识卡片规范
1. 开头是 YAML frontmatter，包含：title（视频标题）、source（原始链接）、author、date（整理日期，用当天）、type（知识类型：概念/方法/案例/经验/行业判断）、tags（3-6个关键词标签）、status（draft/reviewed/verified）、valid_from、weight（权重 1-5，越高越可靠）
2. 正文结构：
   - ## 一句话总结：用 1-2 句话概括这个知识的核心
   - ## 核心内容：分小节（###）整理，把口播改写成清晰条目，保留关键概念、定义、步骤、例子；删除口癖、重复、语气词
   - ## 关键概念/术语：列出视频中出现的专业概念并给出简要解释
   - ## 适用场景：说明这个知识什么时候应该被调用（这是知识卡片最重要的部分）
   - ## 限制与边界：哪些情况不适用、哪些条件会失效
   - ## 与现有知识关联：建议关联的主题词（供知识库建立链接）
   - ## 原文摘录：保留 2-3 段最有价值的原话（用引用块）
3. 语言：与逐字稿一致（中文），专业、简洁、信息密度高。
4. 只输出 Markdown 本身，不要解释，不要额外对话。"""

def organize(meta, text, model):
    prompt = f"""请把下面这段抖音视频逐字稿整理成结构化知识卡片。

【视频元数据】
标题：{meta.get("title", "未知")}
作者：{meta.get("author", "未知")}
时长：{meta.get("duration", "未知")} 秒
原始链接：{meta.get("douyin_url", meta.get("video_url", "未知"))}

【逐字稿】
{text}"""
    return call_ollama(model, prompt, SYSTEM_PROMPT)

def fix_frontmatter(md):
    """修正模型幻觉的日期字段为今天"""
    md = re.sub(r"date:\s*\d{4}-\d{2}-\d{2}", f"date: {TODAY}", md)
    md = re.sub(r"valid_from:\s*\d{4}-\d{2}-\d{2}", f"valid_from: {TODAY}", md)
    return md

def upload_to_knowledge(md_content, filename):
    """上传 Markdown 到 Open WebUI 并关联知识库，返回 file_id（幂等：同名已在库则直接返回）"""
    if not API_KEY:
        raise RuntimeError("OPENWEBUI_API_KEY 未找到（检查 .env）")
    if requests is None:
        raise RuntimeError("requests 库不可用（Open WebUI venv 应自带）")
    headers = {"Authorization": f"Bearer {API_KEY}"}

    # 0. 幂等检查：同名文件已在知识库 → 直接返回其 id
    try:
        r0 = requests.get(f"{OWUI_URL}/api/v1/knowledge/{KNOWLEDGE_ID}/files", headers=headers, timeout=60)
        r0.raise_for_status()
        items = r0.json().get("items", [])
        for it in items:
            if it.get("filename") == filename:
                log(f"     = 已在知识库，复用 file_id={it['id'][:8]}...")
                return it["id"]
    except Exception as e:
        log(f"     ! 幂等检查跳过: {e}")

    last_err = None
    for attempt in (1, 2):
        try:
            # 1. 上传文件（标准 multipart，2~5 秒；向量化在后台异步完成）
            r = requests.post(
                f"{OWUI_URL}/api/v1/files/",
                headers=headers,
                files={"file": (filename, md_content.encode("utf-8"), "text/markdown")},
                timeout=180,
            )
            r.raise_for_status()
            file_id = r.json().get("id")
            if not file_id:
                raise RuntimeError(f"文件上传响应缺少 id: {r.text[:200]}")
            # 2. 关联到知识库
            r2 = requests.post(
                f"{OWUI_URL}/api/v1/knowledge/{KNOWLEDGE_ID}/file/add",
                headers=headers,
                json={"file_id": file_id},
                timeout=180,
            )
            if r2.status_code == 400:
                # 可能并发下刚被加过：再查一次，确认已在库则视为成功
                r3 = requests.get(f"{OWUI_URL}/api/v1/knowledge/{KNOWLEDGE_ID}/files", headers=headers, timeout=60)
                for it in r3.json().get("items", []):
                    if it.get("filename") == filename:
                        log(f"     = add 400 但已在库，复用 file_id={it['id'][:8]}...")
                        return it["id"]
            r2.raise_for_status()
            return file_id
        except Exception as e:
            last_err = e
            log(f"     ! 入库第 {attempt} 次失败: {e}")
            time.sleep(3)
    raise RuntimeError(f"入库失败（已重试 2 次）: {last_err}")

def process_one(url, model):
    log(f"\n▶ 处理: {url}")
    # 1. 提取
    log("  ① 下载+转写 (SenseVoiceSmall)...")
    data = extract_script(url)
    meta, text = data.get("metadata", {}), data.get("text", "")
    log(f"     ✓ 逐字稿 {len(text)} 字 | {meta.get('title','')[:40]}")
    # 2. 整理
    log(f"  ② 本地整理 ({model})...")
    md = organize(meta, text, model)
    md = fix_frontmatter(md)
    title = meta.get("title", "untitled")[:30].replace('"', "")
    md_path = OUTPUT_DIR / f"{Path(data['_path']).stem}_knowledge.md"
    md_path.write_text(md, encoding="utf-8")
    log(f"     ✓ 知识卡片 {md_path.name} ({len(md)} 字符)")
    # 3. 入库
    log("  ③ 推入 Open WebUI 知识库...")
    fname = md_path.name
    file_id = upload_to_knowledge(md, fname)
    log(f"     ✓ 已入库 file_id={file_id[:8]}... → 个人综合知识库")
    return {"url": url, "title": meta.get("title"), "text_len": len(text),
            "card": str(md_path), "file_id": file_id}

def main():
    args = sys.argv[1:]
    model = DEFAULT_MODEL
    urls = []
    if args and args[0] == "--file":
        if len(args) < 2:
            sys.exit("用法: python douyin_pipeline.py --file links.txt [模型名]")
        model = args[2] if len(args) > 2 else model
        links_file = Path(args[1])
        if not links_file.exists():
            sys.exit(f"文件不存在: {links_file}")
        urls = [l.strip() for l in links_file.read_text(encoding="utf-8").splitlines() if l.strip()]
    else:
        urls = [args[0]]
        model = args[1] if len(args) > 1 else model

    if not urls:
        sys.exit("没有链接可处理")
    log(f"流水线启动 | 模型: {model} | 共 {len(urls)} 条")

    results, errors = [], []
    for i, url in enumerate(urls, 1):
        try:
            results.append(process_one(url, model))
        except Exception as e:
            errors.append({"url": url, "error": str(e)})
            log(f"  ✗ 失败: {e}")
    log(f"\n== 完成 == 成功 {len(results)} / 失败 {len(errors)}")
    for r in results:
        log(f"  ✓ {r['title'][:50]} → {r['card']}")
    return 0 if not errors else 2

if __name__ == "__main__":
    sys.exit(main())