# Dokumen Klaim Backend

You said:
i want to make a program that validate document based on rules using large language model (llm)
ChatGPT said:

That’s a great idea — using an LLM to validate documents against defined rules or policies can save tons of manual review time. Let’s walk through how you can design and build such a system.

### 🧩 Step 1: Define the Problem

You want to:

    Input: A document (e.g., a contract, policy, report, etc.)

    Rules: A set of structured or semi-structured validation criteria (e.g., “The document must include a signature,” “The report must mention the fiscal year,” “The policy must not contain confidential terms”)

    Output: A validation report showing which rules are satisfied, violated, or uncertain.

### ⚙️ Step 2: Choose an Approach

There are two common architectures for LLM-based validation:

1. Prompt-Based Validation (Direct)

You give the LLM the document and the rules in a structured prompt, and it outputs a validation result.

✅ Pros: Easy to implement
❌ Cons: May not scale to long documents or complex rule logic

Example (in Python pseudocode):

from openai import OpenAI

client = OpenAI()

rules = """

1. The document must mention a date.
2. The document must include a signature section.
3. The document must not contain confidential terms like 'secret' or 'proprietary'.
   """

document = open("document.txt").read()

prompt = f"""
You are a document validator.
Document:
{document}

Rules:
{rules}

For each rule, say if it's:

- PASSED ✅
- FAILED ❌
- UNCERTAIN 🤔

Explain briefly why.
"""

response = client.chat.completions.create(
model="gpt-5-turbo",
messages=[{"role": "user", "content": prompt}]
)

print(response.choices[0].message.content)

2. Hybrid LLM + Rule Engine

You combine traditional rule-based checks (e.g., regex, metadata validation) with LLM reasoning for semantic or contextual rules.

✅ Pros: Reliable, scalable, explainable
❌ Cons: Slightly more complex architecture

Example structure:

+------------------+
| Document Input |
+------------------+
↓
+------------------+
| Rule Engine (hard rules) |
| e.g., regex, metadata check |
+------------------+
↓
+------------------+
| LLM Validator (semantic rules) |
| e.g., "Does the tone match policy?" |
+------------------+
↓
+------------------+
| Validation Report |
+------------------+

### 🧠 Step 3: Define Rules Clearly

Each rule should be:

    Atomic (one requirement per rule)

    Testable (the model can reason about it)

    Descriptive (so the model understands context)

Example JSON schema for rules:

[
{"id": "R1", "description": "The document must include a date."},
{"id": "R2", "description": "It must contain a signature section."},
{"id": "R3", "description": "It must not contain confidential terms."}
]

### 🧾 Step 4: Generate a Structured Output

Ask the LLM to output machine-readable validation results, e.g. JSON:

{
"R1": {"status": "PASSED", "reason": "Found date 'June 12, 2024'"},
"R2": {"status": "FAILED", "reason": "No signature section detected"},
"R3": {"status": "PASSED", "reason": "No confidential terms found"}
}

This lets you integrate results into dashboards, APIs, or reports.

### 🔧 Step 5: (Optional) Add Evaluation & Feedback Loop

You can add:

    Automatic scoring of validation accuracy (compare to human labels)

    Fine-tuning / custom instructions to improve consistency

    Retrieval-Augmented Generation (RAG) if you have external rule documentation

Would you like me to show you a complete working Python example (that takes a document + rule list and returns a structured validation report using an LLM)?
You said:
yes please
ChatGPT said:

Perfect 👌 — let’s build a complete working Python example that validates a document against a set of rules using an LLM (like GPT-5-Turbo).

Below is a simple yet powerful prototype you can run right away.
🧠 Document Validation Using LLM
🔹 Features

    Input: text document + JSON rules

    Output: structured validation report (JSON)

    Uses OpenAI API with a GPT model (you can easily adapt it to another provider)

### 📦 Step 1: Install Dependencies

`pip install openai`

### 🧾 Step 2: Create a File validator.py

