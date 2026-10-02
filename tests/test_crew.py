from types import SimpleNamespace

import pytest
from crewai import Process

from recruitment_assistant import crew as crew_module

VALID_REPORT = """\
## Advisory
Recruiter review required.
## Ranked Recommendations
Candidate A, 80/100.
## Evidence and Uncertainty
Contact: unknown - verify.
## Outreach Drafts
Draft only.
"""


def test_crew_has_three_sequential_agents_and_context_chain(monkeypatch):
    monkeypatch.setenv("AAMAD_TARGET_RUNTIME", "crewai")
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("AAMAD_ENABLE_WEB_RESEARCH", "false")
    monkeypatch.delenv("SERPER_API_KEY", raising=False)

    crew = crew_module.build_crew()

    assert crew.process == Process.sequential
    assert [agent.role for agent in crew.agents] == [
        "Job Candidate Researcher",
        "Candidate Evaluator",
        "Candidate Recommender",
    ]
    assert [task.name for task in crew.tasks] == [
        "research_candidates_task",
        "evaluate_candidates_task",
        "recommend_candidates_task",
    ]
    assert crew.tasks[1].context == [crew.tasks[0]]
    assert crew.tasks[2].context == [crew.tasks[0], crew.tasks[1]]
    assert all(
        agent.allow_delegation is False
        and agent.max_iter == 8
        and agent.max_retry_limit == 2
        and agent.max_execution_time == 480
        for agent in crew.agents
    )
    assert crew.memory is False
    assert crew.max_rpm == 10
    assert crew.agents[0].tools == []


def test_fixture_profiles_are_injected_for_offline_run(monkeypatch):
    captured_inputs = {}

    class FakeCrew:
        def kickoff(self, inputs):
            captured_inputs.update(inputs)
            return SimpleNamespace(raw=VALID_REPORT)

    monkeypatch.setattr(crew_module, "build_crew", FakeCrew)
    monkeypatch.setenv("AAMAD_ENABLE_WEB_RESEARCH", "false")
    monkeypatch.delenv("SERPER_API_KEY", raising=False)

    report = crew_module.run_crew("Python backend engineer")

    assert report == VALID_REPORT
    assert "Candidate A" in captured_inputs["candidate_profiles"]
    assert "unknown - verify" in captured_inputs["candidate_profiles"]


@pytest.mark.parametrize(
    "report",
    ["", "```markdown\n" + VALID_REPORT + "\n```", "## Advisory\nIncomplete"],
)
def test_invalid_report_is_rejected(report):
    with pytest.raises(crew_module.ReportValidationError):
        crew_module.validate_report(report)


def test_web_research_requires_both_opt_in_and_key(monkeypatch):
    monkeypatch.setenv("AAMAD_ENABLE_WEB_RESEARCH", "true")
    monkeypatch.delenv("SERPER_API_KEY", raising=False)
    assert crew_module.web_research_enabled() is False

    monkeypatch.setenv("SERPER_API_KEY", "test-key")
    assert crew_module.web_research_enabled() is True