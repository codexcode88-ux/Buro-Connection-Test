#!/usr/bin/env python3
"""
BURO — API Connection Tester
CLI tool for verifying connectivity to multiple AI API providers.
"""

import sys
import json
import platform

try:
    import requests
except ImportError:
    print("[!] 'requests' not found. Install it:  pip install requests")
    sys.exit(1)

# ── Constants ─────────────────────────────────────────────────────────────────
VERSION = "2.0.0"
TIMEOUT = 30  # seconds

HTTP_MESSAGES = {
    200: "OK — Request succeeded",
    201: "Created — Resource created successfully",
    400: "Bad Request — Invalid parameters or payload",
    401: "Unauthorized — Invalid or missing API key",
    403: "Forbidden — Insufficient permissions",
    404: "Not Found — Endpoint/model does not exist",
    422: "Unprocessable Entity — Validation error",
    429: "Rate Limited — Too many requests, slow down",
    500: "Internal Server Error — Provider-side failure",
    502: "Bad Gateway — Upstream server error",
    503: "Service Unavailable — API is temporarily down",
    529: "Overloaded — Provider is at capacity",
}

RESET, BOLD, DIM = "\033[0m", "\033[1m", "\033[2m"
GREEN, RED, CYAN, YELLOW = "\033[92m", "\033[91m", "\033[96m", "\033[93m"

# ── Provider registry ───────────────────────────────────────────────────────
# type:  openai | anthropic | azure | bedrock | copilot
# url:   default base URL ("" = user must enter)
# key:   True if API key required
# model: default model name ("" = user must enter)
PROVIDERS = [
    # name,                base_url,                                              type,        key,   model
    ("OpenAI",            "https://api.openai.com/v1",                            "openai",    True,  "gpt-4o-mini"),
    ("Anthropic",         "https://api.anthropic.com/v1",                         "anthropic", True,  "claude-sonnet-4-20250514"),
    ("OpenRouter",        "https://openrouter.ai/api/v1",                         "openai",    True,  "openai/gpt-4o-mini"),
    ("Mixture",           "",                                                     "openai",    True,  ""),
    ("NovitaAI",          "https://api.novita.ai/v3/openai",                      "openai",    True,  "meta-llama/llama-3.1-8b-instruct"),
    ("LM Studio",         "http://localhost:1234/v1",                             "openai",    False, ""),
    ("Qwen Cloud",        "https://dashscope.aliyuncs.com/compatible-mode/v1",    "openai",    True,  "qwen-plus"),
    ("xAI",               "https://api.x.ai/v1",                                  "openai",    True,  "grok-2-latest"),
    ("Xiaomi MiMo",       "",                                                     "openai",    True,  ""),
    ("Tencent TokenHub",  "",                                                     "openai",    True,  ""),
    ("NVIDIA NIM",        "https://integrate.api.nvidia.com/v1",                  "openai",    True,  "meta/llama-3.1-8b-instruct"),
    ("GitHub Copilot",    "https://api.githubcopilot.com",                        "copilot",   True,  "gpt-4o"),
    ("Hugging Face",      "https://router.huggingface.co/v1",                     "openai",    True,  ""),
    ("Google AI Studio",  "https://generativelanguage.googleapis.com/v1beta/openai", "openai", True,  "gemini-2.0-flash"),
    ("Deepseek",          "https://api.deepseek.com/v1",                          "openai",    True,  "deepseek-chat"),
    ("Z.AI",              "https://api.z.ai/api/paas/v4",                         "openai",    True,  "glm-4.5"),
    ("Kimi (Moonshot)",   "https://api.moonshot.cn/v1",                           "openai",    True,  "moonshot-v1-8k"),
    ("StepFun",           "https://api.stepfun.com/v1",                           "openai",    True,  "step-1-8k"),
    ("MiniMax",           "https://api.minimax.chat/v1",                          "openai",    True,  "abab6.5s-chat"),
    ("Ollama",            "http://localhost:11434/v1",                            "openai",    False, "llama3.2"),
    ("Arcee AI",          "https://conductor.arcee.ai/v1",                        "openai",    True,  "auto"),
    ("GMI Cloud",         "https://api.gmi-serving.com/v1",                       "openai",    True,  ""),
    ("Kilo Code",         "",                                                     "openai",    True,  ""),
    ("Opencode",          "",                                                     "openai",    True,  ""),
    ("AWS Bedrock",       "",                                                     "bedrock",   True,  "anthropic.claude-3-5-sonnet-20241022-v2:0"),
    ("Azure Foundry",     "",                                                     "azure",     True,  ""),
    ("Alibaba Cloud",     "https://dashscope.aliyuncs.com/compatible-mode/v1",    "openai",    True,  "qwen-plus"),
    ("Custom Endpoint",   "",                                                     "openai",    True,  ""),
]

