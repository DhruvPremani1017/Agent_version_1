#!/usr/bin/env python3
"""
Single-Agent Code Review & Refactoring Bot using Google Generative AI

- Reads a Python source file
- Runs style and static analysis (flake8)
- Parses AST for function outlines
- Prompts the Google Gemini (Chat-Bison) model to provide annotated suggestions
- Outputs a markdown report with refactored code snippets

Requirements:
  pip install python-dotenv flake8 google-generativeai

Usage:
  export GOOGLE_API_KEY="your_api_key"
  python code_review_bot.py path/to/your_file.py
"""
import os
import sys
import subprocess
import ast
from dotenv import load_dotenv
import google.generativeai as genai
from google import generativeai as genai


def load_api_key():
    load_dotenv()
    key = os.getenv("GOOGLE_API_KEY")
    if not key:
        print("Error: GOOGLE_API_KEY not set in environment.", file=sys.stderr)
        sys.exit(1)
    genai.configure(api_key=key)


def get_flake8_issues(file_path):
    """
    Run flake8 on file_path and return a list of issue strings.
    """
    try:
        result = subprocess.run(
            ["flake8", file_path, "--format=%(row)d:%(col)d: %(code)s %(text)s"],
            capture_output=True,
            text=True,
            check=False
        )
        if result.stdout.strip():
            return result.stdout.strip().splitlines()
        return []
    except FileNotFoundError:
        print("Error: flake8 not installed or not in PATH.", file=sys.stderr)
        sys.exit(1)


def extract_functions(source_code):
    """
    Parse the source code to extract defined function names.
    """
    tree = ast.parse(source_code)
    funcs = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
    return funcs


def build_prompt(source_code, issues, functions):
    """
    Construct the prompt for the LLM including code, issues, and function list.
    """
    prompt = []
    prompt.append("You are a senior Python developer and code reviewer.")
    prompt.append("Analyze the following code for style issues, bugs, performance bottlenecks, and refactor it.")
    prompt.append("Provide inline comments on what changed and why, and output the full refactored snippets.")
    prompt.append("---")
    prompt.append("### Original Code:\n```python")
    prompt.append(source_code)
    prompt.append("```")
    if issues:
        prompt.append("### Detected Issues:")
        for issue in issues:
            prompt.append(f"- {issue}")
    if functions:
        prompt.append("### Functions Defined:")
        prompt.append(", ".join(functions))
    prompt.append("---")
    prompt.append("### Refactored Code and Suggestions:")
    return "\n".join(prompt)


# def call_gemini(prompt_text):
#     """
#     Call Google Gemini (Chat-Bison) to get review and refactored code.
#     """
#     response = genai.chat.completions.create(
#         model="models/chat-bison-001",
#         messages=[
#             {"role": "system", "content": "You are CodeReviewBot, an automated code review assistant."},
#             {"role": "user",   "content": prompt_text}
#         ]
#     )
#     # Extract the assistant reply
#     return response.choices[0].message.content

def call_gemini(prompt_text):
    """
    Call Gemini model and return the response text.
    """
    model = genai.GenerativeModel("gemini-1.5-pro")  # Or use "gemini-pro"
    response = model.generate_content(prompt_text)
    return response.text




def main():
    if len(sys.argv) != 2:
        print("Usage: python code_review_bot.py path/to/file.py", file=sys.stderr)
        sys.exit(1)

    file_path = sys.argv[1]
    if not os.path.isfile(file_path):
        print(f"Error: File not found: {file_path}", file=sys.stderr)
        sys.exit(1)

    # Load API key
    load_api_key()

    # Read source code
    with open(file_path, 'r', encoding='utf-8') as f:
        source = f.read()

    # Analysis steps
    issues = get_flake8_issues(file_path)
    functions = extract_functions(source)

    # Build prompt
    prompt_text = build_prompt(source, issues, functions)

    # LLM call
    review = call_gemini(prompt_text)

    # Output markdown report
    report_path = file_path.rsplit('.', 1)[0] + '_review.md'
    with open(report_path, 'w', encoding='utf-8') as out:
        out.write(review)

    print(f"Code review complete. See {report_path}")


if __name__ == '__main__':
    main()
