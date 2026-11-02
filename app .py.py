import json
import re
import time
from datetime import datetime
from typing import Any

import plotly.graph_objects as go
import plotly.express as px
import streamlit as st
from groq import Groq
from groq import (
    APIConnectionError,
    APITimeoutError,
    AuthenticationError,
    BadRequestError,
    RateLimitError,
    APIStatusError,
)

# ---------------------------------------------------------------------
# AI INTERVIEW PRACTICE — Your Personal AI Interview Coach
# ---------------------------------------------------------------------

st.set_page_config(
    page_title="AI Interview Practice | Your Personal AI Coach",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

APP_NAME = "AI Interview Practice"
DEFAULT_MODEL = "openai/gpt-oss-20b"
ROLES = [
    "Python Developer", "Frontend Developer", "Backend Developer",
    "Full Stack Developer", "Data Scientist", "Data Analyst",
    "Machine Learning Engineer", "AI Engineer", "UI/UX Designer",
    "Cybersecurity Analyst", "Software Engineer",
    "Digital Marketing Specialist", "Custom Job Role",
]
EXPERIENCE_LEVELS = ["Fresh Graduate", "Entry Level", "Junior", "Mid-Level", "Senior"]
DIFFICULTIES = ["Easy", "Intermediate", "Advanced"]
INTERVIEW_TYPES = [
    "Technical Interview", "HR Interview", "Behavioral Interview", "Mixed Interview"
]
QUESTION_COUNTS = [5, 10, 15, 20]

# ---------------------------------------------------------------------
# Styling
# ---------------------------------------------------------------------

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap');

    :root {
        --bg: #080d1a;
        --panel: rgba(17, 27, 49, .82);
        --panel2: rgba(22, 34, 59, .78);
        --line: rgba(133, 163, 219, .17);
        --muted: #93a4c3;
        --text: #edf3ff;
        --blue: #4f8cff;
        --purple: #9b72ff;
        --cyan: #4bd8e8;
    }
    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif;
    }
    .stApp {
        background:
          radial-gradient(ellipse at 8% 0%, rgba(64, 111, 225, .17), transparent 34%),
          radial-gradient(ellipse at 92% 10%, rgba(139, 82, 235, .13), transparent 31%),
          linear-gradient(135deg, #080d1a 0%, #0a1222 52%, #090e1c 100%);
        color: var(--text);
    }
    [data-testid="stHeader"] { background: rgba(8,13,26,.55); }
    [data-testid="stToolbar"], #MainMenu, footer { visibility: hidden; }
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0d1629 0%, #0a1120 100%);
        border-right: 1px solid var(--line);
    }
    [data-testid="stSidebar"] > div { padding-top: 1.2rem; }
    .block-container { padding-top: 2rem; padding-bottom: 3rem; max-width: 1440px; }
    h1, h2, h3, h4 { font-family: 'Manrope', sans-serif !important; color: #f2f6ff !important; }
    p, label, span, div { }
    .brand {
        font-family: 'Manrope', sans-serif;
        font-size: 1.12rem; font-weight: 800; letter-spacing: -.4px;
        color: #f4f7ff; padding: 0 0 .25rem 0;
    }
    .brand-mark {
        display:inline-flex; width:34px; height:34px; align-items:center; justify-content:center;
        border-radius:11px; margin-right:9px; color:white; font-weight:800;
        background: linear-gradient(135deg,#438cff,#9b72ff);
        box-shadow: 0 7px 25px rgba(83,121,255,.35);
    }
    .muted { color: var(--muted); }
    .eyebrow {
        color: #81aaff; font-size: .75rem; text-transform: uppercase;
        letter-spacing: 2px; font-weight: 800;
    }
    .hero {
        position:relative; overflow:hidden; padding: 30px 32px;
        border:1px solid rgba(125,158,231,.24); border-radius:24px;
        background: linear-gradient(115deg, rgba(26,48,88,.94), rgba(38,34,79,.82) 62%, rgba(23,35,63,.91));
        box-shadow: 0 18px 60px rgba(0,0,0,.22);
        margin-bottom: 24px;
    }
    .hero:after {
        content:""; position:absolute; width:260px; height:260px; right:-65px; top:-130px;
        border-radius:50%; background:rgba(106,139,255,.16); filter:blur(5px);
    }
    .hero h1 { font-size: clamp(1.8rem, 4vw, 2.8rem); margin:.45rem 0 .55rem; letter-spacing:-1.5px; }
    .hero p { color:#b8c7e4; max-width:700px; margin:0; line-height:1.7; }
    .metric-card, .surface, .question-card, .feedback-card, .tip-card {
        background: var(--panel); border:1px solid var(--line); border-radius:18px;
        box-shadow: 0 12px 35px rgba(0,0,0,.14);
        transition: transform .22s ease, border-color .22s ease, box-shadow .22s ease;
    }
    .metric-card { padding:19px 20px; min-height:125px; }
    .metric-card:hover, .surface:hover, .tip-card:hover {
        transform: translateY(-3px); border-color:rgba(101,151,255,.42);
        box-shadow:0 15px 38px rgba(36,83,175,.13);
    }
    .metric-label { color:#9aabc9; font-size:.83rem; font-weight:600; }
    .metric-value { color:#f5f8ff; font-family:'Manrope'; font-size:1.9rem; font-weight:800; margin-top:7px; }
    .metric-foot { color:#7488aa; font-size:.76rem; margin-top:3px; }
    .surface { padding:22px; margin-bottom:16px; }
    .question-card {
        padding:28px; margin:14px 0 18px;
        background:linear-gradient(145deg,rgba(24,40,70,.95),rgba(18,28,51,.94));
        border-color:rgba(95,139,232,.28);
    }
    .question-number { color:#8fb4ff; font-size:.78rem; letter-spacing:1.4px; font-weight:800; text-transform:uppercase; }
    .question-text { font-family:'Manrope'; font-size:1.45rem; font-weight:700; line-height:1.5; color:#f2f6ff; margin-top:12px; }
    .feedback-card { padding:20px; margin:12px 0; }
    .score-pill {
        display:inline-block; padding:7px 13px; border-radius:999px;
        background:rgba(77,143,255,.14); color:#9bc0ff; border:1px solid rgba(77,143,255,.3);
        font-weight:800; font-size:.85rem;
    }
    .tag {
        display:inline-block; padding:5px 10px; margin:3px 5px 3px 0; border-radius:8px;
        background:rgba(124,145,190,.12); border:1px solid rgba(124,145,190,.16);
        color:#bdcbea; font-size:.76rem;
    }
    .callout {
        padding:14px 16px; border-radius:13px; background:rgba(69,133,255,.10);
        border:1px solid rgba(69,133,255,.22); color:#c9d9f7; margin:12px 0;
    }
    .stButton > button {
        border:1px solid rgba(112,151,237,.30); border-radius:12px;
        background:linear-gradient(110deg,#367cf0,#7656df); color:white;
        font-weight:700; padding:.62rem 1.1rem; min-height:44px;
        box-shadow:0 7px 22px rgba(67,105,220,.20);
        transition:all .2s ease;
    }
    .stButton > button:hover {
        border-color:rgba(165,190,255,.75); transform:translateY(-2px);
        box-shadow:0 10px 28px rgba(79,121,255,.30); color:white;
    }
    .stButton > button:focus { box-shadow:0 0 0 2px rgba(100,151,255,.35); }
    .stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] > div,
    .stNumberInput input {
        background:#111c31 !important; color:#edf3ff !important;
        border-color:rgba(126,154,211,.25) !important; border-radius:11px !important;
    }
    .stTextArea textarea { line-height:1.65; }
    div[data-testid="stProgressBar"] > div > div { background:linear-gradient(90deg,#438cff,#9b72ff); }
    .stRadio [role="radiogroup"] { gap:7px; }
    .stRadio label { color:#c6d3ec !important; }
    [data-testid="stMetric"] {
        background:rgba(20,32,55,.75); border:1px solid var(--line);
        padding:14px 16px; border-radius:15px;
    }
    [data-testid="stAlert"] { border-radius:13px; }
    .section-title { font-family:'Manrope'; font-weight:800; font-size:1.3rem; margin:8px 0 14px; }
    .small-note { color:#8294b4; font-size:.8rem; }
    .sidebar-foot { color:#7284a5; font-size:.75rem; border-top:1px solid var(--line); padding-top:14px; margin-top:22px; }
    @media (max-width: 700px) {
        .block-container { padding:1rem .8rem 2rem; }
        .hero { padding:22px 20px; border-radius:18px; }
        .question-card { padding:20px; }
        .question-text { font-size:1.15rem; }
        .metric-value { font-size:1.55rem; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------
# Session state
# ---------------------------------------------------------------------

def init_state() -> None:
    defaults = {
        "page": "Dashboard",
        "interview": None,
        "history": [],
        "last_role": "Python Developer",
        "last_setup": {},
        "notice": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


init_state()


def safe_rerun() -> None:
    st.rerun()


def get_config() -> tuple[str | None, str]:
    """Read credentials only from Streamlit Secrets; never from source code."""
    try:
        api_key = str(st.secrets.get("GROQ_API_KEY", "")).strip()
        model = str(st.secrets.get("GROQ_MODEL", DEFAULT_MODEL)).strip() or DEFAULT_MODEL
    except Exception:
        return None, DEFAULT_MODEL
    return (api_key or None), model


@st.cache_resource(show_spinner=False)
def get_groq_client(api_key: str) -> Groq:
    return Groq(api_key=api_key, timeout=60.0, max_retries=1)


def call_groq_json(client: Groq, model: str, system_prompt: str, user_prompt: str,
                   max_tokens: int = 3000, temperature: float = 0.35) -> dict[str, Any]:
    """Call the one configured model and parse a JSON-object response."""
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=temperature,
        max_completion_tokens=max_tokens,
        response_format={"type": "json_object"},
    )
    content = response.choices[0].message.content or ""
    content = content.strip()
    if not content:
        raise ValueError("The AI returned an empty response. Please try again.")
    try:
        parsed = json.loads(content)
    except json.JSONDecodeError:
        # Defensive extraction for providers/models that wrap JSON in fences.
        match = re.search(r"\{.*\}", content, flags=re.DOTALL)
        if not match:
            raise ValueError("The AI response was not valid JSON. Please retry the action.")
        parsed = json.loads(match.group(0))
    if not isinstance(parsed, dict):
        raise ValueError("The AI response format was unexpected. Please retry.")
    return parsed


def friendly_api_error(exc: Exception) -> str:
    if isinstance(exc, AuthenticationError):
        return "Groq rejected the API key. Check GROQ_API_KEY in Streamlit Secrets."
    if isinstance(exc, RateLimitError):
        return "Groq rate limit reached. Wait a little, then try again."
    if isinstance(exc, (APIConnectionError, APITimeoutError)):
        return "Could not connect to Groq. Check your connection and try again."
    if isinstance(exc, BadRequestError):
        return "Groq rejected the request. Check that GROQ_MODEL is available to your account and supports chat completions."
    if isinstance(exc, APIStatusError):
        return f"Groq returned an API error (HTTP {exc.status_code}). Check model access and try again."
    if isinstance(exc, ValueError):
        return str(exc)
    return f"Something went wrong while contacting the AI service: {type(exc).__name__}. Please try again."


def require_client() -> tuple[Groq | None, str | None, str]:
    api_key, model = get_config()
    if not api_key:
        return None, "Add GROQ_API_KEY to Streamlit Cloud → App → Settings → Secrets.", model
    try:
        return get_groq_client(api_key), None, model
    except Exception as exc:
        return None, friendly_api_error(exc), model


def clean_string_list(value: Any, limit: int = 8) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item).strip() for item in value[:limit] if str(item).strip()]


def clamp_score(value: Any) -> int:
    try:
        return max(0, min(100, int(round(float(value)))))
    except (TypeError, ValueError):
        return 0


# ---------------------------------------------------------------------
# AI workflows
# ---------------------------------------------------------------------

def generate_questions(client: Groq, model: str, setup: dict[str, Any]) -> list[str]:
    system = (
        "You are an expert technical recruiter and interview designer. "
        "Return only a valid JSON object. Create realistic, role-specific interview questions. "
        "Questions must be distinct, progressively useful, and appropriate to the candidate's level."
    )
    user = f"""
Create exactly {setup['question_count']} interview questions.
Job role: {setup['role']}
Experience level: {setup['experience']}
Difficulty: {setup['difficulty']}
Interview type: {setup['interview_type']}
Job description (optional context): {setup.get('job_description') or 'Not provided'}

For a technical interview, emphasize role-relevant concepts and practical problem solving.
For HR/behavioral interviews, ask realistic workplace and experience questions.
For mixed interviews, balance technical, behavioral, and communication questions.
Avoid trivia and avoid asking multiple unrelated questions in one item.

Return JSON in this exact shape:
{{"questions":["question 1","question 2"]}}
"""
    data = call_groq_json(client, model, system, user, max_tokens=3500, temperature=0.45)
    questions = clean_string_list(data.get("questions"), limit=setup["question_count"])
    if len(questions) != setup["question_count"]:
        raise ValueError(
            f"The AI generated {len(questions)} usable questions instead of "
            f"{setup['question_count']}. Please generate the interview again."
        )
    return questions


def evaluate_answer(client: Groq, model: str, setup: dict[str, Any],
                    question: str, answer: str, question_index: int) -> dict[str, Any]:
    system = (
        "You are a fair, constructive, experienced interviewer and career coach. "
        "Assess only the answer provided; do not invent candidate experience. "
        "Be specific, balanced, and practical. Return only valid JSON."
    )
    user = f"""
Evaluate this interview answer.

Role: {setup['role']}
Experience level: {setup['experience']}
Difficulty: {setup['difficulty']}
Interview type: {setup['interview_type']}
Question number: {question_index + 1}
Interview question: {question}
Candidate answer: {answer}

Score each dimension from 0 to 100:
- relevance
- technical_accuracy
- clarity_communication
- completeness
- problem_solving
- professional_presentation

The overall_score must be a fair weighted overall score from 0 to 100.
For non-technical questions, judge technical_accuracy as role knowledge/context accuracy,
not as a penalty for not writing code.
Provide concise, actionable feedback and a strong sample answer appropriate to the stated level.
Do not claim the candidate said anything that is absent from their answer.

Return this JSON shape:
{{
  "overall_score": 0,
  "scores": {{
    "relevance": 0,
    "technical_accuracy": 0,
    "clarity_communication": 0,
    "completeness": 0,
    "problem_solving": 0,
    "professional_presentation": 0
  }},
  "strengths": ["..."],
  "improvements": ["..."],
  "missing_points": ["..."],
  "sample_answer": "...",
  "recommendations": ["..."],
  "short_feedback": "..."
}}
"""
    data = call_groq_json(client, model, system, user, max_tokens=3000, temperature=0.25)
    raw_scores = data.get("scores", {})
    dimensions = [
        "relevance", "technical_accuracy", "clarity_communication",
        "completeness", "problem_solving", "professional_presentation"
    ]
    scores = {key: clamp_score(raw_scores.get(key, 0)) for key in dimensions}
    overall = clamp_score(data.get("overall_score", sum(scores.values()) / len(scores)))
    return {
        "overall_score": overall,
        "scores": scores,
        "strengths": clean_string_list(data.get("strengths"), 6),
        "improvements": clean_string_list(data.get("improvements"), 6),
        "missing_points": clean_string_list(data.get("missing_points"), 6),
        "sample_answer": str(data.get("sample_answer", "")).strip(),
        "recommendations": clean_string_list(data.get("recommendations"), 6),
        "short_feedback": str(data.get("short_feedback", "")).strip(),
    }


def build_final_report(client: Groq, model: str, interview: dict[str, Any]) -> dict[str, Any]:
    evaluations = interview["evaluations"]
    scores = [item["overall_score"] for item in evaluations]
    dimension_names = {
        "relevance": "Answer relevance",
        "technical_accuracy": "Role knowledge",
        "clarity_communication": "Communication",
        "completeness": "Completeness",
        "problem_solving": "Problem solving",
        "professional_presentation": "Professional presentation",
    }
    dimension_avgs = {
        key: round(sum(item["scores"][key] for item in evaluations) / len(evaluations))
        for key in dimension_names
    }
    system = (
        "You are a senior interview coach. Produce an evidence-based final assessment "
        "from the supplied interview scores and feedback. Never fabricate achievements. "
        "Return only valid JSON."
    )
    user = f"""
Create a personalized interview performance report.

Interview setup: {json.dumps(interview['setup'], ensure_ascii=False)}
Question scores: {json.dumps(scores)}
Average dimension scores: {json.dumps(dimension_avgs)}
Per-question feedback: {json.dumps([
    {'question': interview['questions'][i], 'score': e['overall_score'],
     'strengths': e['strengths'], 'improvements': e['improvements']}
    for i, e in enumerate(evaluations)
], ensure_ascii=False)}

Return JSON:
{{
  "summary": "A concise, personalized overall assessment.",
  "strongest_areas": ["..."],
  "weakest_areas": ["..."],
  "technical_assessment": "Role knowledge assessment grounded in scores.",
  "communication_assessment": "Communication assessment grounded in scores.",
  "recommendations": ["..."],
  "learning_roadmap": [
    {{"timeframe":"Week 1","focus":"...","actions":["...","..."]}}
  ]
}}
"""
    report = call_groq_json(client, model, system, user, max_tokens=2600, temperature=0.3)
    report["summary"] = str(report.get("summary", "")).strip()
    report["strongest_areas"] = clean_string_list(report.get("strongest_areas"), 6)
    report["weakest_areas"] = clean_string_list(report.get("weakest_areas"), 6)
    report["recommendations"] = clean_string_list(report.get("recommendations"), 8)
    report["technical_assessment"] = str(report.get("technical_assessment", "")).strip()
    report["communication_assessment"] = str(report.get("communication_assessment", "")).strip()
    roadmap = report.get("learning_roadmap", [])
    report["learning_roadmap"] = roadmap if isinstance(roadmap, list) else []
    report["dimension_averages"] = dimension_avgs
    report["average_score"] = round(sum(scores) / len(scores)) if scores else 0
    report["best_score"] = max(scores) if scores else 0
    return report


# ---------------------------------------------------------------------
# Reusable UI and data helpers
# ---------------------------------------------------------------------

def html_metric(label: str, value: str, foot: str, icon: str) -> None:
    st.markdown(
        f"""
        <div class="metric-card">
          <div style="font-size:1.25rem;margin-bottom:8px">{icon}</div>
          <div class="metric-label">{label}</div>
          <div class="metric-value">{value}</div>
          <div class="metric-foot">{foot}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def section_heading(title: str, subtitle: str | None = None) -> None:
    st.markdown(f'<div class="section-title">{title}</div>', unsafe_allow_html=True)
    if subtitle:
        st.markdown(f'<div class="small-note" style="margin-top:-9px;margin-bottom:15px">{subtitle}</div>',
                    unsafe_allow_html=True)


def average_history_score() -> int:
    scores = [item.get("average_score", 0) for item in st.session_state.history]
    return round(sum(scores) / len(scores)) if scores else 0


def all_completed_evaluations() -> list[dict[str, Any]]:
    return [
        evaluation
        for session in st.session_state.history
        for evaluation in session.get("evaluations", [])
    ]


def make_report_text(interview: dict[str, Any]) -> str:
    report = interview.get("final_report", {})
    lines = [
        "AI INTERVIEW PRACTICE — PERFORMANCE REPORT",
        "=" * 52,
        f"Role: {interview['setup']['role']}",
        f"Experience: {interview['setup']['experience']}",
        f"Difficulty: {interview['setup']['difficulty']}",
        f"Interview type: {interview['setup']['interview_type']}",
        f"Completed: {interview.get('completed_at', 'N/A')}",
        f"Overall score: {report.get('average_score', 0)}/100",
        "",
        "SUMMARY",
        report.get("summary", "Report summary unavailable."),
        "",
        "QUESTION-BY-QUESTION RESULTS",
    ]
    for idx, (question, answer, evaluation) in enumerate(
        zip(interview["questions"], interview["answers"], interview["evaluations"]), start=1
    ):
        lines.extend([
            f"\n{idx}. {question}",
            f"Answer: {answer}",
            f"Score: {evaluation['overall_score']}/100",
            f"Feedback: {evaluation.get('short_feedback', '')}",
            "Strengths: " + "; ".join(evaluation.get("strengths", [])),
            "Improvements: " + "; ".join(evaluation.get("improvements", [])),
        ])
    for title, key in [
        ("STRONGEST AREAS", "strongest_areas"),
        ("AREAS TO IMPROVE", "weakest_areas"),
        ("RECOMMENDATIONS", "recommendations"),
    ]:
        lines.extend(["", title])
        lines.extend(["- " + item for item in report.get(key, [])])
    lines.extend(["", "TECHNICAL ASSESSMENT", report.get("technical_assessment", "")])
    lines.extend(["", "COMMUNICATION ASSESSMENT", report.get("communication_assessment", "")])
    lines.extend(["", "LEARNING ROADMAP"])
    for item in report.get("learning_roadmap", []):
        if isinstance(item, dict):
            lines.append(f"{item.get('timeframe', 'Next')}: {item.get('focus', '')}")
            lines.extend(["  - " + str(action) for action in item.get("actions", [])])
    return "\n".join(lines)


def score_color(score: int) -> str:
    if score >= 80:
        return "#42d6a4"
    if score >= 60:
        return "#f4c66a"
    return "#ff7d91"


def render_radar(dimension_averages: dict[str, int]) -> None:
    labels = [
        "Relevance", "Role knowledge", "Communication",
        "Completeness", "Problem solving", "Presentation"
    ]
    keys = [
        "relevance", "technical_accuracy", "clarity_communication",
        "completeness", "problem_solving", "professional_presentation"
    ]
    values = [dimension_averages.get(key, 0) for key in keys]
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values + [values[0]], theta=labels + [labels[0]], fill="toself",
        line=dict(color="#6d91ff", width=2),
        fillcolor="rgba(109,145,255,.20)",
        name="Your performance",
    ))
    fig.update_layout(
        polar=dict(
            bgcolor="rgba(12,20,36,.4)",
            radialaxis=dict(visible=True, range=[0, 100], gridcolor="rgba(145,166,210,.16)",
                            tickfont=dict(color="#8fa2c5", size=9)),
            angularaxis=dict(gridcolor="rgba(145,166,210,.14)", tickfont=dict(color="#c5d2eb", size=10)),
        ),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#c5d2eb"), margin=dict(l=35, r=35, t=20, b=20),
        height=350, showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def render_score_bars(evaluations: list[dict[str, Any]], questions: list[str]) -> None:
    labels = [f"Q{i + 1}" for i in range(len(evaluations))]
    values = [e["overall_score"] for e in evaluations]
    fig = px.bar(
        x=labels, y=values, text=values,
        labels={"x": "Interview question", "y": "Score"},
    )
    fig.update_traces(
        marker_color="#648fff", marker_line_color="#9c8cff", marker_line_width=1,
        textposition="outside", cliponaxis=False,
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#c5d2eb"), yaxis=dict(range=[0, 112], gridcolor="rgba(145,166,210,.13)"),
        xaxis=dict(gridcolor="rgba(0,0,0,0)"), margin=dict(l=10, r=10, t=25, b=10),
        height=320,
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def create_interview_record(interview: dict[str, Any]) -> dict[str, Any]:
    report = interview["final_report"]
    return {
        "role": interview["setup"]["role"],
        "completed_at": interview.get("completed_at", datetime.now().strftime("%d %b %Y, %I:%M %p")),
        "average_score": report.get("average_score", 0),
        "best_score": report.get("best_score", 0),
        "question_count": len(interview["questions"]),
        "evaluations": interview["evaluations"],
        "questions": interview["questions"],
    }


# ---------------------------------------------------------------------
# Sidebar navigation
# ---------------------------------------------------------------------

with st.sidebar:
    st.markdown(
        '<div class="brand"><span class="brand-mark">AI</span>Interview Coach</div>',
        unsafe_allow_html=True,
    )
    st.markdown('<div class="small-note" style="margin:4px 0 20px 2px">PRACTICE. IMPROVE. GET HIRED.</div>',
                unsafe_allow_html=True)

    nav_items = [
        ("Dashboard", "⌂", "Your overview"),
        ("Start Interview", "✦", "Practice session"),
        ("Interview History", "◷", "Past sessions"),
        ("Performance Analytics", "▥", "Your progress"),
        ("Interview Tips", "✧", "Expert guidance"),
        ("About", "ⓘ", "The platform"),
    ]
    current_page = st.session_state.page
    for page_name, symbol, helper in nav_items:
        if st.button(
            f"{symbol}   {page_name}",
            key=f"nav_{page_name}",
            use_container_width=True,
            type="primary" if current_page == page_name else "secondary",
        ):
            st.session_state.page = page_name
            safe_rerun()

    active = st.session_state.interview
    if active:
        st.markdown("---")
        st.markdown("**Active interview**")
        st.caption(active["setup"]["role"])
        done = len(active["evaluations"])
        st.progress(done / len(active["questions"]))
        st.caption(f"{done} of {len(active['questions'])} answered")

    st.markdown(
        '<div class="sidebar-foot">Built for focused interview preparation.<br>AI feedback is guidance, not a hiring decision.</div>',
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------
# Shared header
# ---------------------------------------------------------------------

api_key, configured_model = get_config()
with st.container():
    col_brand, col_status = st.columns([4, 1])
    with col_brand:
        st.markdown(
            f'<div class="eyebrow">PERSONAL CAREER DEVELOPMENT</div>',
            unsafe_allow_html=True,
        )
    with col_status:
        if api_key:
            st.markdown(
                '<div style="text-align:right;color:#5ed9ad;font-size:.78rem;font-weight:700">● AI CONFIGURED</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                '<div style="text-align:right;color:#f0bd69;font-size:.78rem;font-weight:700">● SETUP REQUIRED</div>',
                unsafe_allow_html=True,
            )


# ---------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------

def render_dashboard() -> None:
    completed = len(st.session_state.history)
    avg_score = average_history_score()
    best_score = max([x.get("best_score", 0) for x in st.session_state.history], default=0)
    answered = sum(x.get("question_count", 0) for x in st.session_state.history)
    last_role = st.session_state.last_role

    st.markdown(
        f"""
        <div class="hero">
          <div class="eyebrow">YOUR PERSONAL AI INTERVIEW COACH</div>
          <h1>Turn interview nerves into<br><span style="background:linear-gradient(90deg,#83b4ff,#b39aff);-webkit-background-clip:text;color:transparent">career confidence.</span></h1>
          <p>Practice realistic interviews, get actionable feedback on every answer, and build the skills to walk into your next interview prepared.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    m1, m2, m3, m4 = st.columns(4)
    with m1: html_metric("Completed interviews", str(completed), "This browser session", "🎯")
    with m2: html_metric("Questions answered", str(answered), "Across completed sessions", "✍️")
    with m3: html_metric("Average score", f"{avg_score}%" if completed else "—", "Completed interviews", "📈")
    with m4: html_metric("Best answer score", f"{best_score}%" if completed else "—", "Across completed sessions", "🏆")

    st.write("")
    left, right = st.columns([1.35, 1])
    with left:
        st.markdown('<div class="surface">', unsafe_allow_html=True)
        section_heading("Ready for your next interview?", "Build confidence with a tailored AI-powered practice session.")
        st.markdown(
            f'<div class="tag">Suggested role · {last_role}</div>'
            '<div class="tag">Personalized questions</div><div class="tag">Instant coaching</div>',
            unsafe_allow_html=True,
        )
        if st.button("✦  Start a new interview", key="dashboard_start", use_container_width=True):
            st.session_state.page = "Start Interview"
            safe_rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    with right:
        st.markdown('<div class="surface">', unsafe_allow_html=True)
        section_heading("Your practice snapshot")
        if st.session_state.history:
            latest = st.session_state.history[-1]
            st.markdown(f"**Latest role:** {latest['role']}")
            st.markdown(f"**Latest score:** {latest['average_score']} / 100")
            st.markdown(f"**Completed:** {latest['completed_at']}")
            st.progress(latest["average_score"] / 100)
        else:
            st.markdown(
                '<div class="callout">Your progress will appear here after you complete your first interview. No sample history is shown.</div>',
                unsafe_allow_html=True,
            )
        st.markdown("</div>", unsafe_allow_html=True)

    if st.session_state.history:
        section_heading("Recent activity", "Your latest completed practice sessions.")
        for item in reversed(st.session_state.history[-4:]):
            c1, c2, c3 = st.columns([3, 1, 1])
            c1.markdown(f"**{item['role']}**<div class='small-note'>{item['completed_at']}</div>", unsafe_allow_html=True)
            c2.metric("Score", f"{item['average_score']}%")
            c3.metric("Questions", item["question_count"])


# ---------------------------------------------------------------------
# Interview setup and active session
# ---------------------------------------------------------------------

def render_setup() -> None:
    st.markdown(
        """
        <div class="hero">
          <div class="eyebrow">PERSONALIZED PRACTICE SESSION</div>
          <h1>Set up your interview.</h1>
          <p>Choose the role and interview format. Your AI coach will tailor every question to your goals and experience.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.session_state.interview and not st.session_state.interview.get("completed"):
        active = st.session_state.interview
        st.markdown(
            f'<div class="callout">You have an interview in progress for <b>{active["setup"]["role"]}</b>. '
            f'{len(active["evaluations"])} of {len(active["questions"])} questions completed.</div>',
            unsafe_allow_html=True,
        )
        if st.button("↗  Resume active interview", key="resume_active"):
            st.session_state.page = "Start Interview"
            safe_rerun()

    previous = st.session_state.last_setup
    with st.form("interview_setup_form", clear_on_submit=False):
        st.markdown("#### Interview preferences")
        a, b = st.columns(2)
        with a:
            role = st.selectbox("Job role", ROLES, index=ROLES.index(previous.get("role", "Python Developer"))
                                if previous.get("role", "Python Developer") in ROLES else 0)
            custom_role = ""
            if role == "Custom Job Role":
                custom_role = st.text_input("Enter your custom job role", value=previous.get("custom_role", ""),
                                            placeholder="e.g. Cloud Solutions Architect")
            experience = st.selectbox("Experience level", EXPERIENCE_LEVELS,
                                      index=EXPERIENCE_LEVELS.index(previous.get("experience", "Fresh Graduate")))
            difficulty = st.selectbox("Interview difficulty", DIFFICULTIES,
                                      index=DIFFICULTIES.index(previous.get("difficulty", "Intermediate")))
        with b:
            interview_type = st.selectbox("Interview type", INTERVIEW_TYPES,
                                          index=INTERVIEW_TYPES.index(previous.get("interview_type", "Mixed Interview")))
            question_count = st.selectbox("Number of questions", QUESTION_COUNTS,
                                          index=QUESTION_COUNTS.index(previous.get("question_count", 5)))
            st.markdown('<div class="small-note">A full session may take several minutes depending on the number of questions and API response time.</div>',
                        unsafe_allow_html=True)
        job_description = st.text_area(
            "Job description (optional)",
            value=previous.get("job_description", ""),
            placeholder="Paste the job description to make your interview more targeted...",
            height=120,
        )
        submitted = st.form_submit_button("✦  Generate questions & start interview", use_container_width=True)

    if submitted:
        final_role = custom_role.strip() if role == "Custom Job Role" else role
        if not final_role:
            st.error("Please enter a custom job role.")
            return
        setup = {
            "role": final_role,
            "experience": experience,
            "difficulty": difficulty,
            "interview_type": interview_type,
            "question_count": int(question_count),
            "job_description": job_description.strip()[:7000],
        }
        client, error, model = require_client()
        if error:
            st.error(error)
            return
        try:
            with st.spinner(f"Your AI coach is preparing {question_count} tailored questions..."):
                questions = generate_questions(client, model, setup)
            st.session_state.interview = {
                "setup": setup,
                "questions": questions,
                "answers": [],
                "evaluations": [],
                "current_index": 0,
                "completed": False,
                "final_report": None,
                "started_at": datetime.now().strftime("%d %b %Y, %I:%M %p"),
                "completed_at": None,
                "model": model,
            }
            st.session_state.last_role = final_role
            st.session_state.last_setup = {
                **setup, "custom_role": custom_role,
            }
            st.session_state.page = "Start Interview"
            safe_rerun()
        except Exception as exc:
            st.error(f"Could not start the interview. {friendly_api_error(exc)}")


def render_feedback(evaluation: dict[str, Any]) -> None:
    st.markdown('<div class="feedback-card">', unsafe_allow_html=True)
    score = evaluation["overall_score"]
    st.markdown(
        f'<div class="eyebrow">AI ANSWER EVALUATION</div>'
        f'<div style="display:flex;align-items:center;gap:14px;flex-wrap:wrap;margin:8px 0 14px">'
        f'<span style="font-family:Manrope;font-size:2.2rem;font-weight:800;color:{score_color(score)}">{score}/100</span>'
        f'<span class="score-pill">Overall answer score</span></div>',
        unsafe_allow_html=True,
    )
    score_labels = {
        "relevance": "Relevance",
        "technical_accuracy": "Technical accuracy",
        "clarity_communication": "Clarity & communication",
        "completeness": "Completeness",
        "problem_solving": "Problem solving",
        "professional_presentation": "Professional presentation",
    }
    cols = st.columns(3)
    for idx, (key, label) in enumerate(score_labels.items()):
        with cols[idx % 3]:
            st.markdown(f'<div class="small-note">{label} · <b>{evaluation["scores"][key]}</b>/100</div>',
                        unsafe_allow_html=True)
            st.progress(evaluation["scores"][key] / 100)

    if evaluation.get("short_feedback"):
        st.markdown(f'<div class="callout">{evaluation["short_feedback"]}</div>', unsafe_allow_html=True)

    good, improve = st.columns(2)
    with good:
        st.markdown("**What you did well**")
        if evaluation["strengths"]:
            for item in evaluation["strengths"]:
                st.markdown(f"- {item}")
        else:
            st.caption("No specific strengths were returned.")
    with improve:
        st.markdown("**What to improve**")
        if evaluation["improvements"]:
            for item in evaluation["improvements"]:
                st.markdown(f"- {item}")
        else:
            st.caption("No specific improvements were returned.")

    with st.expander("Important points you may have missed", expanded=True):
        for item in evaluation["missing_points"] or ["No additional missing points identified."]:
            st.markdown(f"- {item}")
    with st.expander("Professionally improved sample answer"):
        st.write(evaluation.get("sample_answer") or "The AI did not provide a sample answer.")
    with st.expander("Actionable recommendations"):
        for item in evaluation["recommendations"] or ["Review the feedback and practice a more structured response."]:
            st.markdown(f"- {item}")
    st.markdown("</div>", unsafe_allow_html=True)


def finish_interview(interview: dict[str, Any], client: Groq, model: str) -> None:
    with st.spinner("Your AI coach is preparing your final performance report..."):
        final_report = build_final_report(client, model, interview)
    interview["final_report"] = final_report
    interview["completed"] = True
    interview["completed_at"] = datetime.now().strftime("%d %b %Y, %I:%M %p")
    st.session_state.history.append(create_interview_record(interview))


def render_active_interview() -> None:
    interview = st.session_state.interview
    if not interview:
        st.info("Your interview has not started yet. Configure a session to begin.")
        if st.button("Go to interview setup"):
            st.session_state.page = "Start Interview"
            safe_rerun()
        return

    if interview.get("completed"):
        render_completed_interview(interview)
        return

    idx = interview["current_index"]
    total = len(interview["questions"])
    answered = len(interview["evaluations"])
    st.markdown(
        f"""
        <div class="hero">
          <div class="eyebrow">LIVE INTERVIEW SESSION · {interview['setup']['role'].upper()}</div>
          <h1>You're doing great. Keep going.</h1>
          <p>Take your time, structure your thoughts, and answer as if you were speaking to a real interviewer.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.progress(answered / total)
    p1, p2, p3 = st.columns(3)
    p1.metric("Progress", f"{answered}/{total}")
    p2.metric("Difficulty", interview["setup"]["difficulty"])
    p3.metric("Interview format", interview["setup"]["interview_type"])

    if answered < total and idx < total:
        question = interview["questions"][idx]
        st.markdown(
            f'<div class="question-card"><div class="question-number">QUESTION {idx + 1:02d} / {total:02d}</div>'
            f'<div class="question-text">{question}</div></div>',
            unsafe_allow_html=True,
        )

        answer_key = f"answer_{id(interview)}_{idx}"
        answer_value = st.session_state.get(answer_key, "")
        answer = st.text_area(
            "Your answer",
            key=answer_key,
            height=190,
            placeholder="Type your answer here. Explain your thinking and include examples where relevant...",
            help="Your answer is submitted to the configured Groq model for evaluation.",
        )
        st.caption(f"{len(answer.strip())} characters · Aim for a clear, structured answer.")
        if st.button("✓  Submit answer for AI feedback", key=f"submit_answer_{idx}",
                     use_container_width=True, disabled=not answer.strip()):
            # Guard against duplicate submissions during reruns.
            if len(interview["evaluations"]) != idx:
                st.warning("This question has already been submitted. Continue to the next question.")
            else:
                client, error, model = require_client()
                if error:
                    st.error(error)
                else:
                    try:
                        with st.spinner("Your coach is reviewing your answer..."):
                            evaluation = evaluate_answer(
                                client, model, interview["setup"], question, answer.strip(), idx
                            )
                        interview["answers"].append(answer.strip())
                        interview["evaluations"].append(evaluation)
                        interview["current_index"] = idx
                        st.session_state[f"submitted_{id(interview)}_{idx}"] = True
                        safe_rerun()
                    except Exception as exc:
                        st.error(f"Your answer was not submitted. {friendly_api_error(exc)}")

        # The feedback only appears after the evaluation is stored.
        if len(interview["evaluations"]) > idx:
            render_feedback(interview["evaluations"][idx])
    elif answered < total:
        st.warning("Interview state needs attention. Please restart this session.")
    else:
        client, error, model = require_client()
        if error:
            st.error(error)
        else:
            try:
                finish_interview(interview, client, model)
                safe_rerun()
            except Exception as exc:
                st.error(f"All answers are saved, but the final report could not be generated. {friendly_api_error(exc)}")
                if st.button("Retry final report generation"):
                    try:
                        finish_interview(interview, client, model)
                        safe_rerun()
                    except Exception as retry_exc:
                        st.error(friendly_api_error(retry_exc))

    # After an answer has been evaluated, the next button is the only way forward.
    if len(interview["evaluations"]) > idx and not interview.get("completed"):
        st.markdown("---")
        if idx + 1 < total:
            if st.button("Next question  →", key=f"next_question_{idx}", use_container_width=True):
                interview["current_index"] = idx + 1
                safe_rerun()
        else:
            if st.button("Finish interview & generate report  →", key="finish_interview",
                         use_container_width=True):
                client, error, model = require_client()
                if error:
                    st.error(error)
                else:
                    try:
                        finish_interview(interview, client, model)
                        safe_rerun()
                    except Exception as exc:
                        st.error(f"Could not generate the final report. {friendly_api_error(exc)}")

    st.markdown("---")
    if st.button("End session and discard this interview", key="discard_interview"):
        st.session_state.interview = None
        st.session_state.page = "Dashboard"
        safe_rerun()


def render_completed_interview(interview: dict[str, Any]) -> None:
    report = interview.get("final_report") or {}
    st.markdown(
        """
        <div class="hero">
          <div class="eyebrow">INTERVIEW COMPLETE</div>
          <h1>Progress worth celebrating.</h1>
          <p>Your answers have been reviewed. Explore your performance report and use the roadmap to prepare for your next opportunity.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    score = report.get("average_score", 0)
    c1, c2, c3 = st.columns(3)
    c1.metric("Overall interview score", f"{score}/100")
    c2.metric("Questions completed", len(interview["questions"]))
    c3.metric("Best answer", f"{report.get('best_score', 0)}/100")
    st.progress(score / 100)

    section_heading("Your AI interview summary")
    st.markdown(f'<div class="surface">{report.get("summary", "Your report is ready.")}</div>',
                unsafe_allow_html=True)

    left, right = st.columns(2)
    with left:
        section_heading("Performance radar")
        render_radar(report.get("dimension_averages", {}))
    with right:
        section_heading("Question-by-question scores")
        render_score_bars(interview["evaluations"], interview["questions"])

    strengths, weaknesses = st.columns(2)
    with strengths:
        st.markdown('<div class="surface">', unsafe_allow_html=True)
        section_heading("Strongest areas")
        for item in report.get("strongest_areas", []):
            st.markdown(f"- {item}")
        st.markdown("</div>", unsafe_allow_html=True)
    with weaknesses:
        st.markdown('<div class="surface">', unsafe_allow_html=True)
        section_heading("Growth opportunities")
        for item in report.get("weakest_areas", []):
            st.markdown(f"- {item}")
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="surface">', unsafe_allow_html=True)
    section_heading("Skill assessment")
    dimension_names = {
        "relevance": "Answer relevance",
        "technical_accuracy": "Role knowledge",
        "clarity_communication": "Communication",
        "completeness": "Completeness",
        "problem_solving": "Problem solving",
        "professional_presentation": "Professional presentation",
    }
    for key, label in dimension_names.items():
        value = report.get("dimension_averages", {}).get(key, 0)
        a, b = st.columns([1, 4])
        a.markdown(f"**{label}**")
        b.progress(value / 100, text=f"{value}/100")
    st.markdown(f"**Technical knowledge:** {report.get('technical_assessment', '')}")
    st.markdown(f"**Communication:** {report.get('communication_assessment', '')}")
    st.markdown("</div>", unsafe_allow_html=True)

    section_heading("Personalized learning roadmap")
    roadmap = report.get("learning_roadmap", [])
    if roadmap:
        for step in roadmap:
            if isinstance(step, dict):
                with st.expander(f"{step.get('timeframe', 'Next step')} · {step.get('focus', 'Practice focus')}",
                                 expanded=True):
                    for action in clean_string_list(step.get("actions", []), 8):
                        st.markdown(f"- {action}")
    else:
        st.info("No roadmap items were returned. Review the recommendations below.")
    section_heading("Recommended next steps")
    for item in report.get("recommendations", []):
        st.markdown(f"- {item}")

    st.download_button(
        "⬇  Download full interview report (.txt)",
        data=make_report_text(interview),
        file_name=f"interview_report_{re.sub(r'[^a-z0-9]+', '_', interview['setup']['role'].lower()).strip('_')}.txt",
        mime="text/plain",
        use_container_width=True,
    )
    if st.button("↻  Restart with a new interview", key="restart_completed", use_container_width=True):
        st.session_state.interview = None
        st.session_state.page = "Start Interview"
        safe_rerun()


# ---------------------------------------------------------------------
# History and analytics
# ---------------------------------------------------------------------

def render_history() -> None:
    st.markdown(
        '<div class="hero"><div class="eyebrow">YOUR PRACTICE JOURNEY</div><h1>Interview history.</h1>'
        '<p>Review completed sessions from this browser session. Your history is not fabricated or stored on a remote database.</p></div>',
        unsafe_allow_html=True,
    )
    if not st.session_state.history:
        st.info("No completed interviews yet. Complete your first practice session to see it here.")
        if st.button("Start your first interview"):
            st.session_state.page = "Start Interview"
            safe_rerun()
        return

    for i, item in enumerate(reversed(st.session_state.history)):
        with st.expander(f"{item['role']}  ·  {item['completed_at']}  ·  {item['average_score']}/100", expanded=i == 0):
            a, b, c = st.columns(3)
            a.metric("Average score", f"{item['average_score']}/100")
            b.metric("Best answer", f"{item['best_score']}/100")
            c.metric("Questions", item["question_count"])
            if item.get("evaluations"):
                render_score_bars(item["evaluations"], item.get("questions", []))


def render_analytics() -> None:
    st.markdown(
        '<div class="hero"><div class="eyebrow">MEASURE YOUR GROWTH</div><h1>Performance analytics.</h1>'
        '<p>Understand how your interview practice is progressing using your real completed-session data.</p></div>',
        unsafe_allow_html=True,
    )
    if not st.session_state.history:
        st.info("Analytics will become available after you complete an interview.")
        if st.button("Start practicing"):
            st.session_state.page = "Start Interview"
            safe_rerun()
        return

    history = st.session_state.history
    a, b, c = st.columns(3)
    a.metric("Completed sessions", len(history))
    b.metric("Average interview score", f"{average_history_score()}/100")
    c.metric("Questions evaluated", sum(item["question_count"] for item in history))

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=list(range(1, len(history) + 1)),
        y=[item["average_score"] for item in history],
        mode="lines+markers+text",
        text=[item["role"] for item in history],
        textposition="top center",
        line=dict(color="#718fff", width=3),
        marker=dict(size=10, color="#9a7cff"),
        name="Interview score",
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#c5d2eb"),
        xaxis=dict(title="Completed session", gridcolor="rgba(145,166,210,.12)", dtick=1),
        yaxis=dict(title="Average score", range=[0, 110], gridcolor="rgba(145,166,210,.12)"),
        height=340, margin=dict(l=10, r=10, t=25, b=10),
    )
    section_heading("Score trend")
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    evaluations = all_completed_evaluations()
    if evaluations:
        keys = ["relevance", "technical_accuracy", "clarity_communication",
                "completeness", "problem_solving", "professional_presentation"]
        labels = ["Relevance", "Role knowledge", "Communication", "Completeness",
                  "Problem solving", "Presentation"]
        averages = [round(sum(e["scores"][key] for e in evaluations) / len(evaluations)) for key in keys]
        fig2 = px.bar(x=labels, y=averages, text=averages,
                      labels={"x": "Skill", "y": "Average score"})
        fig2.update_traces(marker_color="#8a72ef", textposition="outside", cliponaxis=False)
        fig2.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#c5d2eb"),
            yaxis=dict(range=[0, 110], gridcolor="rgba(145,166,210,.12)"),
            height=330, margin=dict(l=10, r=10, t=25, b=10),
        )
        section_heading("Skill evaluation across completed interviews")
        st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})


# ---------------------------------------------------------------------
# Interview tips and about
# ---------------------------------------------------------------------

def render_tips() -> None:
    st.markdown(
        '<div class="hero"><div class="eyebrow">COACHING CORNER</div><h1>Small habits. Strong answers.</h1>'
        '<p>Use these practical frameworks to make your interview responses clearer, more confident, and more memorable.</p></div>',
        unsafe_allow_html=True,
    )
    tips = [
        ("01", "Use the STAR framework", "For behavioral questions, explain the Situation, Task, Action, and Result. Keep the focus on what you personally did and what changed."),
        ("02", "Think aloud on technical problems", "Clarify requirements, state assumptions, outline an approach, discuss trade-offs, and test edge cases. Interviewers want to understand your reasoning."),
        ("03", "Be specific, not vague", "Replace phrases like “I am good at teamwork” with a short example that shows how you collaborated and what the outcome was."),
        ("04", "Structure your answer first", "Start with a direct answer, add two or three supporting points, then close with a concise takeaway. This helps you stay focused."),
        ("05", "Own what you do not know", "Be honest. Explain what you understand, how you would investigate the gap, and how you would validate a solution."),
        ("06", "Ask thoughtful questions", "Prepare questions about team priorities, success measures, technical practices, and the challenges the role is expected to solve."),
    ]
    for number, title, body in tips:
        st.markdown(
            f'<div class="tip-card" style="padding:19px 21px;margin:12px 0;display:flex;gap:18px">'
            f'<div style="font-family:Manrope;font-size:1.1rem;font-weight:800;color:#85aaff">{number}</div>'
            f'<div><div style="font-weight:800;color:#f0f4ff;margin-bottom:5px">{title}</div>'
            f'<div style="color:#9eafce;line-height:1.65">{body}</div></div></div>',
            unsafe_allow_html=True,
        )
    st.markdown('<div class="surface">', unsafe_allow_html=True)
    section_heading("A reliable answer structure")
    st.markdown(
        """
        1. **Direct response** — answer the question in one clear sentence.
        2. **Reasoning** — explain the key idea, method, or decision.
        3. **Evidence** — give an example, metric, or practical detail.
        4. **Outcome** — describe the result and what you learned.
        """
    )
    st.markdown("</div>", unsafe_allow_html=True)


def render_about() -> None:
    st.markdown(
        '<div class="hero"><div class="eyebrow">ABOUT THE PLATFORM</div><h1>Practice with purpose.</h1>'
        '<p>AI Interview Practice is a personal preparation workspace designed to help candidates rehearse interviews and turn feedback into a focused improvement plan.</p></div>',
        unsafe_allow_html=True,
    )
    c1, c2 = st.columns(2)
    with c1:
        st.markdown('<div class="surface">', unsafe_allow_html=True)
        section_heading("What you can do")
        for item in [
            "Generate tailored interview questions for your target role.",
            "Practice one question at a time without skipping.",
            "Receive structured AI feedback and improved sample answers.",
            "Review performance analytics and a personalized learning roadmap.",
            "Download a plain-text report of your completed interview.",
        ]:
            st.markdown(f"- {item}")
        st.markdown("</div>", unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="surface">', unsafe_allow_html=True)
        section_heading("Privacy & session data")
        st.markdown(
            "Your interview state and history are held in Streamlit session state for the current session. "
            "This app does not include a database or long-term account storage. Your submitted answers are sent "
            "to Groq for AI evaluation. Do not submit passwords, confidential employer information, or sensitive personal data."
        )
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="surface">', unsafe_allow_html=True)
    section_heading("AI configuration")
    st.markdown(f"**Configured model:** `{configured_model}`")
    st.markdown("The same model configured in `GROQ_MODEL` is used for question generation, answer evaluation, and final reporting. There is no automatic model fallback.")
    st.markdown("</div>", unsafe_allow_html=True)


# ---------------------------------------------------------------------
# Page router
# ---------------------------------------------------------------------

page = st.session_state.page

if page == "Dashboard":
    render_dashboard()
elif page == "Start Interview":
    active = st.session_state.interview
    if active and not active.get("completed"):
        render_active_interview()
    elif active and active.get("completed"):
        render_completed_interview(active)
    else:
        render_setup()
elif page == "Interview History":
    render_history()
elif page == "Performance Analytics":
    render_analytics()
elif page == "Interview Tips":
    render_tips()
elif page == "About":
    render_about()
else:
    st.session_state.page = "Dashboard"
    safe_rerun()

st.markdown(
    '<div style="text-align:center;color:#647797;font-size:.73rem;padding:28px 0 4px">'
    'AI Interview Practice · Your Personal AI Interview Coach</div>',
    unsafe_allow_html=True,
)