# ── Helpers ───────────────────────────────────────────────────────────────────

def banner():
    plat = platform.system()
    print(f"""
{CYAN}{BOLD}╔══════════════════════════════════════════════╗
║           BURO  —  Connection Tester         ║
║              v{VERSION}  ({plat}){' ' * max(0, 23 - len(plat))}║
╚══════════════════════════════════════════════╝{RESET}
""")


def prompt(label, default=""):
    suffix = f" [{default}]" if default else ""
    val = input(f"  {CYAN}>{RESET} {label}{suffix}: ").strip()
    return val if val else default


def status_label(code):
    msg = HTTP_MESSAGES.get(code, f"HTTP {code}")
    if 200 <= code < 300:
        return f"{GREEN}✔ {msg}{RESET}"
    if 400 <= code < 500:
        return f"{YELLOW}⚠ {msg}{RESET}"
    return f"{RED}✖ {msg}{RESET}"


def divider():
    print(f"{DIM}{'─' * 50}{RESET}")


def print_json(data, indent=2):
    text = json.dumps(data, indent=indent, ensure_ascii=False)
    lines = text.split("\n")
    if len(lines) > 40:
        print("\n".join(lines[:40]))
        print(f"{DIM}  ... ({len(lines) - 40} more lines truncated){RESET}")
    else:
        print(text)


def report_status(resp):
    code = resp.status_code
    print(f"\n  HTTP Status : {status_label(code)}")
    print(f"  Status Code : {BOLD}{code}{RESET}")
    return code


def show_rate_limits(headers):
    pairs = [
        ("x-ratelimit-remaining-requests", "Requests left"),
        ("x-ratelimit-remaining-tokens", "Tokens left"),
        ("anthropic-ratelimit-requests-remaining", "Requests left"),
        ("anthropic-ratelimit-tokens-remaining", "Tokens left"),
    ]
    for hkey, label in pairs:
        if hkey in headers:
            print(f"  {label:<12}: {headers[hkey]}")


def send(method_desc, fn):
    """Wrap a request call with unified network error handling."""
    print(f"\n  {DIM}→ {method_desc}{RESET}")
    divider()
    try:
        return fn(), None
    except requests.exceptions.ConnectionError as e:
        return None, f"{RED}✖ Connection failed — cannot reach host.{RESET}\n    {DIM}{e}{RESET}"
    except requests.exceptions.Timeout:
        return None, f"{RED}✖ Request timed out after {TIMEOUT}s.{RESET}"
    except requests.exceptions.RequestException as e:
        return None, f"{RED}✖ Request error:{RESET} {e}"


# ── Response parsers ──────────────────────────────────────────────────────────

def parse_openai_ok(body):
    if body.get("choices"):
        reply = body["choices"][0].get("message", {}).get("content", "")
        print(f"  Model reply : \"{(reply or '').strip()}\"")
    usage = body.get("usage", {})
    if usage:
        print(f"  Tokens used : prompt={usage.get('prompt_tokens','?')}, "
              f"completion={usage.get('completion_tokens','?')}, "
              f"total={usage.get('total_tokens','?')}")


def parse_anthropic_ok(body):
    if body.get("content"):
        print(f"  Model reply : \"{body['content'][0].get('text','').strip()}\"")
    if body.get("stop_reason"):
        print(f"  Stop reason : {body['stop_reason']}")
    usage = body.get("usage", {})
    if usage:
        print(f"  Tokens used : input={usage.get('input_tokens','?')}, "
              f"output={usage.get('output_tokens','?')}")


