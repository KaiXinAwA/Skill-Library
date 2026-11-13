#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
douyin_pipeline.py — 抖音链接 → 知识卡片 → Open WebUI 知识库 全自动流水线

用法:
  python douyin_pipeline.py <抖音链接> [模型名]
  python douyin_pipeline.py --file links.txt [模型名]

特性:
  - 中文 / 英文 / 其他语言的视频都能处理：ASR 自动识别语言，卡片统一输出简体中文
  - 卡片强清洗：剥掉模型最爱加的 ```markdown 包裹、重写合法 YAML frontmatter
  - 模型自动校验：指定的模型不在 Ollama 里就自动回落到已安装的模型
  - 入库幂等：同名文件已在知识库则复用，不产生重复
"""
import io
import json
import os
import re
import subprocess
import sys
import time
from datetime import date
from pathlib import Path

try:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")
except Exception:
    pass

try:
    import requests
except ImportError:
    requests = None

PROJECT_DIR = Path(r"D:/AI/douyin_text_extraction")
UV_EXE = r"C:/Users/richa/AppData/Local/Microsoft/WinGet/Packages/astral-sh.uv_Microsoft.Winget.Source_8wekyb3d8bbwe/uv.exe"
FFMPEG_BIN = r"C:/Users/richa/AppData/Local/Microsoft/WinGet/Packages/Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe/ffmpeg-9.0.2-full_build/bin"
OUTPUT_DIR = PROJECT_DIR / "output"
OWUI_URL = "http://localhost:8080"
OLLAMA_TAGS = "http://localhost:11434/api/tags"
OLLAMA_URL = "http://localhost:11434/api/chat"
DEFAULT_MODEL = "qwen3.5:4b"
FALLBACK_MODELS = ["qwen3.5:4b", "qwen3.5:9b", "deepseek-r1:7b", "qwen2.5-coder:7b"]
KNOWLEDGE_IDS = [
    ("d580d64e-1d2d-40cf-9dc5-7900bd85c76c", "抖音知识卡片"),
    ("1c84643c-02d3-452e-9336-1718b10acafd", "个人综合知识库"),
]
TODAY = date.today().isoformat()
EMBED_HINTS = ("embed", "bert", "bge", "m3")


def read_api_key():
    env_path = Path(r"D:\Reborn\skill\Skill-Library\OpenWebUI-Sync\.env")
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line.startswith("OPENWEBUI_API_KEY="):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    return ""


API_KEY = read_api_key()


def log(msg):
    print(msg, flush=True)


def run_cli(args, timeout=1200):
    env = os.environ.copy()
    env["PATH"] = FFMPEG_BIN + os.pathsep + env.get("PATH", "")
    cmd = [UV_EXE, "run", "--extra", "local-chinese", "douyin-extract", "extract"] + args
    log(f"  [CLI] {' '.join(cmd[:8])}...")
    result = subprocess.run(cmd, cwd=str(PROJECT_DIR), env=env,
                            capture_output=True, text=True, timeout=timeout,
                            encoding="utf-8", errors="replace")
    if result.returncode != 0:
        raise RuntimeError(f"CLI 失败 ({result.returncode}): {(result.stderr or '')[-800:]}")
    return result


def extract_script(url):
    safe_id = re.sub(r"[^\w\-]", "_", url)[-40:]
    out_path = OUTPUT_DIR / f"dy_{int(time.time())}_{safe_id}.json"
    run_cli([url, "--format", "json", "--output", str(out_path)])
    if not out_path.exists():
        raise RuntimeError("CLI 声称成功但输出文件不存在")
    data = json.loads(out_path.read_text(encoding="utf-8"))
    data["_path"] = str(out_path)
    return data


def detect_language(text):
    cjk = len(re.findall(r"[\u4e00-\u9fff]", text or ""))
    latin = len(re.findall(r"[A-Za-z]", text or ""))
    if cjk >= 8 and cjk * 2 >= latin:
        return "zh"
    if latin > cjk * 2 and latin >= 20:
        return "en"
    if cjk or latin:
        return "other"
    return "unknown"


LANG_LABEL = {"zh": "中文", "en": "英文", "other": "其他语言", "unknown": "未知"}


SYSTEM_PROMPT = """你是一名知识管理专家。用户会给你一段从抖音视频提取的逐字稿（附带元数据），请把它整理成一份结构化的 Markdown 知识卡片。

# 语言规则（最高优先级）
1. 无论逐字稿原文是中文、英文还是其他语言，输出正文必须是简体中文。
2. 原文不是中文时：先翻译成中文，再用中文写卡片；人名、产品名、专业术语可保留英文原词并附中文解释。
3. 「原文摘录」保留原句原文；若原句不是中文，在引用块下再加一行「> 中文：<该句的中文直译>」。
4. 视频标题不是中文时，title 用中文意译，并把原题写进 original_title。

# 输出格式（必须严格遵守）
- 直接输出 Markdown 正文，禁止用三个反引号包裹整篇卡片，不要任何解释性前言、结语、寒暄。
- 第一行必须是三个短横线组成的 YAML 分隔线，frontmatter 结束后再用同样的分隔线收尾。

# Frontmatter 字段
title / original_title（可选）/ source / author / date / type / tags / status / valid_from / weight / source_language
- type 取值：概念 / 方法 / 案例 / 经验 / 行业判断
- tags：3-6 个中文关键词，写成 YAML 列表
- status：draft / reviewed / verified
- weight：1-5 的整数
- source_language：zh / en / other

# 正文结构
## 一句话总结（1-2 句）
## 核心内容（用三级标题分小节，改写口播为清晰条目，删掉口癖、重复、语气词）
## 关键概念/术语（逐条解释，可中英对照）
## 适用场景（什么时候该调用这条知识）
## 限制与边界（什么情况下不适用或会失效）
## 与现有知识关联（建议关联的主题词）
## 原文摘录（2-3 段最有价值原话，引用块）"""


def resolve_model(requested):
    if requests is None:
        return requested
    try:
        tags = requests.get(OLLAMA_TAGS, timeout=20).json().get("models", [])
        names = [m.get("name") or m.get("model") for m in tags]
    except Exception as e:
        log(f"     ! 无法读取 Ollama 模型列表（{e}），按原样尝试 {requested}")
        return requested
    if requested and requested in names:
        return requested
    for cand in FALLBACK_MODELS:
        if cand in names:
            log(f"     ! 模型 {requested} 不存在，回落到 {cand}")
            return cand
    chat = [n for n in names if n and not any(h in n.lower() for h in EMBED_HINTS)]
    if chat:
        log(f"     ! 模型 {requested} 不存在，回落到 {chat[0]}")
        return chat[0]
    raise RuntimeError("Ollama 里没有任何可用的对话模型")


def call_ollama(model, prompt, system):
    body = {
        "model": model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ],
        "stream": False,
        "options": {"temperature": 0.2, "num_ctx": 8192},
    }
    r = requests.post(OLLAMA_URL, json=body, timeout=1800)
    r.raise_for_status()
    return r.json()["message"]["content"]


def organize(meta, text, model, lang):
    prompt = f"""请把下面这段抖音视频逐字稿整理成结构化知识卡片（输出简体中文）。

【视频元数据】
标题：{meta.get("title", "未知")}
作者：{meta.get("author", "未知")}
时长：{meta.get("duration", "未知")} 秒
原始链接：{meta.get("douyin_url", meta.get("video_url", "未知"))}
原文语言判定：{LANG_LABEL.get(lang, "未知")}（source_language 填 {lang}）

【逐字稿】
{text}"""
    md = call_ollama(model, prompt, SYSTEM_PROMPT)
    md = re.sub(r"<think>.*?</think>", "", md, flags=re.S)
    return md.strip()


def strip_fences(md):
    s = (md or "").replace("\ufeff", "").strip()
    m = re.match(r"^```[A-Za-z0-9_-]*\s*\n", s)
    if m:
        s = s[m.end():]
        s = re.sub(r"\n?```\s*$", "", s)
    s = re.sub(r"\n```\s*$", "", s.strip())
    return s.strip()


