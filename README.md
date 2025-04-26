# 🛠️ Multi-Agent and Single-Agent Code Review Bots using LangChain + Google Gemini

This repository contains two Python scripts that automate **Python code review**, **refactoring**, **test stub generation**, and **documentation** using **Google Gemini** and **LangChain**.  
Both **Single-Agent** and **Multi-Agent** architectures are provided for comparison.

---

## 📄 Project Structure

- `multi_agent_code_review.py`:  
  Multi-agent pipeline where each "agent" handles a specific task like AST parsing, linting, refactoring, test generation, and documentation separately.

- `code_review_bot.py`:  
  Single-agent bot that performs full review and refactoring in one LLM interaction.

---

## 🚀 Features

| Feature                           | Multi-Agent Bot (`multi_agent_code_review.py`) | Single-Agent Bot (`code_review_bot.py`) |
|------------------------------------|:---------------------------------------------:|:---------------------------------------:|
| AST Parsing (Function Extraction) | ✅ | ✅ |
| Flake8 Lint Checking               | ✅ | ✅ |
| Refactoring with Inline Comments   | ✅ (separate agent) | ✅ (inline with refactoring) |
| Unit Test Generation (pytest)      | ✅ | ❌ |
| Markdown Documentation Generation  | ✅ | ❌ |
| Modularity and Control             | High (Independent agents) | Medium (One-shot review) |
| Model Used                         | Gemini 1.5 Pro (via `google-generativeai`) | Gemini 1.5 Pro (via `google-generativeai`) |

---

## 📦 Installation

Make sure you have Python 3.8+ installed.

1. Clone the repository:

```bash
git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name
