from __future__ import annotations
import json
import os
import time
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any

@dataclass
class StepResult:
    name: str
    status: str
    output: Any = None
    error: str | None = None
    attempts: int = 1

class Engine:
    def __init__(self):
        self.base_url = os.getenv("LLM_BASE_URL", "http://localhost:11434/v1")
        self.api_key = os.getenv("LLM_API_KEY", "ollama")
        self.model = os.getenv("LLM_MODEL", "qwen3:14b")
        self.mock = os.getenv("LLM_MOCK", "true").lower() == "true"

    def render(self, template: str, ctx: dict) -> str:
        out = template
        for key, value in ctx.items():
            if isinstance(value, (str, int, float, bool)):
                out = out.replace("{{" + key + "}}", str(value))
        return out

    def llm(self, prompt: str) -> str:
        if self.mock:
            return f"[MOCK {self.model}] {prompt[:180]}"

        payload = json.dumps({
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.2,
        }).encode()

        req = urllib.request.Request(
            self.base_url.rstrip("/") + "/chat/completions",
            data=payload,
            method="POST",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
            },
        )

        with urllib.request.urlopen(req, timeout=45) as resp:
            body = json.load(resp)

        return body["choices"][0]["message"]["content"]

    def http_call(self, cfg: dict, ctx: dict) -> Any:
        url = self.render(cfg["url"], ctx)
        method = cfg.get("method", "POST").upper()
        body = cfg.get("body")
        data = None

        if body is not None:
            rendered = {
                k: self.render(str(v), ctx) for k, v in body.items()
            }
            data = json.dumps(rendered).encode()

        req = urllib.request.Request(
            url,
            data=data,
            method=method,
            headers={"Content-Type": "application/json"},
        )

        with urllib.request.urlopen(req, timeout=15) as resp:
            raw = resp.read().decode()
            try:
                return json.loads(raw)
            except Exception:
                return raw

    def execute_step(self, step: dict, ctx: dict):
        kind = step["type"]

        if kind == "template":
            return self.render(step["template"], ctx)

        if kind == "classify":
            source = str(ctx.get(step["field"], "")).lower()
            for rule in step["rules"]:
                if any(word.lower() in source for word in rule["contains"]):
                    return rule["label"]
            return step.get("default", "other")

        if kind == "llm":
            return self.llm(self.render(step["prompt"], ctx))

        if kind == "delay":
            time.sleep(float(step.get("seconds", 0)))
            return "ok"

        if kind == "http":
            return self.http_call(step, ctx)

        if kind == "output":
            return self.render(step["template"], ctx)

        raise ValueError(f"Unknown step type: {kind}")

    def run(self, workflow: dict, payload: dict) -> dict:
        ctx = dict(payload)
        trace = []

        for step in workflow["steps"]:
            retries = int(step.get("retries", 0))
            last_error = None

            for attempt in range(1, retries + 2):
                try:
                    output = self.execute_step(step, ctx)
                    ctx[step["name"]] = output
                    trace.append(StepResult(
                        name=step["name"],
                        status="ok",
                        output=output,
                        attempts=attempt,
                    ).__dict__)
                    break
                except Exception as exc:
                    last_error = exc
                    if attempt <= retries:
                        time.sleep(min(attempt, 3))
                    else:
                        trace.append(StepResult(
                            name=step["name"],
                            status="failed",
                            error=str(exc),
                            attempts=attempt,
                        ).__dict__)
                        if not step.get("continue_on_error", False):
                            return {"ok": False, "context": ctx, "trace": trace}

        return {"ok": True, "context": ctx, "trace": trace}

def load_json(path: str) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))