def _fm_value(fm, key):
    m = re.search(rf"^{re.escape(key)}:\s*(.*)$", fm, flags=re.M)
    if not m:
        return ""
    return m.group(1).strip().strip('"').strip("'").strip()


def _split_tags(raw):
    raw = raw.strip().strip("[]")
    parts = re.split(r"[,，、;；]", raw)
    out = []
    for p in parts:
        p = p.strip().strip('"').strip("'").strip()
        if p and len(p) <= 20:
            out.append(p)
    return out[:6]


def _q(s):
    s = (s or "").replace("\\", "\\\\").replace('"', "'").replace("\n", " ")
    return f'"{s.strip()}"'


def build_card(md, meta, lang):
    body = strip_fences(md)
    fm = ""
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n?", body, flags=re.S)
    if m:
        fm = m.group(1)
        body = body[m.end():].lstrip()

    title = _fm_value(fm, "title") or (meta.get("title") or "未命名")
    title = strip_fences(title)[:80]
    original_title = _fm_value(fm, "original_title")
    source = _fm_value(fm, "source") or meta.get("douyin_url") or meta.get("video_url") or ""
    author = _fm_value(fm, "author") or (meta.get("author") or "")
    ktype = _fm_value(fm, "type") or "概念"
    if ktype not in ("概念", "方法", "案例", "经验", "行业判断"):
        ktype = "概念"
    status = _fm_value(fm, "status") or "draft"
    if status not in ("draft", "reviewed", "verified"):
        status = "draft"
    tags = _split_tags(_fm_value(fm, "tags")) or ["抖音", "知识卡片"]
    weight_raw = _fm_value(fm, "weight")
    try:
        weight = max(1, min(5, int(re.findall(r"\d+", weight_raw)[0]))) if weight_raw else 3
    except Exception:
        weight = 3

    lines = ["---", f"title: {_q(title)}"]
    if original_title:
        lines.append(f"original_title: {_q(original_title)}")
    if source:
        lines.append(f"source: {_q(source)}")
    if author:
        lines.append(f"author: {_q(author)}")
    lines += [
        f"date: {TODAY}",
        f"type: {ktype}",
        "tags: [" + ", ".join(_q(t) for t in tags) + "]",
        f"status: {status}",
        f"valid_from: {TODAY}",
        f"weight: {weight}",
        f"source_language: {lang if lang in ('zh', 'en', 'other') else 'other'}",
        "---",
        "",
    ]
    if not re.search(r"^##\s", body, flags=re.M):
        body = "## 一句话总结\n" + body
    return "\n".join(lines) + body.strip() + "\n"


