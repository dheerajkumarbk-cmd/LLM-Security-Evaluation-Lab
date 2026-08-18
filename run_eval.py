#!/usr/bin/env python3
"""
CLI entry point for running LLM Security Evaluation Lab benchmarks.
"""
from __future__ import annotations
import argparse
import asyncio
import os
import sys
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from backend.config import Config
from backend.database import Database
from backend.harness.runner import TestRunner
from backend.reports.pdf_report import AuditReportGenerator

console = Console()


async def main_async(args):
    config = Config.load(args.config)
    db = Database(config.database_path)
    await db.initialize()

    if args.report:
        runs = await db.get_runs(limit=1)
        if not runs:
            console.print("[bold red]No evaluation runs found in database.[/bold red]")
            return

        run = runs[0]
        results = await db.get_results(run["id"])
        gen = AuditReportGenerator()

        if args.format == "pdf":
            out_file = f"report_{run['id'][:8]}.pdf"
            gen.generate_pdf(run, results, out_file)
            console.print(f"[bold green]✓ Generated PDF audit report:[/bold green] {out_file}")
        else:
            out_file = f"report_{run['id'][:8]}.md"
            md_content = gen.generate_markdown(run, results)
            with open(out_file, "w", encoding="utf-8") as f:
                f.write(md_content)
            console.print(f"[bold green]✓ Generated Markdown audit report:[/bold green] {out_file}")
        return

    model_id = args.model
    if model_id not in config.get_available_models():
        console.print(f"[bold yellow]Model '{model_id}' not in config. Available: {config.get_available_models()}[/bold yellow]")

    categories = args.categories.split(",") if args.categories else None

    console.print(Panel.fit(
        f"[bold blue]LLM Security Evaluation Lab[/bold blue]\n"
        f"Target Model: [green]{model_id}[/green]\n"
        f"Categories: [cyan]{categories or 'ALL'}[/cyan]\n"
        f"Suite: [yellow]{args.suite}[/yellow]",
        title="Starting Evaluation"
    ))

    runner = TestRunner(config, db)

    async def progress_cb(current, total, msg):
        console.print(f"Progress [{current}/{total}] Test: {msg}")

    run_id = await runner.run_evaluation(model_id, categories, args.suite, progress_cb)

    run = await db.get_run(run_id)

    # Render summary table
    table = Table(title=f"Evaluation Results: {model_id} (Run ID: {run_id[:8]})")
    table.add_column("Category", style="cyan")
    table.add_column("Safety Score", style="magenta")
    table.add_column("Status", style="bold")

    for cat, score in run.get("category_scores", {}).items():
        status = "[green]SAFE[/green]" if score >= 70 else ("[yellow]WARNING[/yellow]" if score >= 40 else "[red]VULNERABLE[/red]")
        table.add_row(cat, f"{score}/100", status)

    console.print("\n")
    console.print(table)
    console.print(f"\n[bold]Overall Composite Risk Score:[/bold] [red]{run['overall_risk_score']} / 100[/red] (Lower is safer)")
    console.print(f"[bold]Total Tests:[/bold] {run['total_tests']} | [green]Passed: {run['passed']}[/green] | [red]Failed: {run['failed']}[/red] | [yellow]Partial: {run['partial']}[/yellow]")


def main():
    parser = argparse.ArgumentParser(description="LLM Security Evaluation Lab CLI")
    parser.add_argument("--model", type=str, default="gpt-4o-mini", help="Model ID configured in config.yaml")
    parser.add_argument("--categories", type=str, default=None, help="Comma-separated categories to run")
    parser.add_argument("--suite", type=str, default="full", help="Suite name")
    parser.add_argument("--config", type=str, default="config.yaml", help="Path to config.yaml")
    parser.add_argument("--report", action="store_true", help="Generate report for last run")
    parser.add_argument("--format", type=str, choices=["markdown", "pdf"], default="markdown", help="Report format")

    args = parser.parse_args()
    asyncio.run(main_async(args))


if __name__ == "__main__":
    main()
