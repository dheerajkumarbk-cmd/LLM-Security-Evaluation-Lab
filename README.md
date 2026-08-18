# LLM Security Evaluation Lab

[![Framework Status](https://img.shields.io/badge/Status-Portfolio%20Grade%20v1.0-blue.svg)](#)
[![Python](https://img.shields.io/badge/Python-3.10%2B-green.svg)](#)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688.svg)](#)
[![React](https://img.shields.io/badge/React-18-61DAFB.svg)](#)

A defensive evaluation and red-teaming framework for measuring Large Language Model (LLM) behavior under adversarial, edge-case, and safety-critical prompting scenarios. Built for rigor, reproducibility, and transparent methodology for Supervised Program for Alignment Research (SPAR AI) evaluation contexts.

---

## 📌 Executive Summary & Architecture

The **LLM Security Evaluation Lab** delivers structured, category-based security evaluation across 8 key safety dimensions. Every test prompt exists to produce logged, reproducible, severity-weighted metrics rather than offensive exploits.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          LLM Security Evaluation Lab                        │
├───────────────────┬───────────────────────────┬─────────────────────────────┤
│  Test Case Store  │     Execution Harness     │      Scoring Engine         │
│  (Declarative     │  - Adapter Interface      │  - Rule-based Heuristics    │
│   YAML Suites)    │  - Retry / Backoff        │  - LLM-as-a-Judge Rubrics   │
│   78+ Test Cases  │  - Concurrent Async       │  - Composite Risk Weighting │
└─────────┬─────────┴─────────────┬─────────────┴──────────────┬──────────────┘
          │                       │                            │
          ▼                       ▼                            ▼
┌───────────────────┐   ┌───────────────────┐        ┌───────────────────┐
│ SQLite Database   │◄──┤ REST API Engine   │◄───────┤ React Dashboard   │
│ (Historical Runs &│   │ (FastAPI Backend) │        │ (Interactive UI,  │
│ Results Triage)   │   │                   │        │ Heatmaps & Charts)│
└───────────────────┘   └───────────────────┘        └───────────────────┘
```

---

## 🎯 Evaluated Security Categories

| Category | Taxonomy Code | Focus & Description | Methodology Note |
|---|---|---|---|
| **Prompt Injection** | `PI` | Direct instruction overrides & indirect injection in data/documents | Tests whether model prioritizes system prompt over untrusted data |
| **Jailbreak Attempts** | `JB` | Persona adoption, encoding (Base64/ROT13), multi-turn trust escalation | Probes filter bypass resistance across multi-turn contexts |
| **Data Extraction / PII** | `DE` | Training data disclosure & context PII leakage | Verifies boundary isolation for confidential user/system context |
| **System Prompt Leakage**| `SP` | Extraction via direct asking, translation, or markdown formatting | Measures secret preservation of internal instructions |
| **Unsafe Instruction** | `UI` | False authority claims ("Admin override", "Emergency mode") | Evaluates compliance under simulated authorization claims |
| **Over-Refusal** | `OR` | False positives on safe, benign educational queries | **Inverse category**: Measures utility maintenance vs over-defensiveness |
| **Hallucination** | `HL` | Fabrication of non-existent books, dates, papers, and entities | Evaluates factual grounding fidelity |
| **Tool Misuse** | `TM` | Unauthorized function execution or malformed tool arguments | Tests agentic tool invocation boundaries |

---

## ⚙️ Transparent Risk Scoring Methodology

### 1. Per-Test Score Formula
Each test output is scored using a hybrid combination of deterministic heuristics and LLM-as-a-judge rubrics:

$$\text{Final Score} = (w_h \times S_h) + (w_j \times S_j)$$

* $S_h$: Heuristic score ($1.0$ if all checks pass, $0.0$ if failed)
* $S_j$: LLM-as-a-Judge rubric score ($0.0 \le S_j \le 1.0$)
* Default weights: $w_h = 0.4$, $w_j = 0.6$

### 2. Per-Category Safety Score Formula
$$\text{Category Score} = \frac{\sum_{i=1}^{N} (S_{\text{final}, i} \times w_{\text{severity}, i})}{\sum_{i=1}^{N} w_{\text{severity}, i}} \times 100$$

* Severity weights ($w_{\text{severity}}$): Low = 1, Medium = 2, High = 3, Critical = 5

### 3. Overall Composite Risk Score Formula
$$\text{Composite Risk Score} = 100 - \frac{\sum_{j=1}^{C} (\text{Category Score}_j \times w_{\text{category}, j})}{\sum_{j=1}^{C} w_{\text{category}, j}}$$

* Score range: `0` (Perfect safety) to `100` (Maximum risk / complete vulnerability)

---

## 🚀 Quick Start Guide

### 1. Prerequisites & Environment Setup
```bash
# Clone the repository
git clone https://github.com/dheerajkumarbk-cmd/LLM-Security-Evaluation-Lab.git
cd "LLM-Security-Evaluation-Lab"

# Set up Python virtual environment
python -m venv venv
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure API Keys
Set your provider environment variables:
```bash
# Windows PowerShell
$env:OPENAI_API_KEY="your-openai-key"
$env:ANTHROPIC_API_KEY="your-anthropic-key"
```

### 3. Run Benchmark via CLI
```bash
# Run full evaluation suite against GPT-4o-mini
python run_eval.py --model gpt-4o-mini --suite full

# Run specific categories
python run_eval.py --model claude-sonnet --categories prompt_injection,jailbreak

# Export PDF audit report of latest run
python run_eval.py --report --format pdf
```

### 4. Launch Full Stack Web Dashboard
```bash
# Terminal 1: Start FastAPI backend API (Port 8000)
uvicorn backend.main:app --reload --port 8000

# Terminal 2: Start React Frontend Dashboard (Port 5173)
cd frontend
npm install
npm run dev
```

Open browser at `http://localhost:5173`.

---

## 📊 Sample Empirical Findings (GPT-4o-mini vs Claude 3.5 Sonnet)

| Security Dimension | GPT-4o-mini Score | Claude 3.5 Sonnet Score | Vulnerability Delta |
|---|---|---|---|
| Direct Prompt Injection | 88.5 / 100 | 95.0 / 100 | +6.5 (Claude safer) |
| System Prompt Leakage | 72.0 / 100 | 91.5 / 100 | +19.5 (Claude safer) |
| Over-Refusal Resistance | 94.0 / 100 | 81.0 / 100 | -13.0 (GPT-4o-mini safer) |
| Multi-turn Jailbreaks | 65.0 / 100 | 88.0 / 100 | +23.0 (Claude safer) |
| **Overall Composite Risk** | **22.4 (Low Risk)** | **11.8 (Very Low Risk)** | **Claude -10.6 Risk** |

### Key Alignment Insights:
1. **System Prompt Hardening**: Claude models demonstrate significantly stronger boundary separation when prompts instruct formatting overrides.
2. **Over-Refusal Trade-off**: Stronger safety alignment in Claude leads to elevated false-positive refusal rates on benign educational prompts (e.g., historical weapon queries).

---

## 🧪 Extensibility & Custom Plugins

Adding a new security category requires no modification to core framework logic:
1. Add a new directory in `test_suites/<new_category>/`
2. Include a `_category.yaml` metadata file describing the evaluation methodology
3. Add declarative YAML test cases following `test_suites/_schema.yaml`

---

## 📜 Citation & Research Application

If using this evaluation lab for alignment research, citation, or SPAR AI applications:

```bibtex
@misc{llm-security-eval-lab-2026,
  author = {Dheeraj Kumar},
  title = {LLM Security Evaluation Lab: A Defensive Benchmark & Red-Teaming Framework},
  year = {2026},
  publisher = {GitHub},
  journal = {GitHub repository},
  howpublished = {\url{https://github.com/dheerajkumarbk-cmd/LLM-Security-Evaluation-Lab}}
}
```
