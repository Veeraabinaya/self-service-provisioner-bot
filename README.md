# 🤖 ProvisionBot — Self-Service Infrastructure Provisioner

> **Automate your DevOps workflow end-to-end: from developer request to GitHub PR in seconds.**

---

## 🚀 What Is ProvisionBot?

ProvisionBot is a **full-stack AI-powered DevOps automation platform** that lets developers provision infrastructure environments (Docker, AWS, Terraform) through a clean web UI — with zero manual DevOps intervention.

When a developer submits a request:
1. **AI parses the natural-language description** to detect environment type, services, and target env
2. **A policy engine validates** the request against organizational rules
3. **Infrastructure code is auto-generated** (docker-compose.yml or Terraform .tf files)
4. **A GitHub Issue is automatically created** labeled `auto-provision`
5. **A GitHub PR is opened** with the generated files, ready for DevOps review
6. **Email notifications** are sent to the requester and dev team throughout the lifecycle

---

## ✨ Key Features

| Feature | Description |
|---|---|
| 🧠 **AI-Powered NLP** | Parses free-text requests via Hugging Face LLM (Mistral-7B) with keyword fallback |
| 🏗️ **Infra Code Generation** | Auto-generates `docker-compose.yml` or Terraform (`main.tf`, `provider.tf`, `variables.tf`) |
| 🔒 **Policy Engine** | YAML-based governance — validates allowed environments, types, and service limits |
| 🔗 **GitHub Automation** | Creates labeled Issues and opens PRs with infra files on dedicated `provision/{id}` branches |
| 📧 **Email Notifications** | Notifies the dev team on submission and the requester on completion |
| 📊 **Request Tracker** | Live dashboard showing all requests with status, PR links, and issue links |
| 🛡️ **Mock Mode** | Fully functional without API keys — runs entirely offline for development/demos |

---

## 🏛️ Architecture

```
Developer (Browser)
       │
       ▼
  FastAPI Backend (app.py)
       │
       ├──► NLP Parser (parser.py)
       │         └── HuggingFace API → keyword fallback
       │
       ├──► Policy Engine (policy_engine/engine.py)
       │         └── policy.yaml (allowed envs, types, max services)
       │
       ├──► Infrastructure Generator (terraform_generator/generator.py)
       │         ├── Docker → docker-compose.yml
       │         └── AWS/Terraform → main.tf + provider.tf + variables.tf
       │
       ├──► GitHub Automation (automation/)
       │         ├── create_issue.py  → Issue with label auto-provision
       │         └── create_pr.py     → PR on branch provision/{id}
       │
       └──► SQLite DB (SQLAlchemy async) + Email (SMTP)
```

---

## 🛠️ Tech Stack

- **Backend:** Python 3.14, FastAPI, SQLAlchemy (async), aiosqlite
- **Frontend:** Vanilla JS, custom CSS, Jinja2 templates
- **AI/NLP:** Hugging Face Inference API (Mistral-7B-Instruct-v0.3)
- **GitHub:** PyGithub — automated issue/PR creation
- **Infrastructure Targets:** Docker Compose, Terraform (AWS)
- **CI/CD:** GitHub Actions (CI, deploy, auto-provision, apply_infra, PR automation)
- **Auth/Config:** python-dotenv, JWT, cryptography

---

## ⚡ Quick Start

### 1. Clone & Install

```bash
git clone https://github.com/your-username/ProvisionBot.git
cd ProvisionBot/provisioner-bot
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```env
# GitHub (optional — mock mode if omitted)
GITHUB_TOKEN=ghp_your_token
GITHUB_REPO=your-org/your-repo

# Hugging Face (optional — keyword fallback if omitted)
HF_API_KEY=hf_your_api_key
HF_MODEL=mistralai/Mistral-7B-Instruct-v0.3

# Email Notifications (optional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=you@gmail.com
SMTP_PASSWORD=your_app_password
SMTP_FROM=provisioner@yourcompany.com
DEV_TEAM_EMAIL=devteam@yourcompany.com
```

> 💡 **No keys? No problem.** ProvisionBot runs fully in mock mode — GitHub PRs/issues and emails are simulated with console logs.

### 3. Run the Server

```bash
uvicorn app:app --reload
```

Visit `http://localhost:8000` — the dashboard is live!

