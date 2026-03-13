import os
import glob
import json
import yaml
from pathlib import Path
from datetime import datetime
from flask import Flask, jsonify, request, send_from_directory, render_template

app = Flask(__name__)

# Load config
def load_config():
    config_path = Path(__file__).parent / "config.yaml"
    with open(config_path) as f:
        cfg = yaml.safe_load(f)
    return {
        "memory_base": Path(cfg.get("memory_base_path", "~/.claude/projects")).expanduser(),
        "session_archive": Path(cfg.get("session_archive_path", "~/.claude/session_archive")).expanduser(),
        "port": cfg.get("port", 7900)
    }

def parse_frontmatter(content):
    """Parse frontmatter from markdown file."""
    meta = {"name": "", "description": "", "type": ""}
    body = content
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            try:
                fm = yaml.safe_load(parts[1])
                if fm:
                    meta = {
                        "name": fm.get("name", ""),
                        "description": fm.get("description", ""),
                        "type": fm.get("type", "")
                    }
                body = parts[2].strip()
            except:
                pass
    return meta, body

def find_memory_files(base_path):
    """Find all memory .md files under base_path/**/memory/"""
    pattern = str(base_path / "**" / "memory" / "*.md")
    files = glob.glob(pattern, recursive=True)
    result = []
    for f in sorted(files):
        fp = Path(f)
        try:
            content = fp.read_text(encoding="utf-8")
            meta, body = parse_frontmatter(content)
            project = fp.parent.parent.name
            result.append({
                "path": str(fp),
                "filename": fp.name,
                "project": project,
                "name": meta.get("name") or fp.stem,
                "description": meta.get("description", ""),
                "type": meta.get("type", ""),
                "size": len(content),
                "modified": datetime.fromtimestamp(fp.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
            })
        except Exception as e:
            result.append({"path": str(fp), "filename": fp.name, "error": str(e)})
    return result

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/config")
def api_config():
    cfg = load_config()
    return jsonify({
        "memory_base": str(cfg["memory_base"]),
        "session_archive": str(cfg["session_archive"])
    })

@app.route("/api/memories")
def api_memories():
    cfg = load_config()
    files = find_memory_files(cfg["memory_base"])
    return jsonify(files)

@app.route("/api/memory/read")
def api_memory_read():
    path = request.args.get("path")
    if not path:
        return jsonify({"error": "No path"}), 400
    try:
        content = Path(path).read_text(encoding="utf-8")
        meta, body = parse_frontmatter(content)
        return jsonify({"content": content, "meta": meta, "body": body})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/memory/save", methods=["POST"])
def api_memory_save():
    data = request.json
    path = data.get("path")
    content = data.get("content")
    if not path or content is None:
        return jsonify({"error": "Missing path or content"}), 400
    try:
        Path(path).write_text(content, encoding="utf-8")
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/memory/create", methods=["POST"])
def api_memory_create():
    data = request.json
    project_path = data.get("project_path")
    filename = data.get("filename")
    name = data.get("name", "")
    description = data.get("description", "")
    mem_type = data.get("type", "project")
    body = data.get("body", "")

    if not project_path or not filename:
        return jsonify({"error": "Missing project_path or filename"}), 400

    memory_dir = Path(project_path) / "memory"
    memory_dir.mkdir(parents=True, exist_ok=True)

    if not filename.endswith(".md"):
        filename += ".md"

    filepath = memory_dir / filename
    if filepath.exists():
        return jsonify({"error": "File already exists"}), 409

    content = f"""---
name: {name}
description: {description}
type: {mem_type}
---

{body}
"""
    filepath.write_text(content, encoding="utf-8")
    return jsonify({"ok": True, "path": str(filepath)})

@app.route("/api/memory/delete", methods=["POST"])
def api_memory_delete():
    data = request.json
    path = data.get("path")
    if not path:
        return jsonify({"error": "No path"}), 400
    try:
        Path(path).unlink()
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/projects")
def api_projects():
    cfg = load_config()
    base = cfg["memory_base"]
    projects = []
    if base.exists():
        for p in sorted(base.iterdir()):
            if p.is_dir():
                memory_dir = p / "memory"
                projects.append({
                    "name": p.name,
                    "path": str(p),
                    "has_memory": memory_dir.exists()
                })
    return jsonify(projects)

@app.route("/api/sessions")
def api_sessions():
    cfg = load_config()
    archive = cfg["session_archive"]
    sessions = []
    if archive.exists():
        index_path = archive / "INDEX.md"
        index_content = ""
        if index_path.exists():
            index_content = index_path.read_text(encoding="utf-8")

        for f in sorted(archive.glob("*.md"), key=lambda x: x.stat().st_mtime, reverse=True):
            if f.name == "INDEX.md":
                continue
            sessions.append({
                "filename": f.name,
                "path": str(f),
                "modified": datetime.fromtimestamp(f.stat().st_mtime).strftime("%Y-%m-%d %H:%M"),
                "size": f.stat().st_size
            })
    return jsonify(sessions)

@app.route("/api/session/read")
def api_session_read():
    path = request.args.get("path")
    if not path:
        return jsonify({"error": "No path"}), 400
    try:
        content = Path(path).read_text(encoding="utf-8")
        return jsonify({"content": content})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/sessions/search")
def api_sessions_search():
    q = request.args.get("q", "").lower()
    cfg = load_config()
    archive = cfg["session_archive"]
    results = []
    if not q:
        return jsonify([])
    for f in archive.glob("*.md"):
        if f.name == "INDEX.md":
            continue
        try:
            content = f.read_text(encoding="utf-8")
            if q in content.lower():
                lines = [l for l in content.split("\n") if q in l.lower()][:3]
                results.append({
                    "filename": f.name,
                    "path": str(f),
                    "modified": datetime.fromtimestamp(f.stat().st_mtime).strftime("%Y-%m-%d %H:%M"),
                    "matches": lines
                })
        except:
            pass
    results.sort(key=lambda x: x["modified"], reverse=True)
    return jsonify(results)

# --- Issues API ---

def get_issues_path(project_path):
    return Path(project_path) / "memory" / "issues.jsonl"

def read_issues(project_path):
    fp = get_issues_path(project_path)
    if not fp.exists():
        return []
    issues = []
    for line in fp.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            try:
                issues.append(json.loads(line))
            except:
                pass
    return issues

def write_issues(project_path, issues):
    fp = get_issues_path(project_path)
    fp.parent.mkdir(parents=True, exist_ok=True)
    fp.write_text("\n".join(json.dumps(i, ensure_ascii=False) for i in issues) + "\n", encoding="utf-8")

@app.route("/api/issues")
def api_issues_list():
    project_path = request.args.get("project_path")
    if not project_path:
        return jsonify({"error": "No project_path"}), 400
    issues = read_issues(project_path)
    # Sort: open/in-progress first, done last; within group by priority
    prio_order = {"high": 0, "medium": 1, "low": 2}
    status_order = {"open": 0, "in-progress": 1, "done": 2}
    issues.sort(key=lambda x: (status_order.get(x.get("status","open"), 0), prio_order.get(x.get("priority","medium"), 1)))
    return jsonify(issues)

@app.route("/api/issues/create", methods=["POST"])
def api_issues_create():
    data = request.json
    project_path = data.get("project_path")
    if not project_path:
        return jsonify({"error": "No project_path"}), 400
    issues = read_issues(project_path)
    next_id = max((i.get("id", 0) for i in issues), default=0) + 1
    issue = {
        "id": next_id,
        "type": data.get("type", "feature"),
        "title": data.get("title", ""),
        "description": data.get("description", ""),
        "status": "open",
        "priority": data.get("priority", "medium"),
        "created": datetime.now().strftime("%Y-%m-%d")
    }
    issues.append(issue)
    write_issues(project_path, issues)
    return jsonify({"ok": True, "issue": issue})

@app.route("/api/issues/update", methods=["POST"])
def api_issues_update():
    data = request.json
    project_path = data.get("project_path")
    issue_id = data.get("id")
    if not project_path or issue_id is None:
        return jsonify({"error": "Missing params"}), 400
    issues = read_issues(project_path)
    for issue in issues:
        if issue.get("id") == issue_id:
            for k in ["status", "priority", "title", "description", "type"]:
                if k in data:
                    issue[k] = data[k]
            break
    write_issues(project_path, issues)
    return jsonify({"ok": True})

@app.route("/api/issues/delete", methods=["POST"])
def api_issues_delete():
    data = request.json
    project_path = data.get("project_path")
    issue_id = data.get("id")
    if not project_path or issue_id is None:
        return jsonify({"error": "Missing params"}), 400
    issues = read_issues(project_path)
    issues = [i for i in issues if i.get("id") != issue_id]
    write_issues(project_path, issues)
    return jsonify({"ok": True})

@app.route("/api/issues/next", methods=["GET"])
def api_issues_next():
    project_path = request.args.get("project_path")
    if not project_path:
        return jsonify({"error": "No project_path"}), 400
    issues = read_issues(project_path)
    prio_order = {"high": 0, "medium": 1, "low": 2}
    open_issues = [i for i in issues if i.get("status") in ("open", "in-progress")]
    open_issues.sort(key=lambda x: prio_order.get(x.get("priority","medium"), 1))
    return jsonify(open_issues[:3])

if __name__ == "__main__":
    cfg = load_config()
    app.run(host="0.0.0.0", port=cfg["port"], debug=False)
