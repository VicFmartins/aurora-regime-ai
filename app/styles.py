"""Shared CSS theme for the premium Aurora Streamlit dashboard."""

DASHBOARD_CSS = """
<style>
/* Aurora premium dashboard theme: palette and global surfaces. */
:root {
    --aurora-bg: #06111f;
    --aurora-bg-soft: #0c1c33;
    --aurora-bg-panel: rgba(11, 23, 42, 0.82);
    --aurora-bg-panel-strong: rgba(9, 19, 35, 0.94);
    --aurora-line: rgba(125, 211, 252, 0.18);
    --aurora-line-strong: rgba(103, 232, 249, 0.35);
    --aurora-text: #f8fbff;
    --aurora-text-soft: #bed0e3;
    --aurora-text-muted: #8fa6bf;
    --aurora-teal: #5eead4;
    --aurora-cyan: #38bdf8;
    --aurora-blue: #60a5fa;
    --aurora-violet: #a78bfa;
    --aurora-amber: #f59e0b;
    --aurora-rose: #fb7185;
    --aurora-green: #34d399;
    --aurora-shadow: 0 18px 50px rgba(2, 8, 23, 0.42);
}

.stApp {
    color: var(--aurora-text);
    background:
        radial-gradient(circle at 15% 15%, rgba(56, 189, 248, 0.20), transparent 24%),
        radial-gradient(circle at 82% 12%, rgba(167, 139, 250, 0.16), transparent 28%),
        radial-gradient(circle at 88% 42%, rgba(52, 211, 153, 0.10), transparent 22%),
        linear-gradient(180deg, #07111e 0%, #071425 42%, #07101c 100%);
}

.stApp::before {
    content: "";
    position: fixed;
    inset: 0;
    pointer-events: none;
    opacity: 0.14;
    background-image:
        linear-gradient(rgba(125, 211, 252, 0.12) 1px, transparent 1px),
        linear-gradient(90deg, rgba(125, 211, 252, 0.12) 1px, transparent 1px);
    background-size: 80px 80px;
    mask-image: linear-gradient(180deg, rgba(0, 0, 0, 0.18), rgba(0, 0, 0, 0));
}

.block-container {
    max-width: 1320px;
    padding-top: 1.2rem;
    padding-bottom: 2.5rem;
}

[data-testid="stSidebar"] {
    background:
        radial-gradient(circle at top, rgba(56, 189, 248, 0.16), transparent 22%),
        linear-gradient(180deg, #081727 0%, #0d1d32 60%, #09131f 100%);
    border-right: 1px solid rgba(125, 211, 252, 0.12);
}

[data-testid="stSidebar"] .block-container {
    padding-top: 1.5rem;
    padding-bottom: 1.2rem;
}

[data-testid="stSidebar"] * {
    color: var(--aurora-text);
}

[data-testid="stSidebar"] .stRadio label,
[data-testid="stSidebar"] .stCheckbox label,
[data-testid="stSidebar"] .stCaption,
[data-testid="stSidebar"] p {
    color: var(--aurora-text-soft) !important;
}

[data-testid="stSidebar"] .stButton button {
    width: 100%;
    min-height: 3rem;
    border-radius: 14px;
    border: 1px solid rgba(125, 211, 252, 0.24);
    background: linear-gradient(135deg, rgba(26, 49, 82, 0.95), rgba(17, 33, 59, 0.95));
    color: var(--aurora-text);
    box-shadow: 0 10px 24px rgba(5, 12, 25, 0.35);
}

[data-testid="stSidebar"] .stButton button:hover {
    border-color: rgba(94, 234, 212, 0.42);
    background: linear-gradient(135deg, rgba(32, 61, 101, 1), rgba(18, 39, 71, 1));
}

[data-testid="stSidebar"] .stCheckbox > label > div[data-testid="stMarkdownContainer"] p {
    font-weight: 500;
}

[data-testid="stSidebar"] .stRadio [role="radiogroup"] {
    gap: 0.5rem;
}

/* Sidebar branding, status cards and navigation list. */
.aurora-sidebar-brand,
.aurora-sidebar-card,
.aurora-sidebar-nav {
    background: rgba(9, 19, 35, 0.70);
    border: 1px solid rgba(125, 211, 252, 0.14);
    border-radius: 20px;
    box-shadow: var(--aurora-shadow);
}

.aurora-sidebar-brand {
    padding: 1.25rem 1.15rem;
    margin-bottom: 1rem;
}

.aurora-sidebar-eyebrow {
    margin: 0 0 0.35rem;
    font-size: 0.82rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--aurora-cyan);
}

.aurora-sidebar-title {
    margin: 0;
    font-size: 1.75rem;
    font-weight: 700;
}

.aurora-sidebar-subtitle {
    margin: 0.35rem 0 0;
    font-size: 0.95rem;
    color: var(--aurora-text-soft);
}

.aurora-sidebar-card {
    padding: 1rem 1rem 0.9rem;
    margin-bottom: 1rem;
}

.aurora-sidebar-card h4,
.aurora-sidebar-nav h4 {
    margin: 0 0 0.6rem;
    font-size: 0.96rem;
}

.aurora-sidebar-list,
.aurora-sidebar-nav ul {
    margin: 0;
    padding: 0;
    list-style: none;
}

.aurora-sidebar-list li,
.aurora-sidebar-nav li {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 0.5rem;
    padding: 0.45rem 0;
    border-bottom: 1px solid rgba(125, 211, 252, 0.08);
    color: var(--aurora-text-soft);
    font-size: 0.92rem;
}

.aurora-sidebar-list li:last-child,
.aurora-sidebar-nav li:last-child {
    border-bottom: none;
}

.aurora-sidebar-nav {
    padding: 1rem;
    margin-top: 1rem;
}

.aurora-status-pill {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    padding: 0.28rem 0.55rem;
    border-radius: 999px;
    font-size: 0.76rem;
    font-weight: 600;
    border: 1px solid rgba(94, 234, 212, 0.20);
    background: rgba(15, 36, 65, 0.85);
}

.aurora-status-pill::before {
    content: "";
    width: 0.48rem;
    height: 0.48rem;
    border-radius: 999px;
    background: currentColor;
    box-shadow: 0 0 0 6px rgba(255, 255, 255, 0.03);
}

.aurora-status-pill.teal {
    color: var(--aurora-teal);
}

.aurora-status-pill.orange {
    color: var(--aurora-amber);
}

.aurora-status-pill.violet {
    color: var(--aurora-violet);
}

/* Hero, badges and section headers. */
.aurora-hero {
    position: relative;
    overflow: hidden;
    padding: 2rem 2.2rem 1.8rem;
    border-radius: 28px;
    background:
        radial-gradient(circle at 12% 18%, rgba(56, 189, 248, 0.18), transparent 24%),
        radial-gradient(circle at 72% 18%, rgba(167, 139, 250, 0.18), transparent 26%),
        radial-gradient(circle at 78% 8%, rgba(52, 211, 153, 0.14), transparent 22%),
        linear-gradient(135deg, rgba(11, 23, 42, 0.96), rgba(16, 33, 58, 0.90));
    border: 1px solid rgba(125, 211, 252, 0.22);
    box-shadow: 0 24px 60px rgba(2, 8, 23, 0.45);
}

.aurora-hero::after {
    content: "";
    position: absolute;
    inset: auto -18% -45% auto;
    width: 420px;
    height: 420px;
    background: radial-gradient(circle, rgba(56, 189, 248, 0.22), transparent 62%);
    filter: blur(12px);
}

.aurora-hero-title {
    margin: 0;
    font-size: clamp(2.6rem, 5vw, 4.1rem);
    line-height: 1.02;
    font-weight: 800;
    letter-spacing: -0.04em;
}

.aurora-hero-slogan {
    margin: 0.7rem 0 1rem;
    font-size: 1.3rem;
    color: #eef8ff;
}

.aurora-hero-copy {
    max-width: 58rem;
    margin: 0;
    font-size: 1.02rem;
    line-height: 1.7;
    color: var(--aurora-text-soft);
}

.aurora-badge-row {
    display: flex;
    flex-wrap: wrap;
    gap: 0.65rem;
    margin: 1.25rem 0 0;
}

.aurora-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.45rem;
    padding: 0.42rem 0.78rem;
    border-radius: 999px;
    border: 1px solid rgba(125, 211, 252, 0.18);
    background: rgba(7, 20, 38, 0.56);
    color: var(--aurora-text);
    font-size: 0.82rem;
    font-weight: 600;
}

.aurora-badge::before {
    content: "";
    width: 0.42rem;
    height: 0.42rem;
    border-radius: 999px;
    background: linear-gradient(135deg, var(--aurora-cyan), var(--aurora-violet));
}

.aurora-section-header {
    margin: 1.8rem 0 0.95rem;
}

.aurora-section-header .eyebrow {
    margin: 0 0 0.3rem;
    font-size: 0.80rem;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: var(--aurora-cyan);
}

.aurora-section-header h2 {
    margin: 0;
    font-size: 2rem;
    font-weight: 700;
    letter-spacing: -0.03em;
}

.aurora-section-header p {
    max-width: 68rem;
    margin: 0.5rem 0 0;
    color: var(--aurora-text-soft);
    line-height: 1.65;
}

/* Card system used across metrics, assets, indicators and limitations. */
.aurora-metric-card,
.aurora-info-card,
.aurora-callout,
.aurora-table-card,
.aurora-flow-card {
    background: var(--aurora-bg-panel);
    border: 1px solid rgba(125, 211, 252, 0.16);
    border-radius: 22px;
    box-shadow: var(--aurora-shadow);
}

.aurora-metric-card {
    padding: 1rem 1rem 0.95rem;
    min-height: 9.1rem;
    overflow: hidden;
    position: relative;
}

.aurora-metric-card::after {
    content: "";
    position: absolute;
    inset: auto -24px -42px auto;
    width: 140px;
    height: 140px;
    border-radius: 999px;
    background: radial-gradient(circle, rgba(255, 255, 255, 0.10), transparent 70%);
}

.aurora-metric-label {
    margin: 0 0 0.65rem;
    color: var(--aurora-text-soft);
    font-size: 0.92rem;
}

.aurora-metric-value {
    margin: 0;
    font-size: 2rem;
    font-weight: 800;
    letter-spacing: -0.04em;
}

.aurora-metric-detail {
    margin: 0.55rem 0 0;
    color: var(--aurora-text-muted);
    font-size: 0.84rem;
    line-height: 1.5;
}

.tone-teal {
    border-color: rgba(94, 234, 212, 0.26);
    box-shadow: 0 16px 44px rgba(45, 212, 191, 0.12);
}

.tone-teal .aurora-metric-value,
.tone-teal h4 {
    color: var(--aurora-teal);
}

.tone-orange {
    border-color: rgba(245, 158, 11, 0.28);
    box-shadow: 0 16px 44px rgba(245, 158, 11, 0.10);
}

.tone-orange .aurora-metric-value,
.tone-orange h4 {
    color: #fdbb74;
}

.tone-blue {
    border-color: rgba(96, 165, 250, 0.28);
    box-shadow: 0 16px 44px rgba(96, 165, 250, 0.10);
}

.tone-blue .aurora-metric-value,
.tone-blue h4 {
    color: #8bc3ff;
}

.tone-violet {
    border-color: rgba(167, 139, 250, 0.28);
    box-shadow: 0 16px 44px rgba(167, 139, 250, 0.12);
}

.tone-violet .aurora-metric-value,
.tone-violet h4 {
    color: #c4b5fd;
}

.tone-rose {
    border-color: rgba(251, 113, 133, 0.30);
    box-shadow: 0 16px 44px rgba(251, 113, 133, 0.11);
}

.tone-rose .aurora-metric-value,
.tone-rose h4 {
    color: #fda4af;
}

.tone-green {
    border-color: rgba(52, 211, 153, 0.28);
    box-shadow: 0 16px 44px rgba(52, 211, 153, 0.12);
}

.tone-green .aurora-metric-value,
.tone-green h4 {
    color: #86efac;
}

.aurora-info-card {
    padding: 1.15rem 1.1rem 1rem;
    height: 100%;
}

.aurora-info-card h4 {
    margin: 0;
    font-size: 1.06rem;
    color: var(--aurora-text);
}

.aurora-info-card .eyebrow {
    margin: 0 0 0.38rem;
    font-size: 0.75rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--aurora-text-muted);
}

.aurora-info-card p {
    margin: 0.55rem 0 0;
    color: var(--aurora-text-soft);
    line-height: 1.6;
    font-size: 0.94rem;
}

.aurora-info-card .footer {
    margin-top: 0.8rem;
    color: var(--aurora-text-muted);
    font-size: 0.82rem;
}

.aurora-flow-card {
    padding: 1.25rem;
}

.aurora-flow {
    display: grid;
    grid-template-columns: repeat(5, minmax(0, 1fr));
    gap: 0.8rem;
    margin-top: 1rem;
}

.aurora-flow-step {
    position: relative;
    padding: 0.95rem 0.85rem;
    border-radius: 16px;
    border: 1px solid rgba(125, 211, 252, 0.12);
    background: rgba(8, 20, 38, 0.86);
    text-align: center;
}

.aurora-flow-step strong {
    display: block;
    font-size: 0.96rem;
}

.aurora-flow-step span {
    display: block;
    margin-top: 0.35rem;
    color: var(--aurora-text-muted);
    font-size: 0.82rem;
}

.aurora-flow-step:not(:last-child)::after {
    content: "→";
    position: absolute;
    right: -0.65rem;
    top: 50%;
    transform: translateY(-50%);
    color: var(--aurora-text-muted);
}

.aurora-callout {
    padding: 1rem 1.15rem;
    margin: 1rem 0 0;
}

.aurora-callout p {
    margin: 0;
    color: var(--aurora-text-soft);
    line-height: 1.65;
}

.aurora-callout.genai {
    background:
        radial-gradient(circle at top right, rgba(167, 139, 250, 0.24), transparent 28%),
        linear-gradient(135deg, rgba(32, 16, 60, 0.95), rgba(18, 24, 52, 0.95));
    border-color: rgba(167, 139, 250, 0.30);
    box-shadow: 0 20px 48px rgba(124, 58, 237, 0.20);
}

.aurora-callout.warning {
    background:
        linear-gradient(135deg, rgba(66, 44, 14, 0.92), rgba(49, 33, 12, 0.94));
    border-color: rgba(245, 158, 11, 0.30);
}

.aurora-callout.disclaimer {
    background:
        linear-gradient(135deg, rgba(33, 18, 43, 0.95), rgba(20, 16, 39, 0.95));
    border-color: rgba(196, 181, 253, 0.26);
}

.aurora-table-card {
    padding: 0.9rem;
    overflow-x: auto;
}

.aurora-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.92rem;
    color: var(--aurora-text);
}

.aurora-table thead th {
    padding: 0.82rem 0.85rem;
    text-align: left;
    font-size: 0.76rem;
    letter-spacing: 0.10em;
    text-transform: uppercase;
    color: var(--aurora-text-muted);
    border-bottom: 1px solid rgba(125, 211, 252, 0.14);
}

.aurora-table tbody td {
    padding: 0.9rem 0.85rem;
    border-bottom: 1px solid rgba(125, 211, 252, 0.08);
}

.aurora-table tbody tr:last-child td {
    border-bottom: none;
}

.aurora-table tbody tr:hover {
    background: rgba(125, 211, 252, 0.05);
}

.aurora-cell-bova { color: #5eead4; }
.aurora-cell-ivvb { color: #93c5fd; }
.aurora-cell-imab { color: #fcd34d; }
.aurora-cell-usd  { color: #f9a8d4; }
.aurora-cell-cdi  { color: #c4b5fd; }

/* Plotly and dataframe containers should feel integrated with the dark shell. */
div[data-testid="stPlotlyChart"] {
    padding: 0.65rem 0.65rem 0.2rem;
    border-radius: 22px;
    border: 1px solid rgba(125, 211, 252, 0.14);
    background: rgba(9, 19, 35, 0.74);
    box-shadow: var(--aurora-shadow);
}

div[data-testid="stDataFrame"] {
    border-radius: 20px;
    border: 1px solid rgba(125, 211, 252, 0.12);
    overflow: hidden;
}

.aurora-caption {
    margin-top: 0.55rem;
    color: var(--aurora-text-muted);
    font-size: 0.84rem;
}

@media (max-width: 1200px) {
    .aurora-flow {
        grid-template-columns: repeat(2, minmax(0, 1fr));
    }

    .aurora-flow-step:not(:last-child)::after {
        display: none;
    }
}

@media (max-width: 820px) {
    .block-container {
        padding-left: 1rem;
        padding-right: 1rem;
    }

    .aurora-hero {
        padding: 1.45rem;
    }

    .aurora-hero-title {
        font-size: 2.3rem;
    }

    .aurora-flow {
        grid-template-columns: minmax(0, 1fr);
    }
}
</style>
"""