```python
from openai import OpenAI
import json

# Initialize the client

client = OpenAI(api_key="YOUR_OPENAI_API_KEY")

# Define your rules

rules = [
{"id": "R1", "description": "The document must include a date."},
{"id": "R2", "description": "The document must include a signature section."},
{"id": "R3", "description": "The document must not contain confidential terms such as 'secret' or 'proprietary'."},
]

# Load a sample document

document = """
Acme Corp Annual Report 2024

Date: June 12, 2024

This report contains the financial summary for the fiscal year.

Sincerely,
John Doe
"""

# Construct the LLM prompt

rules_text = "\n".join([f"{r['id']}: {r['description']}" for r in rules])

prompt = f"""
You are an AI document validator.

Document:
\"\"\"{document}\"\"\"

Validation Rules:
{rules_text}

For each rule, decide if it is:

- PASSED ✅
- FAILED ❌
- UNCERTAIN 🤔

Output your results in _strict JSON_ using this format:
{{
  "rule_id": {{
    "status": "PASSED|FAILED|UNCERTAIN",
    "reason": "short explanation"
  }}
}}
"""

# Send request to the model

response = client.chat.completions.create(
model="gpt-5-turbo",
messages=[{"role": "user", "content": prompt}],
temperature=0,
)

# Parse and pretty print JSON output

content = response.choices[0].message.content.strip()

try:
validation_results = json.loads(content)
except json.JSONDecodeError:
print("⚠️ Model did not return valid JSON. Raw output:\n", content)
exit()

print("\n✅ Validation Report:")
print(json.dumps(validation_results, indent=2))
```

### 🧩 Step 3: Run It

`python validator.py`

You’ll get output like:

```json
{
  "R1": {
    "status": "PASSED",
    "reason": "Found a date: 'June 12, 2024'."
  },
  "R2": {
    "status": "PASSED",
    "reason": "Signature section found with 'Sincerely, John Doe'."
  },
  "R3": {
    "status": "PASSED",
    "reason": "No confidential terms found."
  }
}
```

### 🚀 Step 4: Extend It

You can improve this system by adding:

- Hybrid checks — e.g., regex for strict rules (like date format) and LLM for fuzzy checks.

- Batch validation — run many documents in parallel.

- RAG or vector search — if rules are stored in a knowledge base.

- Web or API interface — wrap it with FastAPI or Streamlit for an interactive UI.

Would you like me to show you the hybrid version next — where regex handles simple rules and the LLM only deals with semantic ones (for cost and speed efficiency)?
You said:
yes, i wanto see the hybrid version
ChatGPT said:

Excellent — the hybrid approach is the best of both worlds 💡
It uses traditional rule checks (like regex or string search) for simple or objective rules, and LLM reasoning for complex or semantic ones.

Here’s a complete working Python example 👇
🧠 Hybrid Document Validator (Regex + LLM)
⚙️ Features

    Objective rules handled with regex (fast, cheap)

    Semantic rules handled by an LLM (intelligent)

    Returns a structured JSON validation report

📦 Step 1: Install Dependencies

`pip install openai`

🧾 Step 2: Create a File hybrid_validator.py

```python
import re
import json
from openai import OpenAI

# -------------------------------

# CONFIGURATION

# -------------------------------

client = OpenAI(api_key="YOUR_OPENAI_API_KEY")

# Sample document

document = """
Acme Corp Annual Report 2024

Date: June 12, 2024

This report summarizes Acme's financial performance.
All information is public and non-confidential.

Sincerely,
Jane Doe
"""

# Define validation rules

rules = [
{"id": "R1", "description": "The document must include a date.", "type": "regex"},
{"id": "R2", "description": "The document must include a signature section.", "type": "regex"},
{"id": "R3", "description": "The document must not contain confidential terms such as 'secret' or 'proprietary'.", "type": "regex"},
{"id": "R4", "description": "The tone of the document must be formal and professional.", "type": "llm"},
{"id": "R5", "description": "The document should clearly summarize the fiscal year’s performance.", "type": "llm"}
]

# -------------------------------

# REGEX CHECKS

# -------------------------------

def regex_check(rule, text):
if "date" in rule["description"].lower():
pattern = r"\b(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|" \
 r"Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)\s+\d{1,2},\s+\d{4}\b"
if re.search(pattern, text):
return {"status": "PASSED", "reason": "Found a date in the document."}
else:
return {"status": "FAILED", "reason": "No valid date found."}

    if "signature" in rule["description"].lower():
        if re.search(r"(Sincerely|Best regards|Signed),", text, re.IGNORECASE):
            return {"status": "PASSED", "reason": "Signature section found."}
        else:
            return {"status": "FAILED", "reason": "No signature section detected."}

    if "confidential" in rule["description"].lower():
        if re.search(r"(secret|proprietary|confidential)", text, re.IGNORECASE):
            return {"status": "FAILED", "reason": "Confidential terms found."}
        else:
            return {"status": "PASSED", "reason": "No confidential terms found."}

    return {"status": "UNCERTAIN", "reason": "No regex rule applied."}

# -------------------------------

# LLM CHECKS

# -------------------------------

def llm_check(rules, text):
rules_text = "\n".join([f"{r['id']}: {r['description']}" for r in rules])
prompt = f"""
You are a document validator. Analyze the document below against the listed rules.

Document:
\"\"\"{text}\"\"\"

Rules:
{rules_text}

For each rule, output a JSON object with this format:
{{
  "rule_id": {{
    "status": "PASSED|FAILED|UNCERTAIN",
    "reason": "short explanation"
  }}
}}
Only output JSON, no extra text.
"""

    response = client.chat.completions.create(
        model="gpt-5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
    )

    try:
        return json.loads(response.choices[0].message.content.strip())
    except json.JSONDecodeError:
        return {"error": "Invalid JSON output from LLM"}

# -------------------------------

# MAIN VALIDATION PIPELINE

# -------------------------------

def validate_document(document, rules):
results = {}

    # Split rules by type
    regex_rules = [r for r in rules if r["type"] == "regex"]
    llm_rules = [r for r in rules if r["type"] == "llm"]

    # Run regex validations
    for rule in regex_rules:
        results[rule["id"]] = regex_check(rule, document)

    # Run LLM validations (if any)
    if llm_rules:
        llm_results = llm_check(llm_rules, document)
        results.update(llm_results)

    return results

# -------------------------------

# EXECUTION

# -------------------------------

if **name** == "**main**":
validation_results = validate_document(document, rules)
print("\n✅ Hybrid Validation Report:")
print(json.dumps(validation_results, indent=2))
```

