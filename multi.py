#!/usr/bin/env python3
"""
Multi-Agent Code Review Pipeline using LangChain LLMChain and Google Gemini

This script defines 5 sequential "agents":
  1. AST Parser (local)
  2. Lint Checker (local via flake8)
  3. Refactor Agent (LLMChain)
  4. Test Generation Agent (LLMChain)
  5. Documentation Agent (LLMChain)

Each agent produces a piece of the final Markdown report, which is then aggregated and saved.

Requirements:
  pip install python-dotenv flake8 google-genai langchain pydantic

Usage:
  export GOOGLE_API_KEY="your_api_key"
  python multi_agent_code_review.py path/to/your_file.py

Output:
  path/to/your_file_review.md
"""
import os
import sys
import subprocess
import ast
from dotenv import load_dotenv
import google.generativeai as genai
from langchain import LLMChain, PromptTemplate
from langchain.llms.base import LLM
from pydantic import BaseModel, Field
from typing import Mapping, Any, Optional, List

# ---------- Configure Google Gemini ----------
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")
if not API_KEY:
    print("Error: GOOGLE_API_KEY not set.", file=sys.stderr)
    sys.exit(1)
genai.configure(api_key=API_KEY)

# ---------- LLM Wrapper ----------
class GeminiLLM(LLM, BaseModel):
    model_name: str = Field(default="gemini-1.5-pro")

    def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        model = genai.GenerativeModel(self.model_name)
        resp = model.generate_content(prompt)
        return resp.text.strip()

    @property
    def _identifying_params(self) -> Mapping[str, Any]:
        return {"model_name": self.model_name}

    @property
    def _llm_type(self) -> str:
        return "gemini"

# ---------- Local Agents ----------
def parse_functions(code: str) -> List[str]:
    """Extract function names from Python source code."""
    tree = ast.parse(code)
    return [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]


def lint_issues(code: str) -> List[str]:
    """Run flake8 and return a list of issues."""
    tmp_path = "_tmp_review.py"
    with open(tmp_path, 'w', encoding='utf-8') as f:
        f.write(code)
    result = subprocess.run([
        "flake8", tmp_path, "--format=%(row)d:%(col)d: %(code)s %(text)s"
    ], capture_output=True, text=True)
    os.remove(tmp_path)
    lines = result.stdout.strip().splitlines()
    return lines if lines else []

# ---------- LLM Agents ----------
REFRACTOR_PROMPT = PromptTemplate(
    input_variables=["code", "issues", "functions"],
    template="""
You are a senior Python developer. Refactor the following code, addressing the issues, and add inline comments explaining your changes.

Issues:
{issues}

Functions:
{functions}

Code:
```python
{code}
```

Provide only the refactored code block.
"""
)
refactor_chain = LLMChain(llm=GeminiLLM(), prompt=REFRACTOR_PROMPT)

TEST_PROMPT = PromptTemplate(
    input_variables=["code", "functions"],
    template="""
You are a Python QA engineer. Generate pytest unit test stubs for each function listed.

Functions:
{functions}

Code:
```python
{code}
```

Provide only the test stubs.
"""
)
test_chain = LLMChain(llm=GeminiLLM(), prompt=TEST_PROMPT)

DOC_PROMPT = PromptTemplate(
    input_variables=["code", "functions"],
    template="""
You are a technical writer. Write Markdown documentation for the following Python module.

Functions:
{functions}

Code:
```python
{code}
```

Provide only the documentation section.
"""
)
doc_chain = LLMChain(llm=GeminiLLM(), prompt=DOC_PROMPT)

# ---------- Coordinator ----------
def main():
    if len(sys.argv) != 2:
        print("Usage: python multi_agent_code_review.py path/to/your_file.py", file=sys.stderr)
        sys.exit(1)

    path = sys.argv[1]
    if not os.path.isfile(path):
        print(f"Error: File not found: {path}", file=sys.stderr)
        sys.exit(1)

    code = open(path, 'r', encoding='utf-8').read()

    # 1. AST Parsing
    functions = parse_functions(code)
    functions_str = ", ".join(functions) if functions else "<none>"

    # 2. Linting
    issues = lint_issues(code)
    issues_str = "\n".join(issues) if issues else "<no issues>"

    # 3. Refactoring
    refactored = refactor_chain.run(code=code, issues=issues_str, functions=functions_str)

    # 4. Test Generation
    tests = test_chain.run(code=code, functions=functions_str)

    # 5. Documentation
    docs = doc_chain.run(code=code, functions=functions_str)

    # Aggregate final report
    report = [
        "# Functions", functions_str,
        "", "# Issues", issues_str,
        "", "# Refactored Code", refactored,
        "", "# Test Stubs", tests,
        "", "# Documentation", docs
    ]

    out_path = path.rsplit('.', 1)[0] + 'MultiAgent_review.md'
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(report))

    print(f"Multi-agent review complete. See {out_path}")

if __name__ == '__main__':
    main()