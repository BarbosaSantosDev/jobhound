"""Lógica de score: determinística no domínio.

O LLM extrai fatos (JobFacts); esta política decide o score.
"""

from dataclasses import dataclass, field

from src.domain.entity.job_facts import JobFacts
from src.domain.entity.match_result import MatchResult
from src.domain.entity.profile import Profile
from src.domain.value_object.match_score import MatchScore
from src.domain.value_object.seniority import Seniority
from src.domain.value_object.work_mode import WorkMode


@dataclass(frozen=True)
class ScoreInput:
    job_id: str
    facts: JobFacts
    profile: Profile


@dataclass
class _Scorecard:
    """Acumulador de uma única avaliação — nasce e morre dentro de evaluate()."""

    score: int = 0
    reasons: list[str] = field(default_factory=list)
    red_flags: list[str] = field(default_factory=list)


class ScoreJob:
    """Domain service stateless: uma instância avalia N vagas sem interferência."""

    def evaluate(self, input: ScoreInput) -> MatchResult:
        card = _Scorecard()
        self._stack(card, input)
        self._seniority(card, input)
        self._location(card, input)
        return MatchResult(
            job_id=input.job_id,
            score=MatchScore(value=min(card.score, 100)),
            reasons=card.reasons,
            red_flags=card.red_flags,
        )

    def _stack(self, card: _Scorecard, input: ScoreInput) -> None:
        # Stack (peso 50) — comparada contra a stack do perfil, não fixa em nenhuma linguagem.
        mentioned = {s.lower() for s in input.facts.mentioned_stack}
        primary = {s.lower() for s in input.profile.primary_stack}
        secondary = {s.lower() for s in input.profile.secondary_stack}

        primary_hits = mentioned & primary
        secondary_hits = mentioned & secondary

        if primary_hits:
            card.score += 35
            card.reasons.append(f"Vaga menciona stack principal: {', '.join(sorted(primary_hits))}")
        if secondary_hits:
            card.score += 15
            card.reasons.append(f"Vaga menciona stack secundária: {', '.join(sorted(secondary_hits))}")

        other_required = mentioned - primary - secondary
        if not primary_hits and other_required:
            card.red_flags.append("stack_incompatible")
            card.reasons.append(
                f"Stack exigida incompatível: {', '.join(sorted(other_required))}"
            )

    def _seniority(self, card: _Scorecard, input: ScoreInput) -> None:
        # Senioridade (peso 30)
        if input.facts.seniority == Seniority(input.profile.seniority):
            card.score += 30
            card.reasons.append("Senioridade compatível")
        elif input.facts.seniority == Seniority.NOT_INFORMED:
            card.score += 15
            card.reasons.append("Senioridade não informada")
        elif (
            input.facts.seniority == Seniority.SENIOR
            and input.profile.seniority == "pleno"
        ):
            card.score += 5
            card.reasons.append("Vaga sênior — possível stretch")
        else:
            card.red_flags.append("seniority_mismatch")
            card.reasons.append(
                f"Senioridade incompatível: {input.facts.seniority.value}"
            )

    def _location(self, card: _Scorecard, input: ScoreInput) -> None:
        # Localização / modo de trabalho (peso 20)
        if input.facts.work_mode == WorkMode.REMOTE and input.profile.accepts_remote:
            card.score += 20
            card.reasons.append("Vaga remota")
        elif input.facts.location_city and any(
            loc.lower() in input.facts.location_city.lower()
            for loc in input.profile.preferred_locations
        ):
            card.score += 20
            card.reasons.append(f"Localização compatível: {input.facts.location_city}")
        elif input.facts.work_mode == WorkMode.NOT_INFORMED:
            card.score += 10
            card.reasons.append("Modo de trabalho não informado")
        else:
            card.reasons.append("Localização/modo de trabalho fora das preferências")