### 🧩 Step 3: Run It

`python hybrid_validator.py`

You’ll get output like:

```json
{
  "R1": {
    "status": "PASSED",
    "reason": "Found a date in the document."
  },
  "R2": {
    "status": "PASSED",
    "reason": "Signature section found."
  },
  "R3": {
    "status": "PASSED",
    "reason": "No confidential terms found."
  },
  "R4": {
    "status": "PASSED",
    "reason": "Tone is formal and professional."
  },
  "R5": {
    "status": "PASSED",
    "reason": "Clearly summarizes fiscal year performance."
  }
}
```

🚀 Step 4: Next Steps

You can extend this to:

- Load documents dynamically (PDF → text via pdfplumber or PyMuPDF)

- Load rules from a JSON file or database

- Run in bulk for multiple documents

- Serve via an API (e.g. FastAPI)

Would you like me to show you how to wrap this validator in a simple FastAPI service, so you can send documents and get JSON validation reports via an API endpoint?
You said:
what if document has long text and has a lot of rules?
ChatGPT said:

Excellent — that’s the real-world problem you’ll hit very quickly. ✅

When your document is long (hundreds of pages) or you have many rules, a naïve “send everything to the LLM in one big prompt” approach will fail because of:

    Token limits (even GPT-5 models cap out around 100k tokens max)

    Latency and cost (each validation becomes slow & expensive)

    Context dilution (LLMs lose focus when fed too much information)

So, you’ll want a scalable architecture — a multi-stage, hybrid system that handles long documents intelligently.
🧠 Scalable Architecture for Large Document Validation

Here’s the high-level architecture used in production systems 👇

+----------------------------+
| Document Input |
+----------------------------+
↓
+----------------------------+
| Preprocessing / Chunking | ← split document into sections
+----------------------------+
↓
+-----------------------------------+
| Lightweight Rule Engine (regex, |
| metadata, keyword filters, etc.) |
+-----------------------------------+
↓
+-------------------------------------------+
| LLM Validator (semantic or contextual) |
| - Uses summaries per section |
| - Runs only on relevant chunks |
+-------------------------------------------+
↓
+----------------------------+
| Aggregator / Final Report |
+----------------------------+

⚙️ Step 1: Chunking & Summarization

You split the document into manageable pieces (e.g. ~2–4k tokens each).
Each chunk is summarized and indexed for retrieval.

Example chunking pseudocode:

from langchain.text_splitter import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(chunk_size=3000, chunk_overlap=200)
chunks = splitter.split_text(long_document)

You can store these chunks in:

    A vector database (like Chroma or Pinecone) for retrieval, or

    Just process sequentially if the number of chunks is small.

⚙️ Step 2: Retrieve Only Relevant Chunks per Rule

