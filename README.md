# ATS Resume Generator
### AI-Powered Resume Builder with Groq + LLaMA 3.3 70B

---

## Overview

ATS Resume Generator is a Streamlit web application that creates professionally formatted, ATS-optimized resumes tailored to specific job descriptions. It uses the Groq inference API with the LLaMA 3.3 70B model and LangChain to analyze job postings, extract relevant keywords, and produce clean, structured resumes — exportable as both TXT and PDF.

---

## Features

- Generates complete ATS-friendly resumes from user-provided profile data
- Analyzes job descriptions to incorporate relevant keywords automatically
- Exports finished resumes in TXT (best for ATS parsing) and PDF (professional presentation)
- PDF rendered with ReportLab — clean typography, proper section hierarchy
- Real-time validation of required fields before generation
- ATS optimization tips displayed alongside the generated output
- Session state management for smooth multi-step interaction
- Secure API key input via sidebar — no `.env` required at runtime

---

## Tech Stack

| Layer               | Technology                          |
|---------------------|-------------------------------------|
| Frontend/UI         | Streamlit                           |
| LLM Provider        | Groq (llama-3.3-70b-versatile)      |
| LLM Orchestration   | LangChain (PromptTemplate, RunnableSequence) |
| Output Parsing      | LangChain StrOutputParser           |
| PDF Generation      | ReportLab                           |
| Language            | Python 3.8+                         |

---

## Project Structure

```
ats-resume-generator/
│
├── app.py                  # Main Streamlit application
└── requirements.txt        # Python dependencies
```

No external assets are required. The API key is entered directly in the sidebar at runtime.

---

## Getting Started

### Prerequisites

- Python 3.8 or higher
- A valid Groq API key — obtain one at https://console.groq.com

### Installation

1. Clone the repository:

```bash
git clone https://github.com/your-username/ats-resume-generator.git
cd ats-resume-generator
```

2. Install the required dependencies:

```bash
pip install streamlit langchain-groq langchain-core reportlab
```

3. Run the application:

```bash
streamlit run app.py
```

4. Open your browser and navigate to:

```
http://localhost:8501
```

5. Enter your Groq API key in the sidebar to begin.

---

## Requirements

```
streamlit
langchain-groq
langchain-core
reportlab
```

Save the above to a `requirements.txt` file and install with:

```bash
pip install -r requirements.txt
```

---

## Usage

1. Enter your Groq API key in the sidebar
2. Fill in your personal information, education, and target job title
3. Paste the full job description into the designated field
4. Add your skills, work experience, and projects
5. Optionally add certifications and achievements
6. Click **Generate ATS-Friendly Resume**
7. Download the output as TXT or PDF

### Resume Output Format

The generated resume follows a strict ATS-compatible structure:

```
FULL NAME
Location | Phone | Email | LinkedIn | Portfolio

PROFESSIONAL SUMMARY
...

CORE SKILLS
Skill1 · Skill2 · Skill3

PROFESSIONAL EXPERIENCE
Job Title — Company Name
Location | MM/YYYY – Present
• Achievement with metric
• Achievement with metric

PROJECTS
Project Name — Role
• Description and technologies

EDUCATION
Degree — University
MM/YYYY – MM/YYYY

CERTIFICATIONS
Cert1 · Cert2

ACHIEVEMENTS
• Notable recognition
```

---

## Model Configuration

The LLM is initialized with the following parameters:

```python
model       = "llama-3.3-70b-versatile"
temperature = 0.7
```

These can be adjusted in `app.py` inside the LLM initialization block to control output creativity and consistency.

---

## PDF Generation

The PDF is rendered using ReportLab with a custom set of paragraph styles:

- Name: Centered, 18pt bold
- Contact line: Centered, 9pt
- Section headers: Detected by ALL CAPS pattern, 11pt bold
- Job titles: Detected by em dash presence, 10pt bold
- Bullet points: Left-indented, 10pt
- Body text: 10pt, left-aligned

The PDF renderer parses the plain text output of the LLM and applies appropriate styles automatically, requiring no manual formatting.

---

## Deployment

### Streamlit Community Cloud

1. Push the project to a public GitHub repository
2. Visit https://share.streamlit.io
3. Connect your GitHub account and select the repository
4. Set `app.py` as the entry point
5. Deploy — no secrets configuration required (API key is entered in the UI at runtime)

---

## ATS Optimization Notes

The generated resumes are designed to pass ATS parsers by following these principles:

- Plain text structure with no tables, columns, or graphics
- Standard section headings recognizable by all major ATS platforms
- Keyword injection based on the provided job description
- Consistent use of action verbs with quantified achievements
- Only ATS-safe characters used: `•`, `—`, `|`, `·`

---

## Author

Built with Streamlit and LangChain, powered by the Groq API.

---

## License

This project is open for personal and commercial use. Attribution appreciated.
