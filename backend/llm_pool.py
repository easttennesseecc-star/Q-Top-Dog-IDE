"""LLM pool discovery (local-first).

This module detects locally available LLM CLIs, running assistant processes,
local model files, and local/running services like Copilot, Gemini, ChatGPT, etc.
It avoids contacting external services but CAN detect running instances.
"""
import os
import shutil
import subprocess
import platform
import socket
import json
from typing import List, Dict, Optional, Any


def get_critical_system_models() -> List[str]:
    return [
        "gpt-4-windows-system",
        "system-default-llm",
    ]


# Extended list including Copilot, Gemini, ChatGPT, Grok
KNOWN_CLI_CANDIDATES = [
    ("gpt4all", "gpt4all"),
    ("gpt4all-lora", "gpt4all-lora"),
    ("gpt4o-local", "gpt4o"),
    ("gemini-local", "gemini"),
    ("chatgpt-local", "chatgpt"),
    ("copilot-cli", "copilot"),
    ("grok-local", "grok"),
    ("llama-cpp", "llama"),
    ("ollama", "ollama"),
    ("mistral-cli", "mistral"),
]

# Common ports where local LLM services run
LOCAL_SERVICE_PORTS = [
    (8000, "Local LLM Service"),
    (8001, "Ollama API"),
    (8080, "LLM Web UI"),
    (5000, "Flask LLM"),
    (3000, "Node LLM Service"),
    (9000, "Alternative LLM"),
    (11434, "Ollama Default"),
]

# Process keywords that indicate LLM/AI services
LLM_PROCESS_KEYWORDS = [
    "gpt4all", "chatgpt", "gemini", "llama", "copilot",
    "ollama", "mistral", "grok", "claude", "anthropic",
    "ai", "assistant", "llm", "model", "inference",
    "vscode", "code",  # VS Code for Copilot
]


def which(cmd: str) -> str:
    """Return full path of executable if found on PATH, else empty string."""
    p = shutil.which(cmd)
    return p or ""


def detect_clis() -> List[Dict]:
    found = []
    for name, binname in KNOWN_CLI_CANDIDATES:
        p = which(binname)
        if p:
            found.append({"name": name, "path": p, "source": "cli", "status": "available"})
    return found


def detect_running_services() -> List[Dict]:
    """Detect LLM services running on common local ports."""
    services = []
    for port, service_name in LOCAL_SERVICE_PORTS:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.5)
            result = sock.connect_ex(('127.0.0.1', port))
            sock.close()
            if result == 0:
                services.append({
                    "name": service_name,
                    "port": port,
                    "endpoint": f"http://localhost:{port}",
                    "source": "service",
                    "status": "running"
                })
        except Exception:
            pass
    return services


def list_processes(limit: int = 500) -> List[Dict]:
    """List running processes and identify LLM/AI services."""
    procs = []
    try:
        if platform.system() == "Windows":
            out = subprocess.check_output(
                ["tasklist", "/FO", "CSV", "/NH"],
                text=True,
                stderr=subprocess.DEVNULL,
                timeout=5
            )
            for line in out.strip().splitlines()[:limit]:
                parts = [p.strip('"') for p in line.split(',')]
                if parts:
                    procs.append({
                        "image": parts[0],
                        "pid": parts[1] if len(parts) > 1 else None
                    })
        else:
            out = subprocess.check_output(
                ["ps", "-eo", "pid,comm"],
                text=True,
                stderr=subprocess.DEVNULL,
                timeout=5
            )
            lines = out.strip().splitlines()[1:limit+1]
            for line in lines:
                m = line.strip().split(None, 1)
                if len(m) == 2:
                    procs.append({"pid": m[0], "image": m[1]})
    except Exception:
        pass
    return procs


def scan_common_install_paths() -> List[Dict]:
    """Scan common installation paths for LLM applications."""
    home = os.path.expanduser("~")
    if platform.system() == "Windows":
        program_files = os.environ.get("ProgramFiles", r"C:\Program Files")
        program_files_x86 = os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)")
        candidates = [
            os.path.join(program_files, "gpt4all"),
            os.path.join(program_files_x86, "gpt4all"),
            os.path.join(program_files, "Ollama"),
            os.path.join(home, ".local", "bin"),
            os.path.join(home, "AppData", "Local", "Programs"),
        ]
    else:
        candidates = [
            "/usr/local/bin",
            "/opt",
            os.path.join(home, ".local", "bin"),
            "/usr/bin",
        ]
    found = []
    for p in candidates:
        try:
            if os.path.exists(p):
                files = os.listdir(p)[:200]
                found.append({"path": p, "files": files})
        except Exception:
            pass
    return found