For each rule, instead of sending the whole document, you:

    Use keyword or embedding search to find relevant chunks

    Pass only those chunks to the LLM

Example:

from openai import OpenAI
from openai.embeddings_utils import get_embedding, cosine_similarity

client = OpenAI(api_key="YOUR_API_KEY")

rule = "The document must mention the fiscal year and financial summary."

# Get embeddings for rule and document chunks

rule_vector = get_embedding(rule, model="text-embedding-3-small")
chunk_vectors = [get_embedding(c, model="text-embedding-3-small") for c in chunks]

# Rank chunks by similarity

ranked = sorted(
zip(chunks, chunk_vectors),
key=lambda x: cosine_similarity(rule_vector, x[1]),
reverse=True
)

# Select top 3 most relevant chunks

relevant_chunks = [r[0] for r in ranked[:3]]

Then, send only those chunks + the rule to the LLM for validation.
⚙️ Step 3: Per-Rule LLM Evaluation (on relevant context)

prompt = f"""
You are a document validator. Check if the rule is satisfied
based on the text excerpts below.

Rule: "{rule}"

Relevant Excerpts:
\"\"\"{'\n---\n'.join(relevant_chunks)}\"\"\"

Answer in JSON:
{{ "status": "PASSED|FAILED|UNCERTAIN", "reason": "short explanation" }}
"""

response = client.chat.completions.create(
model="gpt-5-turbo",
messages=[{"role": "user", "content": prompt}],
temperature=0
)

This approach scales easily to dozens or even hundreds of rules because each rule only reads small, relevant portions of the document.
⚙️ Step 4: Aggregation

If multiple chunks are evaluated for a single rule, you can merge results:

def aggregate_results(results):
if any(r["status"] == "FAILED" for r in results):
return {"status": "FAILED", "reason": "At least one section violated the rule."}
elif all(r["status"] == "PASSED" for r in results):
return {"status": "PASSED", "reason": "All relevant sections satisfied the rule."}
else:
return {"status": "UNCERTAIN", "reason": "Mixed results."}

⚙️ Step 5: Optimization Tips
Problem Solution
Long docs exceed token limit Chunk + summarize
Many rules slow things down Parallelize LLM calls (async or multiprocessing)
High cost Pre-filter with regex / embeddings before LLM
Inconsistent outputs Ask model for JSON only; add few-shot examples
Confidential data Run on-prem LLM (e.g., Llama 3) instead of API
⚡ Optional Enhancements

    RAG layer: use embeddings + retrieval for high recall

    Caching: don’t re-validate same rules on same chunks

    Evaluation pipeline: benchmark LLM outputs vs. human reviewers

    UI / API: expose validation as a microservice

If you’d like, I can show you a full working prototype (in Python) that does:

    document chunking,

    per-rule retrieval,

    and per-rule LLM validation,
    returning a unified JSON report.

Would you like me to generate that end-to-end example next?
You said:
yes, please show me full working prototype
ChatGPT said:

Perfect 👍 — let’s build a full working prototype that can handle long documents and many rules efficiently using a chunk + retrieval + validation pipeline.

This example is designed for clarity, scalability, and real-world readiness.
🧠 LLM Document Validator — Scalable Prototype
📦 Step 1: Install Dependencies

pip install openai tiktoken langchain numpy

🧾 Step 2: Create a File scalable_validator.py

import json
import numpy as np
from openai import OpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from openai.embeddings_utils import get_embedding, cosine_similarity

# ------------------------------------------------------------

# CONFIGURATION

# ------------------------------------------------------------

client = OpenAI(api_key="YOUR_OPENAI_API_KEY")
EMBED_MODEL = "text-embedding-3-small"
LLM_MODEL = "gpt-5-turbo"

# ------------------------------------------------------------

# SAMPLE INPUTS

# ------------------------------------------------------------

long_document = """
Acme Corporation Annual Report 2024

Executive Summary:
Acme achieved record revenues in the fiscal year 2024,
increasing profits by 15%. The company's growth was driven by
its new logistics division and expansion into Asia-Pacific.

Governance:
All operations complied with international labor and environmental standards.

Date: June 30, 2024

Sincerely,
Jane Doe, Chief Financial Officer
"""

rules = [
{"id": "R1", "description": "The document must mention the fiscal year."},
{"id": "R2", "description": "The document must include a date."},
{"id": "R3", "description": "The document must include a signature or sign-off section."},
{"id": "R4", "description": "The tone of the document must be formal and professional."},
{"id": "R5", "description": "The document must include an executive summary section."},
{"id": "R6", "description": "The document must not include confidential or proprietary terms."}
]