def _kb_files(kb_id, headers):
    r = requests.get(f"{OWUI_URL}/api/v1/knowledge/{kb_id}/files", headers=headers, timeout=120)
    r.raise_for_status()
    return r.json().get("items", [])


def upload_to_knowledge(md_content, filename):
    if not API_KEY:
        raise RuntimeError("OPENWEBUI_API_KEY 未找到（检查 D:\\AI\\Skill-Library\\OpenWebUI-Sync\\.env）")
    if requests is None:
        raise RuntimeError("requests 库不可用")
    headers = {"Authorization": f"Bearer {API_KEY}"}

    file_id = None
    for kb_id, kb_name in KNOWLEDGE_IDS:
        try:
            for it in _kb_files(kb_id, headers):
                if it.get("filename") == filename:
                    file_id = it.get("id")
                    log(f"     = 已在「{kb_name}」，复用 file_id={file_id[:8]}...")
                    break
        except Exception as e:
            log(f"     ! 幂等检查跳过（{kb_name}）: {e}")
        if file_id:
            break

    if not file_id:
        last_err = None
        for attempt in (1, 2, 3):
            try:
                r = requests.post(
                    f"{OWUI_URL}/api/v1/files/",
                    headers=headers,
                    files={"file": (filename, md_content.encode("utf-8"), "text/markdown")},
                    timeout=300,
                )
                r.raise_for_status()
                file_id = r.json().get("id")
                if not file_id:
                    raise RuntimeError(f"上传响应缺少 id: {r.text[:200]}")
                break
            except Exception as e:
                last_err = e
                log(f"     ! 上传第 {attempt} 次失败: {e}")
                time.sleep(3)
        if not file_id:
            raise RuntimeError(f"上传失败（已重试 3 次）: {last_err}")

    attached = []
    processed = []
    for kb_id, kb_name in KNOWLEDGE_IDS:
        try:
            r2 = requests.post(
                f"{OWUI_URL}/api/v1/knowledge/{kb_id}/file/add",
                headers=headers,
                json={"file_id": file_id},
                timeout=300,
            )
            if r2.status_code == 400:
                try:
                    names = [it.get("filename") for it in _kb_files(kb_id, headers)]
                    if filename in names:
                        attached.append(kb_name)
                        continue
                except Exception:
                    pass
            r2.raise_for_status()
            attached.append(kb_name)
        except Exception as e:
            log(f"     ! 关联「{kb_name}」失败: {e}")
            continue
        # 向量化：只 add 不 process 的话文件在库里但检索不到（前端看着像空库）
        try:
            r3 = requests.post(
                f"{OWUI_URL}/api/v1/retrieval/process/file",
                headers=headers,
                json={"file_id": file_id, "content": md_content, "collection_name": kb_id},
                timeout=900,
            )
            r3.raise_for_status()
            processed.append(kb_name)
        except Exception as e:
            log(f"     ! 「{kb_name}」向量化失败: {e}")
    if attached and not processed:
        raise RuntimeError(f"文件已上传并关联（{' / '.join(attached)}），但向量化失败，RAG 检索不到")
    if not attached:
        raise RuntimeError("文件已上传，但关联知识库全部失败")
    return file_id, attached, processed