def discover_local_llms(model_dirs: Optional[List[str]] = None) -> List[Dict]:
    """Search for local model files (gguf, bin, pt, onnx) under common model directories."""
    critical = set(get_critical_system_models())
    found = []
    if model_dirs is None:
        model_dirs = [
            os.path.join(os.path.expanduser("~"), "models"),
            os.path.join(os.path.expanduser("~"), ".ollama", "models"),
            os.path.join(os.path.expanduser("~"), ".cache", "huggingface"),
            r"C:\models",
            r"C:\Users\%USERNAME%\.ollama\models",
            "/models",
            "/opt/models",
        ]
        # Expand environment variables
        model_dirs = [os.path.expandvars(d) for d in model_dirs]
    
    for d in model_dirs:
        try:
            if os.path.isdir(d):
                for fname in os.listdir(d):
                    if fname in critical:
                        continue
                    if fname.lower().endswith(('.bin', '.gguf', '.pt', '.onnx', '.safetensors')):
                        found.append({
                            "name": fname,
                            "path": os.path.join(d, fname),
                            "source": "localfile",
                            "status": "available"
                        })
        except Exception:
            pass
    return found


def detect_copilot() -> Optional[Dict]:
    """Detect GitHub Copilot via VS Code extension."""
    try:
        # Check if VS Code is running with Copilot
        procs = list_processes()
        for p in procs:
            name = (p.get("image") or "").lower()
            if "code" in name or "vscode" in name:
                return {
                    "name": "GitHub Copilot",
                    "source": "vscode",
                    "type": "copilot",
                    "status": "available",
                    "note": "Running via VS Code"
                }
        
        # Check VS Code config for Copilot
        home = os.path.expanduser("~")
        vscode_config = os.path.join(
            home,
            "AppData", "Local", "Programs", "Microsoft VS Code"
        ) if platform.system() == "Windows" else os.path.join(
            home,
            ".config", "Code"
        )
        if os.path.exists(vscode_config):
            return {
                "name": "GitHub Copilot",
                "source": "vscode",
                "type": "copilot",
                "status": "installed",
                "path": vscode_config
            }
    except Exception:
        pass
    return None


def detect_gemini() -> Optional[Dict]:
    """Detect Google Gemini (if running locally or API configured)."""
    try:
        # Check for Google AI Studio or local Gemini service
        procs = list_processes()
        for p in procs:
            name = (p.get("image") or "").lower()
            if "gemini" in name or "google" in name:
                return {
                    "name": "Google Gemini",
                    "source": "service",
                    "type": "gemini",
                    "status": "available",
                    "note": "Check Google AI Studio or local instance"
                }
        
        return {
            "name": "Google Gemini",
            "source": "web",
            "type": "gemini",
            "status": "available",
            "endpoint": "https://makersuite.google.com/app/apikey",
            "note": "Requires API key configuration"
        }
    except Exception:
        pass
    return None


def detect_chatgpt() -> Optional[Dict]:
    """Detect OpenAI ChatGPT or local OpenAI service."""
    try:
        # Check for local OpenAI service
        procs = list_processes()
        for p in procs:
            name = (p.get("image") or "").lower()
            if "openai" in name or "chatgpt" in name:
                return {
                    "name": "OpenAI ChatGPT",
                    "source": "service",
                    "type": "chatgpt",
                    "status": "available"
                }
        
        # Check for LM Studio or similar that can run ChatGPT models
        if which("lm-studio") or which("lm-studio-cli"):
            return {
                "name": "OpenAI ChatGPT (via LM Studio)",
                "source": "local",
                "type": "chatgpt",
                "status": "available"
            }
        
        return {
            "name": "OpenAI ChatGPT",
            "source": "web",
            "type": "chatgpt",
            "status": "available",
            "endpoint": "https://chat.openai.com",
            "note": "Requires API key or web login"
        }
    except Exception:
        pass
    return None


