# Servos – Offline AI Forensic Assistant

> **"Forensics for the Rest of Us"**

An offline, AI-powered digital forensics assistant that detects suspicious storage devices, enforces safe backups, and guides users through structured forensic investigations — all without sending any data to the cloud.

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run Servos
python -m servos.main

# Or use specific commands
python -m servos.main new        # Start new investigation
python -m servos.main scan       # Quick scan a directory
python -m servos.main devices    # List connected devices
python -m servos.main monitor    # Monitor for new USB devices
python -m servos.main cases      # View past investigations
python -m servos.main settings   # Configure Servos
```

## 🔍 Features

- **USB Device Detection & Auto‑Investigation** – Real-time monitoring for new storage devices with optional automatic full investigations when devices are connected
- **Mandatory Backup** – Forces forensic backup with MD5/SHA-256 integrity hashing
- **Three Investigation Modes:**
  - **Full Automation** – End-to-end pipeline with auto-generated reports
  - **Hybrid** – Step-by-step with user confirmations
  - **Manual** – Guided checklists for expert investigators
- **Forensic Analysis Modules:**
  - File system enumeration & metadata extraction
  - File hashing (MD5, SHA-256)
  - Browser history extraction (Chrome, Firefox)
  - Malware indicator detection (YARA-like rules, entropy analysis)
  - Timeline reconstruction
- **AI-Powered Guidance** – Offline LLM (Ollama) for investigation recommendations
- **Report Generation** – PDF, JSON, CSV, and TXT formats
- **Case Management** – SQLite-based case tracking
- **Playbook System** – YAML-based reusable investigation workflows

## 🛡️ Tech Stack

| Component | Technology |
|-----------|-----------|
| Language | Python 3.10+ |
| LLM Engine | Ollama (Llama 3.1 8B) |
| CLI | Click + Rich |
| Database | SQLite + SQLAlchemy |
| Forensics | psutil, hashlib, YARA-like rules |
| Reports | ReportLab (PDF), Jinja2 |
| Playbooks | PyYAML |

## 📁 Project Structure

```
servos/
├── __init__.py
├── main.py                    # Entry point
├── config.py                  # Configuration management
├── models/
│   └── schema.py              # Data models & database
├── detection/
│   └── usb_monitor.py         # USB device detection
├── preservation/
│   └── backup.py              # Forensic backup & chain-of-custody
├── forensics/
│   ├── file_analyzer.py       # File system analysis
│   ├── hasher.py              # File hashing
│   ├── artifact_extractor.py  # Browser, registry, log extraction
│   ├── malware_detector.py    # Malware indicators
│   └── timeline.py            # Timeline reconstruction
├── llm/
│   └── investigator.py        # Ollama LLM integration
├── orchestration/
│   └── workflow.py            # Investigation pipeline
├── reports/
│   └── generator.py           # PDF/JSON/CSV/TXT reports
├── cli/
│   ├── main.py                # CLI commands
│   └── ui.py                  # Rich UI helpers
├── playbooks/
│   ├── engine.py              # Playbook loader
│   └── defaults/
│       ├── usb_forensics.yaml
│       └── ransomware_triage.yaml
└── rules/
    └── malware_signatures.yar # YARA rules
```

## 🔧 Requirements

- Python 3.10+
- Ollama (optional, for AI-powered analysis)

## 📝 License

MIT License – Open source for the security community.

## 👥 Team

**MoMoSapiens** – CyberHack V4 Hackathon
- Akash Santhnu Sundar
- Shanmitha S
- Shivani M S
- Ajay C

---

*Built for CyberHack V4 – Offline LLM for Advanced Cyber Investigation Track*