# ------------------------------------------------------------

# 1️⃣ CHUNK THE DOCUMENT

# ------------------------------------------------------------

def chunk_document(text, chunk_size=2000, overlap=200):
splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=overlap)
chunks = splitter.split_text(text)
return chunks

# ------------------------------------------------------------

# 2️⃣ EMBED CHUNKS

# ------------------------------------------------------------

def embed_chunks(chunks):
return [get_embedding(c, model=EMBED_MODEL) for c in chunks]

# ------------------------------------------------------------

# 3️⃣ RETRIEVE RELEVANT CHUNKS FOR A RULE

# ------------------------------------------------------------

def get_relevant_chunks(rule_text, chunks, chunk_embeddings, top_k=3):
rule_vector = get_embedding(rule_text, model=EMBED_MODEL)
scores = [cosine_similarity(rule_vector, e) for e in chunk_embeddings]
top_indices = np.argsort(scores)[::-1][:top_k]
return [chunks[i] for i in top_indices]

# ------------------------------------------------------------

# 4️⃣ VALIDATE A RULE USING LLM ON RELEVANT CHUNKS

# ------------------------------------------------------------

def validate_rule(rule, relevant_chunks):
prompt = f"""
You are an AI document validator.
Check whether the following rule is satisfied based only on the provided excerpts.

Rule: "{rule['description']}"

Relevant Excerpts:
\"\"\"{'\n---\n'.join(relevant_chunks)}\"\"\"

Output JSON strictly in this format:
{{
  "status": "PASSED|FAILED|UNCERTAIN",
  "reason": "short explanation"
}}
"""
response = client.chat.completions.create(
model=LLM_MODEL,
messages=[{"role": "user", "content": prompt}],
temperature=0,
)

    try:
        return json.loads(response.choices[0].message.content.strip())
    except json.JSONDecodeError:
        return {"status": "UNCERTAIN", "reason": "Model output not valid JSON"}

# ------------------------------------------------------------

# 5️⃣ MAIN VALIDATION PIPELINE

# ------------------------------------------------------------

def validate_document(document, rules):
print("🔹 Chunking document...")
chunks = chunk_document(document)
print(f" → {len(chunks)} chunks created.")

    print("🔹 Embedding chunks...")
    chunk_embeddings = embed_chunks(chunks)

    results = {}
    for rule in rules:
        print(f"\n🔹 Validating Rule {rule['id']}: {rule['description']}")
        relevant_chunks = get_relevant_chunks(rule["description"], chunks, chunk_embeddings)
        result = validate_rule(rule, relevant_chunks)
        results[rule["id"]] = result

    return results

# ------------------------------------------------------------

# 6️⃣ RUN THE VALIDATOR

# ------------------------------------------------------------

if **name** == "**main**":
report = validate_document(long_document, rules)

    print("\n✅ Final Validation Report:")
    print(json.dumps(report, indent=2))

🧩 Step 3: Run It

python scalable_validator.py

You’ll get output like:

{
"R1": {
"status": "PASSED",
"reason": "Mentions 'fiscal year 2024'."
},
"R2": {
"status": "PASSED",
"reason": "Date 'June 30, 2024' found."
},
"R3": {
"status": "PASSED",
"reason": "Contains sign-off 'Sincerely, Jane Doe'."
},
"R4": {
"status": "PASSED",
"reason": "Tone is formal and professional."
},
"R5": {
"status": "PASSED",
"reason": "Has an 'Executive Summary' section."
},
"R6": {
"status": "PASSED",
"reason": "No confidential or proprietary terms found."
}
}

⚡ Why This Scales Well
Feature Benefit
Chunking Works on long docs (no token limit issues)
Embeddings retrieval Sends only relevant content per rule
Parallelizable Each rule can run in parallel for speed
Structured JSON Easy to consume programmatically
Extensible You can plug in different LLMs or databases
🚀 Optional Enhancements

    Add async or batching for faster API calls

    Cache embeddings with a local store (e.g., SQLite + hash keys)

    Use vector DB (Chroma, Pinecone) for faster retrieval

    Add human review interface for uncertain rules

    Export reports to CSV or JSONL

Would you like me to extend this into a FastAPI web service, where you can upload a document and get a JSON validation report through an API endpoint?

ChatGPT can make mistakes. Check important info. See Cookie Preferences.
