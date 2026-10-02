"""CrewAI crew construction and report validation."""

from __future__ import annotations

import os
from pathlib import Path
from typing import TYPE_CHECKING

import yaml

from recruitment_assistant.fixtures import FIXTURE_CANDIDATES

if TYPE_CHECKING:
    from crewai import Crew

CONFIG_DIR = Path(__file__).parent / "config"
REQUIRED_REPORT_HEADINGS = (
    "## Advisory",
    "## Ranked Recommendations",
    "## Evidence and Uncertainty",
    "## Outreach Drafts",
)


class CrewConfigurationError(RuntimeError):
    """Raised when required runtime configuration is missing or invalid."""


class ReportValidationError(RuntimeError):
    """Raised when the final crew output violates its report contract."""


def _load_yaml(path: Path) -> dict:
    with path.open(encoding="utf-8") as config_file:
        config = yaml.safe_load(config_file)
    if not isinstance(config, dict):
        raise CrewConfigurationError("Crew configuration must be a YAML mapping.")
    return config


def web_research_enabled() -> bool:
    return (
        os.getenv("AAMAD_ENABLE_WEB_RESEARCH", "false").strip().lower() == "true"
        and bool(os.getenv("SERPER_API_KEY", "").strip())
    )


def _research_tools() -> list:
    if not web_research_enabled():
        return []
    try:
        from crewai_tools import SerperDevTool
    except ImportError as error:
        raise CrewConfigurationError(
            "Optional web research is enabled, but CrewAI Serper tools are unavailable."
        ) from error
    return [SerperDevTool()]


def build_crew() -> Crew:
    try:
        from crewai import Agent, Crew, LLM, Process, Task
    except ImportError as error:
        raise CrewConfigurationError("CrewAI dependencies are not installed.") from error

    if os.getenv("AAMAD_TARGET_RUNTIME", "crewai").strip().lower() != "crewai":
        raise CrewConfigurationError("This backend requires AAMAD_TARGET_RUNTIME=crewai.")

    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        raise CrewConfigurationError("OPENAI_API_KEY is required to run the crew.")

    agents_config = _load_yaml(CONFIG_DIR / "agents.yaml")
    tasks_config = _load_yaml(CONFIG_DIR / "tasks.yaml")
    model = os.getenv("OPENAI_MODEL", "gpt-4o").strip() or "gpt-4o"
    llm = LLM(model=f"openai/{model}", api_key=api_key, temperature=0, max_tokens=2048)

    researcher = Agent(
        config=agents_config["researcher"],
        llm=llm,
        tools=_research_tools(),
        memory=False,
    )
    evaluator = Agent(config=agents_config["evaluator"], llm=llm, memory=False)
    recommender = Agent(config=agents_config["recommender"], llm=llm, memory=False)

    research_task = Task(config=tasks_config["research_candidates_task"], agent=researcher)
    evaluate_task = Task(
        config=tasks_config["evaluate_candidates_task"],
        agent=evaluator,
        context=[research_task],
    )
    recommend_task = Task(
        config=tasks_config["recommend_candidates_task"],
        agent=recommender,
        context=[research_task, evaluate_task],
    )

    return Crew(
        agents=[researcher, evaluator, recommender],
        tasks=[research_task, evaluate_task, recommend_task],
        process=Process.sequential,
        memory=False,
        max_rpm=10,
        verbose=False,
    )


def run_crew(job_requirements: str, candidate_profiles: str = "") -> str:
    use_web_research = web_research_enabled()
    profiles = candidate_profiles.strip()
    if not profiles and not use_web_research:
        profiles = FIXTURE_CANDIDATES

    result = build_crew().kickoff(
        inputs={
            "job_requirements": job_requirements,
            "candidate_profiles": profiles,
        }
    )
    report = getattr(result, "raw", None) or str(result)
    validate_report(report)
    return report


def validate_report(report: str) -> None:
    if not isinstance(report, str) or not report.strip():
        raise ReportValidationError("The crew returned an empty report.")
    if report.lstrip().startswith("```"):
        raise ReportValidationError("The report must not be wrapped in a code fence.")
    missing_headings = [heading for heading in REQUIRED_REPORT_HEADINGS if heading not in report]
    if missing_headings:
        raise ReportValidationError("The report is missing required sections.")