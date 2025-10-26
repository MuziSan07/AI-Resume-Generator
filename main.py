import streamlit as st
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableSequence
from langchain_core.output_parsers import StrOutputParser
import os
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from io import BytesIO

# Page configuration
st.set_page_config(
    page_title="ATS Resume Generator",
    page_icon="📄",
    layout="wide"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .section-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #2c3e50;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
        border-bottom: 2px solid #1f77b4;
        padding-bottom: 0.5rem;
    }
    .stTextArea textarea {
        font-size: 14px;
    }
    </style>
""", unsafe_allow_html=True)

# Title
st.markdown('<div class="main-header">🤖 AI-Powered ATS Resume Generator</div>', unsafe_allow_html=True)
st.markdown("Create a professional, ATS-friendly resume tailored to your target job using AI")

# Initialize session state
if 'resume_generated' not in st.session_state:
    st.session_state.resume_generated = False
if 'generated_resume' not in st.session_state:
    st.session_state.generated_resume = ""

# Sidebar for API Key
with st.sidebar:
    st.header("⚙️ Configuration")
    groq_api_key = st.text_input("Enter GROQ API Key", type="password", help="Get your API key from https://console.groq.com")
    
    st.markdown("---")
    st.markdown("### 📋 About")
    st.info("""
    This tool creates ATS-optimized resumes by:
    - Analyzing job descriptions
    - Highlighting relevant skills
    - Formatting for ATS systems
    - Using professional structure
    - Powered by Llama 3.3 70B
    """)
    
    st.markdown("---")
    st.markdown("### 📥 Export Formats")
    st.success("""
    ✅ TXT - Best for ATS systems
    ✅ PDF - Professional presentation
    """)
    
    if st.button("Clear All Data"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# Main content
if not groq_api_key:
    st.warning("⚠️ Please enter your GROQ API key in the sidebar to continue")
    st.stop()

# Initialize LLM
try:
    llm = ChatGroq(
        temperature=0.7,
        model_name="llama-3.3-70b-versatile",
        groq_api_key=groq_api_key
    )
except Exception as e:
    st.error(f"Error initializing GROQ API: {str(e)}")
    st.stop()

# Function to create PDF from resume text
def create_pdf(resume_text, full_name):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                           rightMargin=0.75*inch, leftMargin=0.75*inch,
                           topMargin=0.75*inch, bottomMargin=0.75*inch)
    
    # Container for the 'Flowable' objects
    elements = []
    
    # Define styles
    styles = getSampleStyleSheet()
    
    # Custom styles for resume
    name_style = ParagraphStyle(
        'NameStyle',
        parent=styles['Normal'],
        fontSize=18,
        textColor='#000000',
        spaceAfter=4,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold',
        leading=22
    )
    
    contact_style = ParagraphStyle(
        'ContactStyle',
        parent=styles['Normal'],
        fontSize=9,
        textColor='#333333',
        spaceAfter=12,
        alignment=TA_CENTER,
        fontName='Helvetica'
    )
    
    heading_style = ParagraphStyle(
        'HeadingStyle',
        parent=styles['Normal'],
        fontSize=11,
        textColor='#000000',
        spaceAfter=8,
        spaceBefore=14,
        fontName='Helvetica-Bold',
        leading=13
    )
    
    subheading_style = ParagraphStyle(
        'SubheadingStyle',
        parent=styles['Normal'],
        fontSize=10,
        textColor='#000000',
        spaceAfter=2,
        spaceBefore=6,
        fontName='Helvetica-Bold',
        leading=12
    )
    
    normal_style = ParagraphStyle(
        'NormalStyle',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=4,
        alignment=TA_LEFT,
        fontName='Helvetica',
        leading=12
    )
    
    bullet_style = ParagraphStyle(
        'BulletStyle',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=3,
        leftIndent=20,
        fontName='Helvetica',
        leading=12
    )
    
    # Split resume into lines and process
    lines = resume_text.split('\n')
    is_first_line = True
    is_second_line = False
    
    for i, line in enumerate(lines):
        line = line.strip()
        
        if not line:
            elements.append(Spacer(1, 0.08*inch))
            continue
        
        # Escape special characters for reportlab
        line_escaped = line.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        
        # First line (Name)
        if is_first_line and len(line) < 80:
            elements.append(Paragraph(line_escaped, name_style))
            is_first_line = False
            is_second_line = True
            continue
        
        # Second line (Contact info)
        if is_second_line and '|' in line:
            elements.append(Paragraph(line_escaped, contact_style))
            is_second_line = False
            continue
        
        # Section headers (ALL CAPS)
        if line.isupper() and len(line) > 3 and len(line) < 50:
            elements.append(Paragraph(line_escaped, heading_style))
        # Job titles or subheadings (contains em dash —)
        elif '—' in line and not line.startswith('•'):
            elements.append(Paragraph(line_escaped, subheading_style))
        # Bullet points
        elif line.startswith('•'):
            elements.append(Paragraph(line_escaped, bullet_style))
        # Location and date lines (contains |)
        elif '|' in line and any(month in line for month in ['01/', '02/', '03/', '04/', '05/', '06/', '07/', '08/', '09/', '10/', '11/', '12/', 'Present', 'Expected']):
            elements.append(Paragraph(line_escaped, normal_style))
        # Normal text
        else:
            elements.append(Paragraph(line_escaped, normal_style))
    
    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer

# Create two columns for better layout
col1, col2 = st.columns([1, 1])

with col1:
    st.markdown('<div class="section-header">👤 Personal Information</div>', unsafe_allow_html=True)
    
    full_name = st.text_input("Full Name *", placeholder="John Doe")
    email = st.text_input("Email *", placeholder="john.doe@email.com")
    phone = st.text_input("Phone Number *", placeholder="+1 (555) 123-4567")
    location = st.text_input("Location *", placeholder="New York, NY")
    linkedin = st.text_input("LinkedIn Profile (Optional)", placeholder="linkedin.com/in/johndoe")
    github = st.text_input("GitHub Profile (Optional)", placeholder="github.com/johndoe")
    portfolio = st.text_input("Portfolio/Website (Optional)", placeholder="johndoe.com")
    
    st.markdown('<div class="section-header">🎓 Education</div>', unsafe_allow_html=True)
    education = st.text_area(
        "Education Details *",
        placeholder="Example:\nBachelor of Science in Computer Science — University of California, Berkeley\n08/2016 – 05/2020\nGPA: 3.8/4.0",
        height=120
    )

with col2:
    st.markdown('<div class="section-header">💼 Target Job</div>', unsafe_allow_html=True)
    
    job_title = st.text_input("Target Job Title *", placeholder="Senior Software Engineer")
    job_description = st.text_area(
        "Job Description *",
        placeholder="Paste the complete job description here...",
        height=200
    )
    
    st.markdown('<div class="section-header">💡 Professional Summary</div>', unsafe_allow_html=True)
    professional_summary = st.text_area(
        "Brief Professional Summary (Optional)",
        placeholder="A brief overview of your professional background...",
        height=100
    )

st.markdown('<div class="section-header">🛠️ Skills</div>', unsafe_allow_html=True)
skills = st.text_area(
    "Your Skills *",
    placeholder="Example:\nProgramming Languages: Python, JavaScript, Java, C++\nFrameworks & Libraries: React, Django, Flask, FastAPI, Node.js\nDatabases: PostgreSQL, MongoDB, MySQL, Redis\nCloud & DevOps: AWS, Azure, Docker, Kubernetes, CI/CD\nTools: Git, Postman, VS Code, Linux\nSoft Skills: Leadership, Problem-solving, Team Collaboration",
    height=150
)

st.markdown('<div class="section-header">💼 Work Experience</div>', unsafe_allow_html=True)
work_experience = st.text_area(
    "Work Experience *",
    placeholder="Example:\n\nSoftware Engineer — Tech Corp Inc\nSan Francisco, CA | 06/2020 – Present\n• Built and deployed RESTful APIs with Python/FastAPI serving 10K+ monthly users\n• Integrated authentication, rate limiting, and logging using industry standards\n• Improved response latency by 40% by optimizing query structure and caching\n• Collaborated with frontend and data teams to deliver production-grade features\n\nJunior Developer — StartUp XYZ\nNew York, NY | 01/2018 – 05/2020\n• Designed microservices for AI-powered document processing pipeline\n• Automated CI/CD using GitHub Actions and Docker for seamless deploys",
    height=250
)

st.markdown('<div class="section-header">🚀 Projects</div>', unsafe_allow_html=True)
projects = st.text_area(
    "Key Projects *",
    placeholder="Example:\n\nAI Speech Transcription API — Full Stack Developer\n• Built AI-based speech transcription API using wav2vec2 + FastAPI + SQLite\n• Added token-based access, rate limiting, and an admin dashboard with analytics\n• Deployed on AWS EC2 with 99.9% uptime serving 5K+ requests daily\n\nRAG Chatbot System — Backend Developer\n• Developed LLM-based RAG chatbot with LangChain and Groq\n• Integrated role-based access for student/admin panels with JSON/MongoDB backend\n• Achieved 85% user satisfaction with response accuracy",
    height=200
)

st.markdown('<div class="section-header">🏆 Certifications (Optional)</div>', unsafe_allow_html=True)
certifications = st.text_area(
    "Certifications",
    placeholder="Example:\nAWS Certified Solutions Architect · Azure DP-100 · Google Data Analytics · CompTIA Security+",
    height=80
)

st.markdown('<div class="section-header">🌟 Achievements (Optional)</div>', unsafe_allow_html=True)
achievements = st.text_area(
    "Notable Achievements",
    placeholder="Example:\n• Published 3 AI-based projects on GitHub with 100+ stars\n• Ranked Top 1% in Kaggle Competition XYZ\n• Winner of ABC Hackathon 2023\n• Contributed to open-source projects with 50+ merged PRs\n• Mentored 10+ junior developers",
    height=120
)

# Generate Resume Button
st.markdown("---")
col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])

with col_btn2:
    generate_button = st.button("🚀 Generate ATS-Friendly Resume", use_container_width=True, type="primary")

if generate_button:
    # Validate required fields
    required_fields = {
        "Full Name": full_name,
        "Email": email,
        "Phone": phone,
        "Location": location,
        "Education": education,
        "Job Title": job_title,
        "Job Description": job_description,
        "Skills": skills,
        "Work Experience": work_experience,
        "Projects": projects
    }
    
    missing_fields = [field for field, value in required_fields.items() if not value.strip()]
    
    if missing_fields:
        st.error(f"❌ Please fill in the following required fields: {', '.join(missing_fields)}")
    else:
        with st.spinner("🤖 AI is crafting your ATS-friendly resume..."):
            try:
                # Create the prompt template
                resume_prompt = PromptTemplate(
                    input_variables=[
                        "full_name", "email", "phone", "location", "linkedin", "portfolio",
                        "job_title", "job_description", "professional_summary", "education",
                        "skills", "work_experience", "projects", "certifications"
                    ],
                    template="""You are an expert resume writer specializing in ATS (Applicant Tracking System) optimization. 
