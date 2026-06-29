# BURO — API Connection Tester

CLI tool to verify connectivity with **OpenAI** and **Anthropic** APIs.

## Quick Start

```bash
# Install dependency
pip install -r requirements.txt

# Run
python buro.py
```

## Features

| Feature | Description |
|---------|-------------|
| OpenAI Test | Tests `/chat/completions` with custom base URL, API key, model |
| Anthropic Test | Tests `/messages` with custom endpoint, API key, model |
| Status Codes | Auto-interprets HTTP 200, 400, 401, 403, 404, 422, 429, 500, 502, 503, 529 |
| Error Diagnostics | Displays API error type + message for quick debugging |
| Rate Limits | Shows remaining request/token quotas from response headers |
| Cross-Platform | Runs on Windows, macOS, Linux via Python 3.8+ |

## Menu

```
1 │ Test OpenAI connection
2 │ Test Anthropic connection
3 │ About
0 │ Exit
```

## Requirements

- Python 3.8+
- `requests` library

## License

Free to use.