def process_one(url, model):
    log(f"\n▶ 处理: {url}")
    log("  ① 下载+转写 (SenseVoice，语言自动识别)...")
    data = extract_script(url)
    meta, text = data.get("metadata", {}), data.get("text", "")
    if not text.strip():
        raise RuntimeError("逐字稿为空（视频可能无口播或被静音）")
    lang = detect_language(text)
    log(f"     ✓ 逐字稿 {len(text)} 字 | 判定语种 {LANG_LABEL.get(lang, lang)} | {str(meta.get('title',''))[:40]}")

    used_model = resolve_model(model)
    log(f"  ② 本地整理 ({used_model}) → 输出简体中文...")
    raw = organize(meta, text, used_model, lang)
    md = build_card(raw, meta, lang)

    md_path = OUTPUT_DIR / f"{Path(data['_path']).stem}_knowledge.md"
    md_path.write_text(md, encoding="utf-8")
    log(f"     ✓ 知识卡片 {md_path.name}（{len(md)} 字符，代码块包裹已清理）")

    log("  ③ 推入 Open WebUI 知识库...")
    file_id, attached, processed = upload_to_knowledge(md, md_path.name)
    log(f"     ✓ 已入库 file_id={file_id[:8]}... → {' / '.join(attached)}")
    log(f"     ✓ 已向量化（可检索）→ {' / '.join(processed) or '无'}")

    title = _fm_value(md[:400], "title") or str(meta.get("title") or "")
    return {"url": url, "title": title, "lang": lang, "text_len": len(text),
            "card": str(md_path), "file_id": file_id, "kb": processed or attached}


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
    elif args:
        urls = [args[0]]
        model = args[1] if len(args) > 1 else model
    else:
        sys.exit("没有链接可处理")

    log(f"流水线启动 | 模型: {model} | 共 {len(urls)} 条 | 目标库: {' / '.join(n for _, n in KNOWLEDGE_IDS)}")
    results, errors = [], []
    for url in urls:
        try:
            results.append(process_one(url, model))
        except Exception as e:
            errors.append({"url": url, "error": str(e)})
            log(f"  ✗ 失败: {e}")
    log(f"\n== 完成 == 成功 {len(results)} / 失败 {len(errors)}")
    for r in results:
        log(f"  ✓ [{r['lang']}] {r['title'][:50]} → {r['card']}")
    for e in errors:
        log(f"  ✗ {e['url']} → {e['error']}")
    return 0 if not errors else 2


if __name__ == "__main__":
    sys.exit(main())