Create a professional, ATS-friendly resume following this EXACT format and structure:

**STRICT FORMATTING REQUIREMENTS:**
1. Name at top in ALL CAPS
2. Contact line: City, Country | Phone | Email | LinkedIn | Portfolio/GitHub (if provided)
3. Section headers in ALL CAPS with blank line before
4. Use bullet points (•) for job responsibilities and achievements
5. Use em dash (—) for separating job title and company
6. Use vertical bars (|) for separating location and dates
7. NO tables, columns, icons, or graphics
8. Keep it simple, clean, and text-only

**REQUIRED FORMAT:**

{full_name}
{location} | {phone} | {email} | {linkedin} | {portfolio}

PROFESSIONAL SUMMARY
Write 2-4 lines based on: {professional_summary}
If not provided, create a compelling summary highlighting experience for {job_title} role using keywords from job description.

CORE SKILLS
Extract and list relevant skills from: {skills}
Format: Skill1 · Skill2 · Skill3 · Skill4 (use middle dot · as separator)
Prioritize skills matching the job description: {job_description}

PROFESSIONAL EXPERIENCE
Format work experience from: {work_experience}
Use this structure:
Job Title — Company Name
Location | MM/YYYY – Present (or MM/YYYY – MM/YYYY)
• Achievement/responsibility with metrics
• Achievement/responsibility with metrics
• Achievement/responsibility with metrics
• Achievement/responsibility with metrics