def detect_grok() -> Optional[Dict]:
    """Detect xAI Grok (typically web-based)."""
    try:
        return {
            "name": "xAI Grok",
            "source": "web",
            "type": "grok",
            "status": "available",
            "endpoint": "https://grok.x.ai",
            "note": "Requires API key or X/Twitter account"
        }
    except Exception:
        pass
    return None


def get_opensource_llms() -> List[Dict]:
    """Suggest open-source LLMs available for download."""
    return [
        {
            "name": "llama-2-7b",
            "source": "huggingface",
            "type": "opensource",
            "status": "available_for_download",
            "url": "https://huggingface.co/meta-llama/Llama-2-7b-hf"
        },
        {
            "name": "mistral-7b",
            "source": "huggingface",
            "type": "opensource",
            "status": "available_for_download",
            "url": "https://huggingface.co/mistralai/Mistral-7B-v0.1"
        },
        {
            "name": "neural-chat-7b",
            "source": "huggingface",
            "type": "opensource",
            "status": "available_for_download",
            "url": "https://huggingface.co/Intel/neural-chat-7b-v3-1"
        },
    ]


def build_llm_pool() -> List[Dict]:
    """Build the LLM pool from all local discoveries."""
    pool = []

    # 1) CLI tools on PATH
    pool.extend(detect_clis())

    # 2) Running local services on common ports
    pool.extend(detect_running_services())

    # 3) Local model files
    pool.extend(discover_local_llms())

    # 4) Running processes that look like LLM services
    procs = list_processes()
    for p in procs:
        name = (p.get("image") or "").lower()
        if any(k in name for k in LLM_PROCESS_KEYWORDS):
            pool.append({
                "name": name,
                "pid": p.get("pid"),
                "source": "process",
                "status": "running"
            })

    # 5) Specific AI assistants
    copilot = detect_copilot()
    if copilot:
        pool.append(copilot)
    
    gemini = detect_gemini()
    if gemini:
        pool.append(gemini)
    
    chatgpt = detect_chatgpt()
    if chatgpt:
        pool.append(chatgpt)
    
    grok = detect_grok()
    if grok:
        pool.append(grok)

    # Remove duplicates by (name, path/pid/port)
    unique = []
    seen = set()
    for item in pool:
        key = (
            item.get("name"),
            item.get("path") or item.get("pid") or item.get("port") or item.get("endpoint")
        )
        if key in seen:
            continue
        seen.add(key)
        unique.append(item)

    if unique:
        return unique
    # Fallback to open source suggestions
    return get_opensource_llms()


def get_llm_priority_score(item: Dict) -> int:
    """Score LLM by quality/priority. Higher = better. Used for auto-selection.
    
    Scoring hierarchy:
    - Cloud services (Copilot, Gemini, ChatGPT, Grok): 100-150 (best)
    - Local CLIs (Ollama, Llama): 50-65 (good)
    - Running processes: 30 (ok)
    - Local model files: 20 (acceptable)
    """
    score = 0
    name = (item.get("name") or "").lower()
    source = (item.get("source") or "").lower()
    
    # Cloud services (best for operations): +100
    if source in ["vscode", "service", "web"]:
        score += 100
        # Copilot (VS Code) is excellent: +50
        if "copilot" in name:
            score += 50
        # GPT-4 variants: +30
        elif "gpt-4" in name or "gpt4" in name:
            score += 30
        # Gemini/ChatGPT/Grok: +20
        elif any(x in name for x in ["gemini", "chatgpt", "grok", "claude"]):
            score += 20
    # Local CLIs (good): +50
    elif source == "cli":
        score += 50
        # Ollama and ollama-powered are solid: +15
        if "ollama" in name:
            score += 15
        # Llama-based: +10
        elif "llama" in name:
            score += 10
    # Running processes: +30
    elif source == "process":
        score += 30
    # Local model files: +20
    elif source == "local":
        score += 20
    
    # Penalize unavailable/disabled: -100
    status = (item.get("status") or "").lower()
    if status not in ["available", "running", ""]:
        score -= 100
    
    return max(0, score)