def show_error(body):
    print(f"\n  {RED}✖ Request failed.{RESET}")
    error = body.get("error", body) if isinstance(body, dict) else body
    if isinstance(error, dict):
        print(f"  Error type  : {error.get('type', error.get('code', 'unknown'))}")
        print(f"  Message     : {error.get('message', json.dumps(error)[:300])}")
    else:
        print("  Response    :")
        print_json(body)


# ── Test backends ─────────────────────────────────────────────────────────────

TEST_MSG = [{"role": "user", "content": "Say 'buro' in one word."}]


def test_openai_family(base_url, api_key, model, extra_headers=None):
    base_url = base_url.rstrip("/")
    url = f"{base_url}/chat/completions"
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    if extra_headers:
        headers.update(extra_headers)
    payload = {"model": model, "messages": TEST_MSG, "max_tokens": 16, "temperature": 0}

    resp, err = send(f"POST {url}  (model={model})",
                     lambda: requests.post(url, headers=headers, json=payload, timeout=TIMEOUT))
    if err:
        print(f"\n  {err}")
        return
    code = report_status(resp)
    show_rate_limits(resp.headers)
    try:
        body = resp.json()
    except json.JSONDecodeError:
        body = {"raw": resp.text[:500]}
    if code == 200:
        print(f"\n  {GREEN}✔ Connection successful!{RESET}")
        parse_openai_ok(body)
    else:
        show_error(body)


def test_anthropic(base_url, api_key, model):
    base_url = base_url.rstrip("/")
    url = f"{base_url}/messages"
    headers = {
        "Content-Type": "application/json",
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
    }
    payload = {"model": model, "max_tokens": 16, "messages": TEST_MSG}

    resp, err = send(f"POST {url}  (model={model})",
                     lambda: requests.post(url, headers=headers, json=payload, timeout=TIMEOUT))
    if err:
        print(f"\n  {err}")
        return
    code = report_status(resp)
    show_rate_limits(resp.headers)
    try:
        body = resp.json()
    except json.JSONDecodeError:
        body = {"raw": resp.text[:500]}
    if code == 200:
        print(f"\n  {GREEN}✔ Connection successful!{RESET}")
        parse_anthropic_ok(body)
    else:
        show_error(body)


def test_azure(base_url, api_key, model):
    # Azure: {endpoint}/openai/deployments/{deployment}/chat/completions?api-version=...
    api_version = prompt("API version", "2024-10-21")
    base_url = base_url.rstrip("/")
    url = f"{base_url}/openai/deployments/{model}/chat/completions?api-version={api_version}"
    headers = {"Content-Type": "application/json", "api-key": api_key}
    payload = {"messages": TEST_MSG, "max_tokens": 16, "temperature": 0}

    resp, err = send(f"POST {url}",
                     lambda: requests.post(url, headers=headers, json=payload, timeout=TIMEOUT))
    if err:
        print(f"\n  {err}")
        return
    code = report_status(resp)
    try:
        body = resp.json()
    except json.JSONDecodeError:
        body = {"raw": resp.text[:500]}
    if code == 200:
        print(f"\n  {GREEN}✔ Connection successful!{RESET}")
        parse_openai_ok(body)
    else:
        show_error(body)


def test_copilot(base_url, api_key, model):
    extra = {
        "Editor-Version": "vscode/1.90.0",
        "Copilot-Integration-Id": "vscode-chat",
    }
    test_openai_family(base_url, api_key, model, extra_headers=extra)


