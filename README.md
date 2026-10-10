# ðŸ¤– BAITHAK WITH AI
### 4-Tier Agentic AI Administrative Workflow

**Designed by Engr. Bilal Mehmood**  
*Certified Generative and Agentic AI Application Developer*

Baithak with AI is a Streamlit-based administrative assistant designed to help users prepare, review, verify, and organize official documents through a simulated four-tier administrative workflow:

**Naib Qasid â†’ Clerk â†’ Superintendent â†’ Section Officer**

The application supports chat-based requests, optional OpenAI-powered responses, a demo mode, reference-document uploads, multiple conversations, and downloads in TXT, DOCX, PDF, and Excel formats (Excel export is available when the response contains a compatible Markdown table).

> **Important:** AI-generated reviews and approvals are drafts produced by the application. They do not constitute real government authorization, legal approval, or an official institutional decision. A human authorized officer must review and approve official documents.

---

## Table of Contents

1. [Features](#-features)
2. [Workflow Architecture](#-workflow-architecture)
3. [Technology Stack](#-technology-stack)
4. [Project Structure](#-project-structure)
5. [Requirements](#-requirements)
6. [Installation on Windows](#-installation-on-windows)
7. [Run the Application](#-run-the-application)
8. [Configure the OpenAI API](#-configure-the-openai-api)
9. [Deploy on Streamlit Community Cloud](#-deploy-on-streamlit-community-cloud)
10. [How to Use](#-how-to-use)
11. [Supported File Formats](#-supported-file-formats)
12. [Configuration](#-configuration)
13. [Troubleshooting](#-troubleshooting)
14. [Security and Privacy](#-security-and-privacy)
15. [Known Limitations](#-known-limitations)
16. [Roadmap](#-roadmap)
17. [Credits](#-credits)
18. [License](#-license)

---

## ðŸš€ Features

- **Four-tier workflow:** Simulates intake, drafting, quality review, and executive sign-off.
- **Individual role selection:** Run the full workflow or select one of the four roles.
- **Demo mode:** Provides a sample workflow response when a usable API client is unavailable.
- **OpenAI integration:** Uses the OpenAI Python SDK and Responses API when configured.
- **Multiple conversations:** Create, switch between, clear, and delete chats for the current session.
- **Document uploads:** Attach PDF, DOCX, and TXT reference documents to a conversation.
- **Text extraction:** Extracts selectable PDF text, Word paragraphs/tables, and text-file content.
- **Document exports:** Download assistant responses as TXT, DOCX, or PDF.
- **Excel exports:** Convert compatible Markdown tables in a response into an XLSX workbook.
- **Responsive interface:** Streamlit layout with a sidebar, workflow selector, chat area, and animated robot panel.
- **Suggested prompts:** Start common administrative drafting tasks with a single click.
- **Optional dependencies:** Several document-processing libraries are imported conditionally, allowing the app to fall back when they are not installed.

---

## ðŸ§­ Workflow Architecture

```text
                 USER REQUEST
                      |
                      v
          +------------------------+
          | 1. NAIB QASID AI       |
          | Intake and Docket      |
          | Creation / Routing     |
          +------------------------+
                      |
                      v
          +------------------------+
          | 2. CLERK AI            |
          | Drafting and Document  |
          | Preparation            |
          +------------------------+
                      |
                      v
          +------------------------+
          | 3. SUPERINTENDENT AI   |
          | Quality Audit and      |
          | Verification Notes     |
          +------------------------+
                      |
                      v
          +------------------------+
          | 4. SECTION OFFICER AI  |
          | Final AI-Generated     |
          | Recommendation         |
          +------------------------+
                      |
                      v
            REVIEW AND HUMAN SIGN-OFF
                      |
                      v
              EXPORT THE DOCUMENT
             TXT / DOCX / PDF / XLSX
```

### Roles and responsibilities

| Role | Responsibility |
|---|---|
| Naib Qasid AI | Accepts the request, records the brief, and prepares a routing/docket response. |
| Clerk AI | Drafts formal emails, memos, notices, tables, and other administrative content. |
| Superintendent AI | Reviews the draft for clarity, completeness, tone, and structure. |
| Section Officer AI | Produces an AI-generated final recommendation or verdict for human review. |

The full hierarchy runs four sequential model calls when the API client is available. Individual-role mode calls the model with the selected role's system instructions.

---

## ðŸ§° Technology Stack

- **Python** â€” application language
- **Streamlit** â€” interactive web application
- **OpenAI Python SDK** â€” optional language-model integration
- **pypdf** â€” PDF text extraction
- **python-docx** â€” Word document reading and generation
- **fpdf2** â€” PDF generation
- **pandas** â€” parsing Markdown tables and preparing Excel exports
- **openpyxl** â€” XLSX workbook writing
- **HTML, CSS, and JavaScript-free CSS animations** â€” interface styling and animated robot illustration

---

## ðŸ“ Project Structure

Create a project directory with the following files:

```text
baithak-with-ai/
â”œâ”€â”€ app.py
â”œâ”€â”€ requirements.txt
â”œâ”€â”€ README.md
â””â”€â”€ .gitignore
```

- `app.py` â€” the Streamlit application code.
- `requirements.txt` â€” Python dependencies.
- `README.md` â€” project documentation.
- `.gitignore` â€” files and secrets that must not be committed.

---

## ðŸ“¦ Requirements

Recommended: Python 3.10 or newer, with a Python version supported by the selected dependency releases.

### `requirements.txt`

Create a file named `requirements.txt` with:

```text
streamlit
openai
pypdf
python-docx
pandas
fpdf2
openpyxl
```

These dependencies enable the main interface, API client, document extraction, and exports. Pin tested package versions for a reproducible production deployment.

---

## ðŸ’» Installation on Windows

### 1. Install Python

Download Python from the official website:

https://www.python.org/downloads/

During installation, select **Add Python to PATH** if the installer offers this option.

Verify the installation in Command Prompt:

```bat
python --version
pip --version
```

If `python` is not recognized, try:

```bat
py --version
py -m pip --version
```

### 2. Create a project folder

```bat
mkdir baithak-with-ai
cd baithak-with-ai
```

Place `app.py`, `requirements.txt`, and `README.md` in this directory.

### 3. Create a virtual environment

```bat
python -m venv .venv
```

Activate it:

```bat
.venv\Scripts\activate
```

If you use the Python launcher instead, create the environment with:

```bat
py -m venv .venv
```

### 4. Upgrade pip and install dependencies

```bat
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 5. Start the application

```bat
streamlit run app.py
```

Streamlit normally opens the app in your default browser. If it does not, open the local URL printed in the terminal, usually:

http://localhost:8501

---

## â–¶ï¸ Run the Application

After installing dependencies, use:

```bash
streamlit run app.py
```

To stop the local server, press `Ctrl+C` in the terminal.

---

## ðŸ”‘ Configure the OpenAI API

The application reads the API key from Streamlit Secrets first and then from the environment variable `OPENAI_API_KEY`.

It also reads `OPENAI_MODEL`, with a code default of `gpt-6-luna`. **Confirm that the model identifier is available to your API account before using it.** If it is not available, set `OPENAI_MODEL` to a model identifier supported by your account and the Responses API.

### Option A: Streamlit Secrets (recommended for Streamlit Cloud)

For local development, create:

```text
.streamlit/secrets.toml
```

Add:

```toml
OPENAI_API_KEY = "your-openai-api-key"
OPENAI_MODEL = "your-supported-model-id"
```

Replace the example values with your own valid credentials and supported model ID.

**Never commit `secrets.toml` or expose your API key in public source code.**

### Option B: Windows Command Prompt environment variable

For the current Command Prompt session:

```bat
set OPENAI_API_KEY=your-openai-api-key
set OPENAI_MODEL=your-supported-model-id
streamlit run app.py
```

For PowerShell:

```powershell
$env:OPENAI_API_KEY="your-openai-api-key"
$env:OPENAI_MODEL="your-supported-model-id"
streamlit run app.py
```

Environment variables set this way generally apply only to the current terminal session.

### How API and Demo modes work

- If the OpenAI SDK or API key is unavailable, the app falls back to its sample demo response.
- If the API client initializes but a request fails, the workflow catches the error and may return the demo response.
- A configured key does not guarantee that a request will succeed. Confirm the model name, account access, network connectivity, and API usage limits.
- The application uses the OpenAI Responses API through `client.responses.create(...)`.

---

## â˜ï¸ Deploy on Streamlit Community Cloud

### Step 1: Create a GitHub repository

1. Sign in to GitHub: https://github.com/
2. Create a repository, for example `baithak-with-ai`.
3. Upload `app.py`, `requirements.txt`, and `README.md`.
4. Do not upload API keys, `.streamlit/secrets.toml`, or your virtual environment.

### Step 2: Add a `.gitignore` file

Use the following:

```gitignore
.venv/
venv/
__pycache__/
*.py[cod]
.env
.streamlit/secrets.toml
.DS_Store
```

### Step 3: Deploy

1. Open https://share.streamlit.io/
2. Sign in with GitHub.
3. Select **Create app**.
4. Choose your repository and branch.
5. Set the main file path to `app.py`.
6. Open the app's **Secrets** settings and add:

```toml
OPENAI_API_KEY = "your-openai-api-key"
OPENAI_MODEL = "your-supported-model-id"
```

7. Deploy the app and review the logs if deployment fails.

Official Streamlit documentation:

- Streamlit documentation: https://docs.streamlit.io/
- Community Cloud deployment: https://docs.streamlit.io/deploy/streamlit-community-cloud
- Streamlit secrets management: https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/secrets

---

## ðŸ“ How to Use

1. Open Baithak with AI.
2. Select **Full Multi-Agent Hierarchy** or choose a specific role from the sidebar.
3. Enter an administrative request in the chat box, or select a suggested prompt.
4. Optionally open **Attach reference documents for official file routing**.
5. Upload PDF, DOCX, or TXT files and select **Add files to conversation**.
6. Submit a request that clearly explains how the source documents should be used.
7. Review the generated output from each workflow stage.
8. Use the export buttons to download the response in a supported format.
9. Have an authorized human review and sign off on official documents before use.

### Example requests

- â€œDraft an official procurement memo for IT hardware supplies.â€
- â€œPrepare a formal administrative notice regarding revised working hours.â€
- â€œGenerate a project schedule table with deadlines and responsible leads.â€
- â€œDraft an executive briefing note based on the attached document.â€

### Conversation controls

- **New chat:** Creates another conversation.
- **Select a chat:** Switches to a conversation listed in the sidebar.
- **Clear current chat:** Clears the selected conversation's messages and attachments.
- **Delete all chats:** Resets the conversation list in the current session.
- **Remove attachment:** Removes a source document from the selected conversation.

---

## ðŸ“„ Supported File Formats

| Format | Upload | Export | Notes |
|---|---:|---:|---|
| TXT | Yes | Yes | Reads text using common encodings. |
| PDF | Yes | Yes | Upload extraction requires selectable text; scanned PDFs may need OCR. PDF export uses `fpdf2`. |
| DOCX | Yes | Yes | Reads paragraphs and tables; exports generated text to Word. |
| XLSX | No | Yes, conditionally | Export requires a compatible Markdown table and the relevant spreadsheet dependencies. |

### Upload limits and document handling

- The interface checks for a maximum of **20 MB per file** when the user clicks **Add files to conversation**.
- PDF, DOCX, and TXT uploads are supported.
- Extracted content is truncated to **80,000 characters per document**.
- When preparing a request, the code includes up to approximately **120,000 characters total** from attached source text in the model input.
- Files with no extractable text may produce a warning.
- Reusing a filename already attached to the same conversation will not add it again.

The upload size check is an application-level check; server and hosting upload limits may also apply.

---

## âš™ï¸ Configuration

The application defines the following settings:

| Setting | Purpose |
|---|---|
| `OPENAI_API_KEY` | API credential, read from Streamlit Secrets or the environment. |
| `OPENAI_MODEL` | Model identifier; defaults in the code to `gpt-6-luna`. |
| `DEFAULT_MODEL` | Fallback model string in the application source. |
| `SYSTEM_PROMPTS` | Instructions defining each administrative role. |

The current code uses Streamlit session state for conversations, messages, attachments, workflow selection, and status notices. This is session-oriented storage, not a permanent database. Do not assume conversations will survive a server restart or be shared across users.

---

## ðŸ› ï¸ Troubleshooting

### `ModuleNotFoundError: No module named 'streamlit'`

Activate your virtual environment and install the dependencies:

```bash
python -m pip install -r requirements.txt
```

### `ModuleNotFoundError: No module named 'openai'`

Install the SDK:

```bash
python -m pip install openai
```

### API error or Demo Mode keeps appearing

1. Confirm that `OPENAI_API_KEY` is set correctly in the environment or Streamlit Secrets.
2. Verify that the model ID configured in `OPENAI_MODEL` is supported by your API account.
3. Check the deployment logs for authentication, quota, network, or model-access errors.
4. Restart or redeploy after updating secrets.

Do not print or share the secret key when debugging.

### PDF export is unavailable

Install `fpdf2`:

```bash
python -m pip install fpdf2
```

### Word export is unavailable

Install `python-docx`:

```bash
python -m pip install python-docx
```

### Excel export says no valid table was found

Excel export expects a Markdown table with a header, separator row, and data rows. Ask the assistant to produce a clear Markdown table, then try exporting again. Make sure `pandas` and `openpyxl` are installed.

### PDF upload returns no text

The PDF may contain scanned page images rather than selectable text. OCR support is not included in the current code. Run OCR separately or upload a text-based PDF or TXT/DOCX version.

### The app deploys but the API does not work

Check the Streamlit Cloud logs, verify the secrets syntax, and ensure `app.py` is selected as the main file. Confirm the configured model is accessible through the Responses API.

---

## ðŸ”’ Security and Privacy

- Keep API keys in Streamlit Secrets or environment variables.
- Never commit credentials, private source documents, or `.streamlit/secrets.toml` to a public repository.
- Uploaded document text may be sent to the configured AI provider when a prompt is submitted. Do not upload confidential or sensitive material unless your organization has approved the data-handling arrangement.
- The application does not implement user authentication, role-based access control, persistent encrypted storage, or a database-backed audit trail.
- The role names represent AI workflow stages; they do not verify the identity or authority of a real administrative officer.
- Review generated text, calculations, names, dates, and decisions before using it in official work.
- Avoid logging or displaying API keys and confidential content during troubleshooting.

---

## âš ï¸ Known Limitations

1. **Demo output:** Demo mode returns a fixed sample response, not a real analysis of the submitted request.
2. **No persistent database:** Chat state is stored in Streamlit session state.
3. **No actual official approval:** â€œSanctionedâ€ or â€œapprovedâ€ wording is generated by the model or demo response and is not institutional authorization.
4. **Model compatibility:** The default model string may need to be changed to one available to the configured API account.
5. **Document context:** Extracted text is bounded by character limits; formatting, images, and some document structures may not be preserved.
6. **Scanned PDFs:** OCR is not implemented.
7. **Excel export:** Only detected Markdown tables are exported; arbitrary prose is not converted into a spreadsheet.
8. **PDF layout:** PDF generation is text-focused and does not reproduce the complete Markdown layout or embedded images.
9. **Error visibility:** Some API failures fall back to demo output; consult server logs to diagnose the underlying issue.
10. **No authentication:** The current app is not designed as a secure multi-user records-management system.

---

## ðŸ—ºï¸ Roadmap

Possible future improvements:

- Persistent database-backed conversations and document metadata.
- User login, authorization, and access controls.
- Audit logs with timestamps and workflow status.
- Explicit human approval controls before marking a document as approved.
- More robust Markdown-to-PDF formatting and page headers/footers.
- OCR support for scanned PDFs.
- Better API error messages and a visible distinction between live AI output and demo output.
- Document size and token-budget controls.
- Configurable retention and deletion policies for uploaded documents.

---

## ðŸ‘¨â€ðŸ’» Credits

**Project:** BAITHAK WITH AI  
**Designed by:** Engr. Bilal Mehmood  
**Focus:** Generative AI, Agentic AI, administrative workflow assistance, and document automation.

---

## ðŸ“œ License

No license has been specified in the supplied application code. Before making the repository public or distributing the software, add a `LICENSE` file stating the terms under which others may use, modify, and redistribute it. Until then, do not assume that the project is open-source or freely reusable.
