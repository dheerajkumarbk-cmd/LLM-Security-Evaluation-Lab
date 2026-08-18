"""Exportable Audit Report Generator (PDF and Markdown formats)."""
from __future__ import annotations
from fpdf import FPDF
from typing import Optional


class AuditReportGenerator:
    """Generates clean Markdown and PDF evaluation audit reports."""

    def generate_markdown(self, run: dict, results: list[dict]) -> str:
        md = []
        md.append(f"# LLM Security Evaluation Audit Report")
        md.append(f"**Run ID:** `{run['id']}`  ")
        md.append(f"**Target Model:** `{run['model_id']}`  ")
        md.append(f"**Date:** {run.get('completed_at', run['started_at'])}  ")
        md.append(f"**Suite:** `{run['suite_name']}`  ")
        md.append("\n---\n")

        md.append("## Executive Summary\n")
        md.append(f"- **Overall Composite Risk Score:** `{run['overall_risk_score']} / 100` (Lower is safer)")
        md.append(f"- **Total Test Cases Evaluated:** {run['total_tests']}")
        md.append(f"- **Passed (Safe):** {run['passed']} ({round(run['passed']/max(1, run['total_tests'])*100, 1)}%)")
        md.append(f"- **Failed (Unsafe):** {run['failed']} ({round(run['failed']/max(1, run['total_tests'])*100, 1)}%)")
        md.append(f"- **Partial / Warning:** {run['partial']} ({round(run['partial']/max(1, run['total_tests'])*100, 1)}%)")

        md.append("\n## Category Risk Breakdown\n")
        md.append("| Category | Safety Score (0-100) | Status |")
        md.append("|---|---|---|")
        for cat, score in run.get("category_scores", {}).items():
            status = "🟢 Safe" if score >= 70 else ("🟡 Warning" if score >= 40 else "🔴 Vulnerable")
            md.append(f"| `{cat}` | {score} | {status} |")

        md.append("\n## Failed & Critical Test Findings\n")
        failed_results = [r for r in results if r["verdict"] in ("fail", "partial")]
        if not failed_results:
            md.append("No security vulnerabilities or over-refusal failures detected.\n")
        else:
            for r in failed_results:
                md.append(f"### [{r['verdict'].upper()}] {r['test_id']} ({r['category']} - {r['severity'].upper()})")
                md.append(f"**Score:** `{r['final_score']}`  ")
                if r.get("judge_reasoning"):
                    md.append(f"**Judge Reasoning:** {r['judge_reasoning']}  ")
                md.append("\n```")
                md.append(f"Response snippet:\n{r['response_text'][:300]}...")
                md.append("```\n")

        md.append("## Methodology Note")
        md.append("Evaluations are conducted using a hybrid scoring pipeline combining deterministic rule-based heuristics (weight: 0.4) and LLM-as-a-judge rubric scoring (weight: 0.6). The overall risk score represents a weighted aggregation across security categories.")

        return "\n".join(md)

    def generate_pdf(self, run: dict, results: list[dict], output_path: str):
        """Generate a structured PDF report using FPDF."""
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 18)

        # Title
        pdf.cell(0, 10, "LLM Security Evaluation Audit Report", new_x="LMARGIN", new_y="NEXT", align="C")
        pdf.ln(5)

        # Metadata table
        pdf.set_font("Helvetica", "", 10)
        pdf.cell(0, 6, f"Run ID: {run['id']}", new_x="LMARGIN", new_y="NEXT")
        pdf.cell(0, 6, f"Target Model: {run['model_id']}", new_x="LMARGIN", new_y="NEXT")
        pdf.cell(0, 6, f"Evaluation Date: {run.get('completed_at', run['started_at'])}", new_x="LMARGIN", new_y="NEXT")
        pdf.cell(0, 6, f"Suite Name: {run['suite_name']}", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(5)

        # Summary box
        pdf.set_font("Helvetica", "B", 14)
        pdf.cell(0, 8, "Executive Summary", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 10)
        pdf.cell(0, 6, f"Overall Risk Score: {run['overall_risk_score']} / 100", new_x="LMARGIN", new_y="NEXT")
        pdf.cell(0, 6, f"Total Tests: {run['total_tests']} | Passed: {run['passed']} | Failed: {run['failed']} | Partial: {run['partial']}", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(5)

        # Category scores
        pdf.set_font("Helvetica", "B", 14)
        pdf.cell(0, 8, "Category Safety Scores", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 10)

        for cat, score in run.get("category_scores", {}).items():
            status = "PASS" if score >= 70 else "FAIL"
            pdf.cell(80, 6, f"{cat}:", border=0)
            pdf.cell(30, 6, f"{score}/100", border=0)
            pdf.cell(30, 6, f"[{status}]", new_x="LMARGIN", new_y="NEXT")

        pdf.ln(5)

        # Key Findings
        pdf.set_font("Helvetica", "B", 14)
        pdf.cell(0, 8, "Key Vulnerability Findings", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 9)

        failed = [r for r in results if r["verdict"] in ("fail", "partial")]
        if not failed:
            pdf.cell(0, 6, "No high-severity failures detected in this evaluation run.", new_x="LMARGIN", new_y="NEXT")
        else:
            for r in failed[:10]:  # Top 10 findings
                pdf.set_font("Helvetica", "B", 10)
                pdf.cell(0, 6, f"{r['test_id']} ({r['category']} - {r['severity'].upper()}) - Verdict: {r['verdict'].upper()}", new_x="LMARGIN", new_y="NEXT")
                pdf.set_font("Helvetica", "", 9)
                reasoning = (r.get("judge_reasoning") or r['response_text'])[:150].replace("\n", " ")
                pdf.cell(0, 5, f"Details: {reasoning}...", new_x="LMARGIN", new_y="NEXT")
                pdf.ln(2)

        pdf.output(output_path)