PROJECTS
Format projects from: {projects}
Use this structure:
Project Name — Role
• Brief description with technologies used
• Key features and achievements with metrics if available

EDUCATION
Format education from: {education}
Use this structure:
Degree — University Name
MM/YYYY – MM/YYYY (or Expected MM/YYYY)

CERTIFICATIONS
List certifications from: {certifications}
Format: Certification1 · Certification2 · Certification3

ACHIEVEMENTS (if notable achievements exist)
List any significant achievements, rankings, or recognitions

**CRITICAL INSTRUCTIONS:**
- Analyze the job description and naturally incorporate relevant keywords
- Use action verbs: Built, Developed, Implemented, Designed, Improved, Led, etc.
- Include metrics and numbers wherever possible (%, $, time saved, users, etc.)
- Keep bullet points concise (1-2 lines max)
- Ensure proper spacing between sections
- Use consistent formatting throughout
- Make it ATS-friendly (no special characters except · — | • )

Job Description for keyword optimization:
{job_description}

Generate the complete resume now following this exact format."""
                )
                
                # Create the output parser
                output_parser = StrOutputParser()
                
                # Create and run the chain using RunnableSequence
                chain = RunnableSequence(resume_prompt | llm | output_parser)
                
                # Prepare input data
                input_data = {
                    "full_name": full_name,
                    "email": email,
                    "phone": phone,
                    "location": location,
                    "linkedin": linkedin if linkedin else "Not provided",
                    "portfolio": portfolio if portfolio else "Not provided",
                    "job_title": job_title,
                    "job_description": job_description,
                    "professional_summary": professional_summary if professional_summary else "Not provided",
                    "education": education,
                    "skills": skills,
                    "work_experience": work_experience,
                    "projects": projects,
                    "certifications": certifications if certifications else "Not provided"
                }
                
                # Invoke the chain
                resume_output = chain.invoke(input_data)
                
                # Check if response is blocked by content moderation
                if resume_output and resume_output.strip().lower() in ['safe', 'unsafe', '']:
                    st.error("❌ Content moderation triggered. Try rephrasing your input or use a different model.")
                    st.info("💡 Tip: Try removing any unusual characters or sensitive information from your inputs.")
                else:
                    st.session_state.generated_resume = resume_output
                    st.session_state.resume_generated = True
                    st.success("✅ Resume generated successfully!")
                
            except Exception as e:
                st.error(f"❌ Error generating resume: {str(e)}")
                st.info("💡 If you see 'safe' as output, this means the content was blocked by GROQ's moderation. Try using a different model or rephrasing your input.")

# Display generated resume
if st.session_state.resume_generated and st.session_state.generated_resume:
    st.markdown("---")
    st.markdown('<div class="section-header">📄 Your ATS-Friendly Resume</div>', unsafe_allow_html=True)
    
    # Display resume in a nice container
    st.text_area(
        "Generated Resume",
        value=st.session_state.generated_resume,
        height=600,
        label_visibility="collapsed"
    )
    
    # Download button
    col_dl1, col_dl2, col_dl3 = st.columns([1, 1, 1])
    
    with col_dl1:
        st.download_button(
            label="📥 Download as TXT",
            data=st.session_state.generated_resume,
            file_name=f"ATS_Resume_{full_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.txt",
            mime="text/plain",
            use_container_width=True
        )
    
    with col_dl3:
        # Generate PDF
        try:
            pdf_buffer = create_pdf(st.session_state.generated_resume, full_name)
            st.download_button(
                label="📄 Download as PDF",
                data=pdf_buffer,
                file_name=f"ATS_Resume_{full_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        except Exception as e:
            st.error(f"Error creating PDF: {str(e)}")
    
    # Tips section
    st.markdown("---")
    st.markdown('<div class="section-header">💡 ATS Optimization Tips</div>', unsafe_allow_html=True)
    
    tips_col1, tips_col2 = st.columns(2)
    
    with tips_col1:
        st.markdown("""
        **✅ Do's:**
        - Use standard section headings
        - Include relevant keywords from job description
        - Use simple bullet points
        - Save as .txt or .docx format
        - Use standard fonts (Arial, Calibri)
        """)
    
    with tips_col2:
        st.markdown("""
        **❌ Don'ts:**
        - Avoid tables and text boxes
        - Don't use headers/footers
        - Avoid graphics and images
        - Don't use special characters
        - Avoid columns layout
        """)

# Footer
st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: #7f8c8d; padding: 1rem;'>
        <p>💼 Built with Streamlit & LangChain | Powered by GROQ API</p>
    </div>
""", unsafe_allow_html=True)