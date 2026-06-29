<div align="center">

# 🚀 BURO

### API Connection Tester

**Verify connectivity to 28+ AI providers from your terminal.**

[![Python](https://img.shields.io/badge/Python-3.8+-blue?logo=python&logoColor=white)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Version](https://img.shields.io/badge/Version-2.0.0-purple.svg)]()
[![Platform](https://img.shields.io/badge/Platform-Win%20%7C%20macOS%20%7C%20Linux-orange.svg)]()
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://github.com/your-username/buro/pulls)

<br>

```
╔══════════════════════════════════════════════╗
║           BURO  —  Connection Tester         ║
║              v2.0.0                           ║
╚══════════════════════════════════════════════╝
```

</div>

---

## ✨ Features

- 🌐 **28 Providers** — OpenAI, Anthropic, Azure, Bedrock, and 24 more in one tool
- 📊 **Smart Diagnostics** — auto-interprets HTTP status codes with human-readable descriptions
- 🔑 **Rate Limit Display** — shows remaining request/token quotas from response headers
- 💬 **Model Reply Preview** — displays actual model response on successful connection
- ⚡ **Zero Config** — sensible defaults pre-filled for each provider
- 🔧 **Extensible** — add new providers in one line of code
- 🖥️ **Cross-Platform** — Windows, macOS, Linux

---

## 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/your-username/buro.git
cd buro

# Install dependencies
pip install -r requirements.txt

# Run
python buro.py
```

> 💡 For AWS Bedrock support, also install: `pip install boto3`

---

## 📋 Supported Providers

<table>
<tr>
<td valign="top" width="50%">

### 🔵 OpenAI-Compatible
| Provider | Default Model |
|----------|---------------|
| **OpenAI** | `gpt-4o-mini` |
| **OpenRouter** | `openai/gpt-4o-mini` |
| **Deepseek** | `deepseek-chat` |
| **Google AI Studio** | `gemini-2.0-flash` |
| **xAI** | `grok-2-latest` |
| **Qwen Cloud** | `qwen-plus` |
| **Kimi (Moonshot)** | `moonshot-v1-8k` |
| **NVIDIA NIM** | `llama-3.1-8b-instruct` |
| **NovitaAI** | `llama-3.1-8b-instruct` |
| **StepFun** | `step-1-8k` |
| **MiniMax** | `abab6.5s-chat` |
| **Hugging Face** | *(enter manually)* |
| **Alibaba Cloud** | `qwen-plus` |
| **Z.AI** | `glm-4.5` |
| **Arcee AI** | `auto` |
| **GMI Cloud** | *(enter manually)* |
| **Mixture** | *(enter manually)* |
| **Xiaomi MiMo** | *(enter manually)* |
| **Tencent TokenHub** | *(enter manually)* |
| **Kilo Code** | *(enter manually)* |
| **Opencode** | *(enter manually)* |

</td>
<td valign="top" width="50%">

### 🟢 Other Protocols
| Provider | Protocol |
|----------|----------|
| **Anthropic** | Anthropic Messages API |
| **GitHub Copilot** | Copilot Protocol |
| **AWS Bedrock** | Bedrock Converse API |
| **Azure Foundry** | Azure OpenAI Service |

### 🟡 Local / Self-Hosted
| Provider | Default Endpoint |
|----------|-----------------|
| **Ollama** | `localhost:11434` |
| **LM Studio** | `localhost:1234` |

### ⚙️ Custom
| Provider | Notes |
|----------|-------|
| **Custom Endpoint** | Any OpenAI-compatible API |

</td>
</tr>
</table>

---

## 🖼️ Usage

### Main Menu

```
  Select a provider to test:

     1 │ OpenAI                 15 │ Deepseek
     2 │ Anthropic              16 │ Z.AI
     3 │ OpenRouter             17 │ Kimi (Moonshot)
     4 │ Mixture                18 │ StepFun
     5 │ NovitaAI               19 │ MiniMax
     6 │ LM Studio              20 │ Ollama
     7 │ Qwen Cloud             21 │ Arcee AI
     8 │ xAI                    22 │ GMI Cloud
     9 │ Xiaomi MiMo            23 │ Kilo Code
    10 │ Tencent TokenHub       24 │ Opencode
    11 │ NVIDIA NIM             25 │ AWS Bedrock
    12 │ GitHub Copilot         26 │ Azure Foundry
    13 │ Hugging Face           27 │ Alibaba Cloud
    14 │ Google AI Studio       28 │ Custom Endpoint

     0 │ Exit           a │ About
```

### Successful Connection

```
  ━━━  OpenAI Connection Test  ━━━

  > Base URL [https://api.openai.com/v1]:
  > API Key: sk-***
  > Model name [gpt-4o-mini]:

  → POST https://api.openai.com/v1/chat/completions  (model=gpt-4o-mini)
  ──────────────────────────────────────────────────

  HTTP Status : ✔ OK — Request succeeded
  Status Code : 200
  Requests left: 4998

  ✔ Connection successful!
  Model reply : "Buro"
  Tokens used : prompt=12, completion=2, total=14
```

### Error Handling

```
  HTTP Status : ⚠ Unauthorized — Invalid or missing API key
  Status Code : 401

  ✖ Request failed.
  Error type  : authentication_error
  Message     : Invalid API key provided: sk-***
```

---

## 📁 Project Structure

```
buro/
├── buro.py              # Main CLI application
├── requirements.txt     # Python dependencies
├── README.md            # This file
└── LICENSE              # MIT License
```

---

## 🛠️ Architecture

```
┌──────────────┐
│   Main Menu  │
└──────┬───────┘
       │
       ▼
┌──────────────────────────────┐
│     Provider Registry        │
│  (name, url, type, key, model) │
└──────┬───────────────────────┘
       │
       ▼
┌──────────────────────────────┐
│     Test Dispatcher          │
├──────────┬───────────────────┤
│          │                   │
▼          ▼                   ▼
┌────────┐ ┌──────────┐ ┌──────────┐
│ OpenAI │ │Anthropic │ │  Azure   │
│ Family │ │ Messages │ │ OpenAI   │
├────────┤ ├──────────┤ ├──────────┤
│Copilot │ │ Bedrock  │ │ Custom   │
│protocol│ │ Converse │ │ endpoint │
└────┬───┘ └────┬─────┘ └────┬─────┘
     │          │             │
     ▼          ▼             ▼
┌──────────────────────────────────┐
│   Unified Response Handler       │
│  status · rate limits · reply    │
└──────────────────────────────────┘
```

---

## ⚙️ Requirements

| Dependency | Required | Notes |
|-----------|----------|-------|
| `requests` | ✅ Always | HTTP client |
| `boto3` | 🔶 Optional | Only for AWS Bedrock |

---

## 🤝 Contributing

Contributions are welcome! Here's how:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feat/add-provider`)
3. **Commit** your changes (`git commit -m "feat: add XYZ provider"`)
4. **Push** to the branch (`git push origin feat/add-provider`)
5. **Open** a Pull Request

### Adding a New Provider

In `buro.py`, append to the `PROVIDERS` list:

```python
("MyProvider", "https://api.example.com/v1", "openai", True, "default-model")
#  name         base_url                      type     key?  default_model
```

That's it. One line. 🎉

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

<div align="center">

**Built with ❤️ for developers who test before they deploy.**

[⬆ Back to Top](#-buro)

</div>