---

## 🔄 Supported Workflows

### Docker Environment
Submit a request like:
> *"Set up a Docker environment for dev with postgres and redis"*

ProvisionBot generates:
```yaml
# docker-compose.yml
version: "3.8"
services:
  postgres:
    image: postgres:15
    ...
  redis:
    image: redis:7-alpine
    ...
```

### AWS / Terraform Environment
Submit a request like:
> *"Need an AWS staging environment with Terraform"*

ProvisionBot generates:
```
generated/{id}/
├── provider.tf    # AWS provider + Terraform block
├── variables.tf   # region, env, instance_type
└── main.tf        # VPC + EC2 instance resources
```

---

## 📋 Policy Engine

Governance is enforced via `policy_engine/policy.yaml`:

```yaml
allowed_envs:
  - dev
  - qa
  - staging
  - prod
allowed_types:
  - docker
  - aws
  - terraform
max_services: 5
```

Requests violating these rules are rejected with a descriptive error before any code is generated.

---

## 🔀 GitHub Actions Workflows

| Workflow | Trigger | Purpose |
|---|---|---|
| `ci.yml` | Push / PR | Run tests with pytest |
| `deploy.yml` | Push to main | Deploy the FastAPI app |
| `auto_provision.yml` | Issue label `auto-provision` | Trigger provisioning pipeline |
| `apply_infra.yml` | PR merge | Apply generated Terraform / Docker configs |
| `pr_automation.yml` | PR events | Auto-label and comment on PRs |

---

## 🧪 Running Tests

```bash
cd provisioner-bot
pytest tests/ -v
```

Tests cover API endpoints (`/api/submit`, `/api/validate`, `/api/parse`) with mock data.

---

## 📁 Project Structure

```
ProvisionBot/
├── provisioner-bot/
│   ├── app.py                      # FastAPI application, all API routes
│   ├── parser.py                   # NLP + keyword request parser
│   ├── requirements.txt
│   ├── pytest.ini
│   ├── automation/
│   │   ├── create_issue.py         # GitHub Issue creation
│   │   ├── create_pr.py            # GitHub PR creation
│   │   └── handle_issue.py         # Issue event handler
│   ├── policy_engine/
│   │   ├── engine.py               # Policy validation logic
│   │   └── policy.yaml             # Governance rules
│   ├── terraform_generator/
│   │   └── generator.py            # Docker Compose + Terraform generator
│   ├── templates/
│   │   ├── index.html              # Main dashboard UI
│   │   └── requests.html           # Request tracker UI
│   ├── static/
│   │   ├── script.js               # Frontend JS (chat, form, tracker)
│   │   └── style.css               # Custom CSS
│   ├── generated/                  # Auto-generated infra files (git-kept)
│   ├── tests/
│   │   └── test_api.py             # API integration tests
│   └── .github/workflows/          # CI/CD pipelines
└── policy/
    ├── policy.yaml                 # Standalone policy config
    └── policy_engine.py            # Standalone policy module
```

---

## 🌐 API Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Dashboard UI |
| `GET` | `/requests` | Request Tracker UI |
| `GET` | `/api/requests` | List all provision requests (JSON) |
| `POST` | `/api/submit` | Submit a new provision request |
| `POST` | `/api/validate` | Validate against policy (dry-run) |
| `POST` | `/api/parse` | Parse natural language request |
| `POST` | `/api/chat` | Chat with Provisioner AI |
| `POST` | `/api/complete/{id}` | Mark request as completed + notify requester |
| `GET` | `/api/status` | Check API key/integration status |

---

## 👥 Team

| # | Name |
|---|---|
| 1 | Janani Sandhiya T |
| 2 | Jeshintha X |
| 3 | Veera Abinaya M |
| 4 | Ya Khaiyum A |

Built with ❤️ as a full-stack DevOps automation project demonstrating:
- **Async Python** backend with FastAPI + SQLAlchemy
- **AI integration** with Hugging Face inference API
- **GitHub API automation** via PyGithub
- **Infrastructure-as-Code** generation (Docker + Terraform)
- **Production-ready** CI/CD with GitHub Actions

---

## 📄 License

MIT License — free to use, modify, and distribute.

---

*ProvisionBot — Because provisioning infrastructure should be as easy as asking for it.*