def build_llm_report() -> Dict:
    """Return a comprehensive report of available LLMs and services."""
    critical = set(get_critical_system_models())
    available: List[Dict[str, Any]] = []
    excluded: List[Dict[str, Any]] = []

    # Check CLIs
    for name, binname in KNOWN_CLI_CANDIDATES:
        p = which(binname)
        if p:
            if name in critical or any(c in name for c in critical):
                excluded.append({"name": name, "path": p, "reason": "critical"})
            else:
                available.append({"name": name, "path": p, "source": "cli", "status": "available"})

    # Check running services
    for item in detect_running_services():
        available.append(item)

    # Local models
    for item in discover_local_llms():
        nm = item.get("name", "").lower()
        if nm in critical or any(c in nm for c in critical):
            excluded.append({"name": str(item.get("name") or ""), "path": str(item.get("path") or ""), "reason": "critical"})
        else:
            available.append(item)

    # Running processes
    for proc in list_processes():
        nm = (proc.get("image") or "").lower()
        entry = {"name": nm, "pid": proc.get("pid"), "source": "process", "status": "running"}
        if any(c in nm for c in critical):
            excluded.append({"name": nm, "pid": proc.get("pid"), "reason": "critical_process"})
        elif any(k in nm for k in LLM_PROCESS_KEYWORDS):
            available.append(entry)

    # Specific AI assistants
    for detector in [detect_copilot, detect_gemini, detect_chatgpt, detect_grok]:
        result = detector()
        if result:
            available.append(result)

    # Deduplicate
    def uniq_list(items, key_fields):
        seen = set()
        out = []
        for it in items:
            key = tuple(it.get(k) for k in key_fields)
            if key in seen:
                continue
            seen.add(key)
            out.append(it)
        return out

    available = uniq_list(available, ("name", "path", "pid", "port", "endpoint"))
    excluded = uniq_list(excluded, ("name", "path", "pid"))
    
    # Score and sort available LLMs by priority (best first)
    for item in available:
        item["priority_score"] = get_llm_priority_score(item)
    available.sort(key=lambda x: x.get("priority_score", 0), reverse=True)

    if available:
        # Provider signup hints (augment each item with quick signup/help info)
        for item in available:
            name_low = (item.get("name") or "").lower()
            if "copilot" in name_low:
                item.setdefault("signup_hint", "Enable GitHub Copilot in VS Code (GitHub account required)")
                item.setdefault("quick_link", "https://github.com/features/copilot")
            elif "gemini" in name_low:
                item.setdefault("signup_hint", "Get an API key at Google AI Studio")
                item.setdefault("quick_link", "https://makersuite.google.com/app/apikey")
            elif "chatgpt" in name_low or "openai" in name_low or "gpt" in name_low:
                item.setdefault("signup_hint", "Create OpenAI key in dashboard (Billing may be required)")
                item.setdefault("quick_link", "https://platform.openai.com/account/api-keys")
            elif "grok" in name_low:
                item.setdefault("signup_hint", "Apply for xAI API access; requires X account")
                item.setdefault("quick_link", "https://x.ai")
            elif "claude" in name_low or "anthropic" in name_low:
                item.setdefault("signup_hint", "Generate an Anthropic key in console")
                item.setdefault("quick_link", "https://console.anthropic.com")
            elif item.get("source") == "cli" and "ollama" in name_low:
                item.setdefault("signup_hint", "Install Ollama locally; no API key needed")
                item.setdefault("quick_link", "https://ollama.ai")
        return {"available": available, "excluded": excluded}
    # Fallback suggestions
    suggestions = get_opensource_llms()
    for s in suggestions:
        if "huggingface" in s.get("source","") or s.get("url"):
            s.setdefault("signup_hint", "Create free Hugging Face account to download model")
            s.setdefault("quick_link", s.get("url"))
    return {"available": suggestions, "excluded": excluded}


def get_best_llms_for_operations(count: int = 3) -> List[Dict]:
    """Return the top N best LLMs for use in operations, auto-selected by quality.
    
    This is used by the frontend to automatically populate operation slots
    with the best available options without user intervention.
    """
    report = build_llm_report()
    available = report.get("available", [])
    
    # Already sorted by priority score in build_llm_report, just take top N
    return available[:count]


if __name__ == "__main__":
    print("Scanning for LLM pool...")
    pool = build_llm_pool()
    print(f"\nFound {len(pool)} LLM(s):\n")
    for p in pool:
        print(json.dumps(p, indent=2))
    
    print("\n" + "="*60)
    print("Full Report:")
    print("="*60)
    report = build_llm_report()
    print(json.dumps(report, indent=2))