def test_bedrock(model):
    try:
        import boto3
        from botocore.exceptions import ClientError, BotoCoreError
    except ImportError:
        print(f"\n  {YELLOW}⚠ AWS Bedrock needs boto3.  Install:  pip install boto3{RESET}")
        return
    region   = prompt("AWS Region", "us-east-1")
    akid     = prompt("AWS Access Key ID")
    secret   = prompt("AWS Secret Access Key")
    if not (akid and secret):
        print(f"\n  {RED}✖ AWS credentials required.{RESET}")
        return
    print(f"\n  {DIM}→ Bedrock converse  (region={region}, model={model}){RESET}")
    divider()
    try:
        client = boto3.client(
            "bedrock-runtime", region_name=region,
            aws_access_key_id=akid, aws_secret_access_key=secret,
        )
        resp = client.converse(
            modelId=model,
            messages=[{"role": "user", "content": [{"text": "Say 'buro' in one word."}]}],
            inferenceConfig={"maxTokens": 16, "temperature": 0},
        )
        print(f"\n  {GREEN}✔ Connection successful!{RESET}")
        out = resp["output"]["message"]["content"][0]["text"]
        print(f"  Model reply : \"{out.strip()}\"")
        u = resp.get("usage", {})
        print(f"  Tokens used : input={u.get('inputTokens','?')}, output={u.get('outputTokens','?')}")
    except ClientError as e:
        print(f"\n  {RED}✖ Bedrock error.{RESET}")
        err = e.response.get("Error", {})
        print(f"  Code        : {err.get('Code','?')}")
        print(f"  Message     : {err.get('Message','?')}")
    except BotoCoreError as e:
        print(f"\n  {RED}✖ Bedrock connection error:{RESET} {e}")


# ── Dispatcher ────────────────────────────────────────────────────────────────

def run_test(prov):
    name, default_url, ptype, key_req, default_model = prov
    print(f"\n{BOLD}━━━  {name} Connection Test  ━━━{RESET}\n")

    if ptype == "bedrock":
        model = prompt("Model ID", default_model)
        if not model:
            print(f"\n  {RED}✖ Model ID required.{RESET}")
            return
        test_bedrock(model)
        return

    base_url = prompt("Base URL", default_url)
    if not base_url:
        print(f"\n  {RED}✖ Base URL required for {name}.{RESET}")
        return

    api_key = prompt("API Key")
    if key_req and not api_key:
        print(f"\n  {RED}✖ API key is required for {name}.{RESET}")
        return

    model = prompt("Model name" if ptype != "azure" else "Deployment name", default_model)
    if not model:
        print(f"\n  {RED}✖ Model/deployment name required.{RESET}")
        return

    if ptype == "openai":
        test_openai_family(base_url, api_key, model)
    elif ptype == "anthropic":
        test_anthropic(base_url, api_key, model)
    elif ptype == "azure":
        test_azure(base_url, api_key, model)
    elif ptype == "copilot":
        test_copilot(base_url, api_key, model)


# ── Menu ──────────────────────────────────────────────────────────────────────

def print_menu():
    print(f"  {BOLD}Select a provider to test:{RESET}\n")
    half = (len(PROVIDERS) + 1) // 2
    left = PROVIDERS[:half]
    right = PROVIDERS[half:]
    for i in range(half):
        ln = f"    {CYAN}{i+1:>2}{RESET} │ {left[i][0]:<20}"
        j = i + half
        if j < len(PROVIDERS):
            ln += f"   {CYAN}{j+1:>2}{RESET} │ {right[i][0]:<20}"
        print(ln)
    print(f"\n    {CYAN} 0{RESET} │ Exit          {CYAN} a{RESET} │ About\n")


def about():
    print(f"""
  {BOLD}BURO{RESET} v{VERSION} — Multi-provider API Connection Tester
  Platform  : {platform.system()} {platform.release()}
  Python    : {platform.python_version()}
  Providers : {len(PROVIDERS)} configured
  Backends  : OpenAI-compatible · Anthropic · Azure · Bedrock · Copilot
  Checks    : HTTP status, rate limits, model reply, error diagnostics
""")


def main():
    banner()
    while True:
        print_menu()
        choice = prompt("Choice").strip().lower()

        if choice in ("0", "q", "quit", "exit"):
            print(f"\n  {DIM}Goodbye!{RESET}\n")
            break
        if choice == "a":
            about()
        elif choice.isdigit() and 1 <= int(choice) <= len(PROVIDERS):
            run_test(PROVIDERS[int(choice) - 1])
        else:
            print(f"  {YELLOW}Invalid choice.{RESET}")

        divider()
        print()


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print(f"\n\n  {DIM}Interrupted. Goodbye!{RESET}\n")
