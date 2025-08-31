from __future__ import annotations

import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict

# --------- Run context (simple global dict) ---------
class _RunContext:
    _data: Dict[str, Any] = {}

    def set(self, d: Dict[str, Any]) -> None:
        self._data.update(d)

    def get(self) -> Dict[str, Any]:
        return dict(self._data)

CTX = _RunContext()

# --------- LoggerAdapter that injects CTX into extra ---------
class CtxAdapter(logging.LoggerAdapter):
    def process(self, msg, kwargs):
        extra = kwargs.get("extra", {}) or {}
        # merge global context
        merged = {**CTX.get(), **extra}
        kwargs["extra"] = merged
        return msg, kwargs

# --------- formatters ---------
class _PlainFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        base = super().format(record)
        # if dict-like extra exists, append as key=val JSON-ish
        extra = getattr(record, "__dict__", {})
        # Logging internals occupy many keys; pick only what we injected
        ctx_keys = set(CTX.get().keys())
        payload = {k: extra.get(k) for k in ctx_keys if k in extra}
        if payload:
            return f"{base} | {payload}"
        return base

class _JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        ctx = CTX.get()
        out = {
            "ts": self.formatTime(record, datefmt="%Y-%m-%d %H:%M:%S"),
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
            **ctx,
        }
        # include any explicit extras the caller passed
        for k, v in record.__dict__.items():
            if k not in out and k not in logging.LogRecord(None, None, "", 0, "", (), None).__dict__:
                out[k] = v
        return json.dumps(out, ensure_ascii=False)

# --------- handlers / factories ---------
def _ensure_dir(p: Path) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)

def _base_logger(name: str) -> logging.Logger:
    lg = logging.getLogger(name)
    lg.setLevel(logging.INFO)
    lg.propagate = False
    return lg

def get_console_logger(name: str = "app") -> logging.Logger:
    lg = _base_logger(name)
    if not lg.handlers:
        h = logging.StreamHandler(sys.stdout)
        h.setFormatter(_PlainFormatter("[%(asctime)s] %(levelname)s | %(name)s | %(message)s"))
        lg.addHandler(h)
    return lg

def get_file_logger(name: str = "app", log_filename: str = "app.log", base_dir: str = "logs") -> logging.Logger:
    lg = _base_logger(name)
    if not lg.handlers:
        path = Path(base_dir) / log_filename
        _ensure_dir(path)
        h = logging.FileHandler(path, encoding="utf-8")
        h.setFormatter(_PlainFormatter("[%(asctime)s] %(levelname)s | %(name)s | %(message)s"))
        lg.addHandler(h)
    return lg

def get_json_logger(name: str = "app", log_filename: str = "app.jsonl", base_dir: str = "logs") -> logging.Logger:
    lg = _base_logger(name)
    if not lg.handlers:
        path = Path(base_dir) / log_filename
        _ensure_dir(path)
        h = logging.FileHandler(path, encoding="utf-8")
        h.setFormatter(_JsonFormatter())
        lg.addHandler(h)
    return lg
