#!/usr/bin/env python3
"""
BURO — API Connection Tester
CLI tool for verifying connectivity to OpenAI and Anthropic APIs.
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
VERSION = "1.0.0"
TIMEOUT = 30  # seconds

HTTP_MESSAGES = {
    200: "OK — Request succeeded",
    201: "Created — Resource created successfully",
    400: "Bad Request — Invalid parameters or payload",
    401: "Unauthorized — Invalid or missing API key",
    403: "Forbidden — Insufficient permissions",
    404: "Not Found — Endpoint does not exist",
    422: "Unprocessable Entity — Validation error",
    429: "Rate Limited — Too many requests, slow down",
    500: "Internal Server Error — Provider-side failure",
    502: "Bad Gateway — Upstream server error",
    503: "Service Unavailable — API is temporarily down",
    529: "Overloaded — Provider is at capacity",
}

RESET = "\033[0m"
BOLD  = "\033[1m"
GREEN = "\033[92m"
RED   = "\033[91m"
CYAN  = "\033[96m"
YELLOW = "\033[93m"
DIM   = "\033[2m"

# ── Helpers ───────────────────────────────────────────────────────────────────

def banner():
    print(f"""
{CYAN}{BOLD}╔══════════════════════════════════════════════╗
║           BURO  —  Connection Tester         ║
║              v{VERSION}  ({platform.system()}){' ' * (23 - len(platform.system()))}║
╚══════════════════════════════════════════════╝{RESET}
""")


def prompt(label: str, default: str = "") -> str:
    suffix = f" [{default}]" if default else ""
    val = input(f"  {CYAN}>{RESET} {label}{suffix}: ").strip()
    return val if val else default


def status_label(code: int) -> str:
    if code in HTTP_MESSAGES:
        msg = HTTP_MESSAGES[code]
    else:
        msg = f"HTTP {code}"
    if 200 <= code < 300:
        return f"{GREEN}✔ {msg}{RESET}"
    elif 400 <= code < 500:
        return f"{YELLOW}⚠ {msg}{RESET}"
    else:
        return f"{RED}✖ {msg}{RESET}"


def print_divider():
    print(f"{DIM}{'─' * 50}{RESET}")


def print_json(data, indent=2):
    """Pretty-print JSON with truncation for large responses."""
    text = json.dumps(data, indent=indent, ensure_ascii=False)
    lines = text.split("\n")
    if len(lines) > 40:
        print("\n".join(lines[:40]))
        print(f"{DIM}  ... ({len(lines) - 40} more lines truncated){RESET}")
    else:
        print(text)


# ── OpenAI Test ───────────────────────────────────────────────────────────────

def test_openai():
    print(f"\n{BOLD}━━━  OpenAI Connection Test  ━━━{RESET}\n")

    base_url = prompt("Base URL", "https://api.openai.com/v1")
    api_key  = prompt("API Key (sk-...)")
    model    = prompt("Model name", "gpt-4o-mini")

    if not api_key:
        print(f"\n  {RED}✖ API key is required.{RESET}")
        return

    # Ensure base_url ends cleanly
    base_url = base_url.rstrip("/")
    url = f"{base_url}/chat/completions"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": "Say 'buro' in one word."}],
        "max_tokens": 10,
        "temperature": 0,
    }

    print(f"\n  {DIM}→ Sending test request to:{RESET} {url}")
    print(f"  {DIM}→ Model:{RESET} {model}")
    print_divider()

    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=TIMEOUT)
    except requests.exceptions.ConnectionError as e:
        print(f"\n  {RED}✖ Connection failed — cannot reach host.{RESET}")
        print(f"    {DIM}{e}{RESET}")
        return
    except requests.exceptions.Timeout:
        print(f"\n  {RED}✖ Request timed out after {TIMEOUT}s.{RESET}")
        return
    except requests.exceptions.RequestException as e:
        print(f"\n  {RED}✖ Request error:{RESET} {e}")
        return

    code = resp.status_code
    print(f"\n  HTTP Status : {status_label(code)}")
    print(f"  Status Code : {BOLD}{code}{RESET}")

    # Response headers of interest
    rate_limit = resp.headers.get("x-ratelimit-remaining-requests", "")
    if rate_limit:
        print(f"  Rate Limit  : {rate_limit} requests remaining")

    try:
        body = resp.json()
    except json.JSONDecodeError:
        body = {"raw": resp.text[:500]}

    if code == 200:
        print(f"\n  {GREEN}✔ Connection successful!{RESET}")
        if "choices" in body and body["choices"]:
            reply = body["choices"][0].get("message", {}).get("content", "")
            print(f"  Model reply : \"{reply.strip()}\"")
        usage = body.get("usage", {})
        if usage:
            print(f"  Tokens used : prompt={usage.get('prompt_tokens','?')}, "
                  f"completion={usage.get('completion_tokens','?')}, "
                  f"total={usage.get('total_tokens','?')}")
    else:
        print(f"\n  {RED}✖ Request failed.{RESET}")
        error = body.get("error", body)
        if isinstance(error, dict):
            print(f"  Error type  : {error.get('type', 'unknown')}")
            print(f"  Message     : {error.get('message', 'No message')}")
        else:
            print(f"  Response    :")
            print_json(body)


# ── Anthropic Test ────────────────────────────────────────────────────────────

def test_anthropic():
    print(f"\n{BOLD}━━━  Anthropic Connection Test  ━━━{RESET}\n")

    base_url = prompt("Base URL", "https://api.anthropic.com/v1")
    api_key  = prompt("API Key (sk-ant-...)")
    model    = prompt("Model name", "claude-sonnet-4-20250514")

    if not api_key:
        print(f"\n  {RED}✖ API key is required.{RESET}")
        return

    base_url = base_url.rstrip("/")
    url = f"{base_url}/messages"

    headers = {
        "Content-Type": "application/json",
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
    }
    payload = {
        "model": model,
        "max_tokens": 10,
        "messages": [{"role": "user", "content": "Say 'buro' in one word."}],
    }

    print(f"\n  {DIM}→ Sending test request to:{RESET} {url}")
    print(f"  {DIM}→ Model:{RESET} {model}")
    print_divider()

    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=TIMEOUT)
    except requests.exceptions.ConnectionError as e:
        print(f"\n  {RED}✖ Connection failed — cannot reach host.{RESET}")
        print(f"    {DIM}{e}{RESET}")
        return
    except requests.exceptions.Timeout:
        print(f"\n  {RED}✖ Request timed out after {TIMEOUT}s.{RESET}")
        return
    except requests.exceptions.RequestException as e:
        print(f"\n  {RED}✖ Request error:{RESET} {e}")
        return

    code = resp.status_code
    print(f"\n  HTTP Status : {status_label(code)}")
    print(f"  Status Code : {BOLD}{code}{RESET}")

    # Anthropic rate limit headers
    rl_req  = resp.headers.get("anthropic-ratelimit-requests-remaining", "")
    rl_tok  = resp.headers.get("anthropic-ratelimit-tokens-remaining", "")
    if rl_req:
        print(f"  Rate Limit  : {rl_req} requests remaining")
    if rl_tok:
        print(f"  Token Limit : {rl_tok} tokens remaining")

    try:
        body = resp.json()
    except json.JSONDecodeError:
        body = {"raw": resp.text[:500]}

    if code == 200:
        print(f"\n  {GREEN}✔ Connection successful!{RESET}")
        if "content" in body and body["content"]:
            reply = body["content"][0].get("text", "")
            print(f"  Model reply : \"{reply.strip()}\"")
        stop = body.get("stop_reason", "")
        if stop:
            print(f"  Stop reason : {stop}")
        usage = body.get("usage", {})
        if usage:
            print(f"  Tokens used : input={usage.get('input_tokens','?')}, "
                  f"output={usage.get('output_tokens','?')}")
    else:
        print(f"\n  {RED}✖ Request failed.{RESET}")
        error = body.get("error", body)
        if isinstance(error, dict):
            print(f"  Error type  : {error.get('type', 'unknown')}")
            print(f"  Message     : {error.get('message', 'No message')}")
        else:
            print(f"  Response    :")
            print_json(body)


# ── Main Menu ─────────────────────────────────────────────────────────────────

def main():
    banner()

    while True:
        print(f"  {BOLD}Select an option:{RESET}\n")
        print(f"    {CYAN}1{RESET} │ Test OpenAI connection")
        print(f"    {CYAN}2{RESET} │ Test Anthropic connection")
        print(f"    {CYAN}3{RESET} │ About")
        print(f"    {CYAN}0{RESET} │ Exit\n")

        choice = prompt("Choice", "").strip()

        if choice == "1":
            test_openai()
        elif choice == "2":
            test_anthropic()
        elif choice == "3":
            print(f"""
  {BOLD}BURO{RESET} v{VERSION} — API Connection Tester
  Platform: {platform.system()} {platform.release()}
  Python  : {platform.python_version()}
  Checks  : HTTP status, rate limits, error diagnostics
  Author  : Built with ❤ for local OTA dev workflow
""")
        elif choice == "0" or choice.lower() in ("q", "quit", "exit"):
            print(f"\n  {DIM}Goodbye!{RESET}\n")
            break
        else:
            print(f"  {YELLOW}Invalid choice. Try 1, 2, 3, or 0.{RESET}")

        print_divider()
        print()


if __name__ == "__main__":
    main()
