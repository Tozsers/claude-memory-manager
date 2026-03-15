> ⚠️ **Újabb verzió elérhető / Newer version available:**
> **[claude-memory-manager-v2](https://github.com/Tozsers/claude-memory-manager-v2)** — REST API, biztonsági javítások, jobb keresés.
> Ez az eredeti (v1) verzió, Issues tabbal. / This is the original (v1) with Issues tab.

---# 🧠 Claude Memory Manager

**English** | [Magyar](#magyar)

A lightweight self-hosted web UI for managing [Claude Code](https://docs.anthropic.com/en/docs/claude-code) persistent memory files — browse, edit, create, delete and search your AI memory context across all projects.

![Python](https://img.shields.io/badge/python-3.8+-blue?style=flat-square) ![Flask](https://img.shields.io/badge/flask-3.0-green?style=flat-square) ![License](https://img.shields.io/badge/license-MIT-orange?style=flat-square)

---

## What is Claude Code memory?

Claude Code supports a file-based persistent memory system. You can store long-term context (preferences, project status, feedback, references) in Markdown files that are automatically loaded at the start of every new session — so Claude never forgets who you are or what you're working on.

Memory files live here:
```
~/.claude/projects/<project-name>/memory/
```

Each file uses a simple frontmatter format:
```markdown
---
name: My coding preferences
description: How I like code formatted and explained
type: user
---

Always use dark themes. Keep responses short and direct.
Use Python type hints everywhere.
```

**Memory types:**
| Type | Purpose |
|------|---------|
| `user` | Who you are, preferences, communication style |
| `feedback` | Corrections you gave Claude — so it does not repeat mistakes |
| `project` | Ongoing work, goals, decisions, deadlines |
| `reference` | External resources, URLs, ports, file paths |

---

## Features

| Feature | Description |
|---------|-------------|
| 📋 **Browse** | List all memory files across all projects, filtered by type |
| ✏️ **Edit** | Edit memory files directly in the browser |
| ➕ **Create** | New memory with auto-generated frontmatter template |
| 🗑️ **Delete** | Delete with confirmation dialog |
| 📄 **MEMORY.md viewer** | View your index file per project |
| 🔍 **Session search** | Full-text search across all archived Claude sessions |

---

## Requirements

- Python 3.8+
- Claude Code installed and configured
- (Optional) A session archive script

---

## Installation

```bash
git clone https://github.com/yourusername/claude-memory-manager
cd claude-memory-manager
python3 -m venv venv
venv/bin/pip install -r requirements.txt
```

---

## Configuration

Edit `config.yaml` before first run:

```yaml
# Where Claude Code stores your project memory files
memory_base_path: "~/.claude/projects"

# Where your session archive .md files are stored (optional)
session_archive_path: "~/.claude/session_archive"

# Port for the web UI
port: 7910
```

---

## Usage

```bash
./start.sh
```

Then open **http://localhost:7910** in your browser.

The `start.sh` script will automatically create a virtual environment and install dependencies on first run.

---

## How the memory system works

```
~/.claude/
└── projects/
    └── my-project/
        └── memory/
            ├── MEMORY.md          <- index file (auto-loaded every session)
            ├── user_profile.md    <- who you are
            ├── feedback.md        <- corrections given to Claude
            ├── project_status.md  <- what is in progress
            └── references.md     <- useful links, ports, paths
```

**MEMORY.md** is the index — it is loaded automatically by Claude Code at the start of every session. Keep it concise (~200 lines max) and use it to point to the detailed topic files.

Detailed topic files are read on-demand when Claude needs them.

---

## Session Archive (optional)

The Session Archive tab lets you browse and search past Claude Code conversations, if you save them as `.md` files.

You need a session archiving script that saves conversations after each session. Point `session_archive_path` in `config.yaml` to the directory where those files are stored.

Example archive structure:
```
~/.claude/session_archive/
├── INDEX.md
├── abc123.md
└── def456.md
```

---

## Desktop shortcut (Linux)

```bash
cp claude_memory_manager.desktop ~/Desktop/
chmod +x ~/Desktop/claude_memory_manager.desktop
```

---

## License

MIT

---
---

<a name="magyar"></a>

# 🧠 Claude Memory Manager — Magyar leírás

Egy könnyű, saját szerveren futó webes felület a [Claude Code](https://docs.anthropic.com/en/docs/claude-code) perzisztens memória fájlok kezeléséhez. Böngészd, szerkeszd, hozd létre, töröld és keresd az AI kontextus fájlokat minden projekten keresztül.

---

## Mi a Claude Code memória?

A Claude Code támogat egy fájl-alapú perzisztens memória rendszert. Hosszú távú kontextust tárolhatsz (preferenciák, projekt státusz, visszajelzések, referenciák) Markdown fájlokban, amelyek automatikusan betöltődnek minden új session elején — így Claude soha nem felejti el, ki vagy és min dolgozol.

A memória fájlok helye:
```
~/.claude/projects/<projekt-neve>/memory/
```

Minden fájl egy egyszerű frontmatter formátumot használ:
```markdown
---
name: Kódolási preferenciáim
description: Hogyan szeretem a kódot formázva és magyarázva
type: user
---

Mindig sötét témát használj. Tartsd rövidre a válaszokat.
Magyar UI szövegeket írj minden appba.
```

**Memória típusok:**
| Típus | Célja |
|-------|-------|
| `user` | Ki vagy, preferenciák, kommunikációs stílus |
| `feedback` | Javítások amiket adtál Claude-nak — hogy ne ismételje meg a hibákat |
| `project` | Folyamatban lévő munka, célok, döntések, határidők |
| `reference` | Külső erőforrások, URL-ek, portok, fájl útvonalak |

---

## Funkciók

| Funkció | Leírás |
|---------|--------|
| 📋 **Böngészés** | Összes memória fájl listázása típus-szűrővel |
| ✏️ **Szerkesztés** | Fájlok szerkesztése közvetlenül a böngészőben |
| ➕ **Létrehozás** | Új memória automatikusan generált frontmatter sablonnal |
| 🗑️ **Törlés** | Törlés megerősítő dialógussal |
| 📄 **MEMORY.md nézet** | Az index fájl megtekintése projektenként |
| 🔍 **Session keresés** | Teljes szöveges keresés az archivált Claude sessionökben |

---

## Követelmények

- Python 3.8+
- Telepített és beállított Claude Code
- (Opcionális) Session archiváló script

---

## Telepítés

```bash
git clone https://github.com/yourusername/claude-memory-manager
cd claude-memory-manager
python3 -m venv venv
venv/bin/pip install -r requirements.txt
```

---

## Konfiguráció

Az első indítás előtt szerkeszd a `config.yaml` fájlt:

```yaml
# Ahol a Claude Code tárolja a projekt memória fájlokat
memory_base_path: "~/.claude/projects"

# Ahol a session archívum .md fájlok vannak (opcionális)
session_archive_path: "~/.claude/session_archive"

# A webes felület portja
port: 7910
```

---

## Használat

```bash
./start.sh
```

Majd nyisd meg a **http://localhost:7910** címet a böngészőben.

A `start.sh` script az első indításkor automatikusan létrehozza a virtual environment-et és telepíti a függőségeket.

---

## Hogyan működik a memória rendszer

```
~/.claude/
└── projects/
    └── sajat-projektem/
        └── memory/
            ├── MEMORY.md           <- index fájl (minden sessionben betöltődik)
            ├── user_profil.md      <- ki vagy te
            ├── visszajelzesek.md   <- javítások amiket adtál Claude-nak
            ├── projekt_status.md   <- mi van folyamatban
            └── referenciak.md     <- hasznos linkek, portok, útvonalak
```

A **MEMORY.md** az index — Claude Code minden session elején automatikusan betölti. Legyen tömör (~200 sor max) és mutasson a részletes topic fájlokra.

A részletes topic fájlokat Claude igény szerint olvassa be.

---

## Session Archívum (opcionális)

A Session Archive tab lehetővé teszi a korábbi Claude Code beszélgetések böngészését és keresését, ha `.md` fájlként mentetted azokat.

Ehhez egy session archiváló script szükséges, ami minden session után elmenti a beszélgetést. A `config.yaml`-ben a `session_archive_path` mutasson arra a könyvtárra.

---

## Asztali ikon (Linux)

```bash
cp claude_memory_manager.desktop ~/Desktop/
chmod +x ~/Desktop/claude_memory_manager.desktop
```

---

## Licenc

MIT — szabadon használható, módosítható és terjeszthető.
