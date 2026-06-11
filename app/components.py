"""Reusable HTML helpers for the Aurora premium Streamlit dashboard."""

from __future__ import annotations

from html import escape

import pandas as pd

ASSET_CELL_CLASSES = {
    "BOVA11.SA": "aurora-cell-bova",
    "IVVB11.SA": "aurora-cell-ivvb",
    "IMAB11.SA": "aurora-cell-imab",
    "USDBRL=X": "aurora-cell-usd",
    "CDI": "aurora-cell-cdi",
}


def build_hero(
    *,
    title: str,
    slogan: str,
    description: str,
    badges: list[str],
) -> str:
    """Build the dashboard hero banner."""
    badge_html = "".join(f'<span class="aurora-badge">{escape(badge)}</span>' for badge in badges)
    return (
        '<section class="aurora-hero">'
        f'<h1 class="aurora-hero-title">{escape(title)}</h1>'
        f'<p class="aurora-hero-slogan">{escape(slogan)}</p>'
        f'<p class="aurora-hero-copy">{escape(description)}</p>'
        f'<div class="aurora-badge-row">{badge_html}</div>'
        "</section>"
    )


def build_section_header(
    title: str,
    subtitle: str,
    *,
    eyebrow: str | None = None,
) -> str:
    """Build a section header with optional eyebrow text."""
    eyebrow_html = f'<div class="eyebrow">{escape(eyebrow)}</div>' if eyebrow else ""
    return (
        '<div class="aurora-section-header">'
        f"{eyebrow_html}"
        f"<h2>{escape(title)}</h2>"
        f"<p>{escape(subtitle)}</p>"
        "</div>"
    )


def build_metric_card(
    label: str,
    value: str,
    *,
    detail: str = "",
    tone: str = "tone-blue",
) -> str:
    """Build a highlighted KPI card."""
    detail_html = f'<p class="aurora-metric-detail">{escape(detail)}</p>' if detail else ""
    return (
        f'<div class="aurora-metric-card {escape(tone)}">'
        f'<p class="aurora-metric-label">{escape(label)}</p>'
        f'<p class="aurora-metric-value">{escape(value)}</p>'
        f"{detail_html}"
        "</div>"
    )


def build_info_card(
    title: str,
    body: str,
    *,
    eyebrow: str | None = None,
    tone: str = "",
    footer: str | None = None,
) -> str:
    """Build a generic research/info card."""
    eyebrow_html = f'<div class="eyebrow">{escape(eyebrow)}</div>' if eyebrow else ""
    footer_html = f'<div class="footer">{escape(footer)}</div>' if footer else ""
    tone_class = f" {escape(tone)}" if tone else ""
    return (
        f'<div class="aurora-info-card{tone_class}">'
        f"{eyebrow_html}"
        f"<h4>{escape(title)}</h4>"
        f"<p>{escape(body)}</p>"
        f"{footer_html}"
        "</div>"
    )


def build_callout(body: str, *, variant: str = "warning") -> str:
    """Build a wide callout box for notes, GenAI and disclaimer text."""
    return f'<div class="aurora-callout {escape(variant)}"><p>{escape(body)}</p></div>'


def build_flow_card(steps: list[tuple[str, str]]) -> str:
    """Build a compact flowchart card for the research pipeline."""
    step_html = "".join(
        (
            '<div class="aurora-flow-step">'
            f"<strong>{escape(title)}</strong>"
            f"<span>{escape(detail)}</span>"
            "</div>"
        )
        for title, detail in steps
    )
    return f'<div class="aurora-flow-card"><div class="aurora-flow">{step_html}</div></div>'


def build_sidebar_brand(title: str, subtitle: str) -> str:
    """Build the sidebar brand block."""
    return (
        '<div class="aurora-sidebar-brand">'
        '<div class="aurora-sidebar-eyebrow">Aurora Console</div>'
        f'<h1 class="aurora-sidebar-title">{escape(title)}</h1>'
        f'<p class="aurora-sidebar-subtitle">{escape(subtitle)}</p>'
        "</div>"
    )


def build_sidebar_status(
    *,
    execution_mode: str,
    data_source: str,
    date_window: str,
    note: str | None,
) -> str:
    """Build the sidebar execution status block."""
    note_html = f"<p>{escape(note)}</p>" if note else ""
    return (
        '<div class="aurora-sidebar-card">'
        "<h4>Pipeline Status</h4>"
        '<ul class="aurora-sidebar-list">'
        f"<li><span>Modo</span>"
        f'<span class="aurora-status-pill teal">{escape(execution_mode)}</span></li>'
        f"<li><span>Fonte</span>"
        f'<span class="aurora-status-pill orange">{escape(data_source)}</span></li>'
        f"<li><span>Janela</span><span>{escape(date_window)}</span></li>"
        "</ul>"
        f"{note_html}"
        "</div>"
    )


def build_sidebar_nav(items: list[str]) -> str:
    """Build a simple sidebar roadmap list."""
    list_html = "".join(f"<li>{escape(item)}</li>" for item in items)
    return f'<div class="aurora-sidebar-nav"><h4>Overview</h4><ul>{list_html}</ul></div>'


def build_allocation_table(frame: pd.DataFrame) -> str:
    """Render the allocation grid as a styled HTML table."""
    headers = "".join(f"<th>{escape(str(column))}</th>" for column in frame.columns)
    rows = []
    for _, row in frame.iterrows():
        cells = []
        for column, value in row.items():
            column_name = str(column)
            cell_class = ASSET_CELL_CLASSES.get(column_name, "")
            class_attr = f' class="{cell_class}"' if cell_class else ""
            cells.append(f"<td{class_attr}>{escape(str(value))}</td>")
        rows.append(f"<tr>{''.join(cells)}</tr>")
    return (
        '<div class="aurora-table-card">'
        '<table class="aurora-table">'
        f"<thead><tr>{headers}</tr></thead>"
        f"<tbody>{''.join(rows)}</tbody>"
        "</table>"
        "</div>"
    )
