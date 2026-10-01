import asyncio

import typer

app = typer.Typer(help="jobhound: agente de busca de vagas compatíveis com seu perfil")


@app.command()
def run(
    profile: str | None = typer.Option(None, help="Slug do perfil (padrão: o editado por último)"),
) -> None:
    """Executa o pipeline: busca vagas, avalia matches e notifica."""
    from src.app.dto.pipeline_report import PipelineReport
    from src.container import build_pipeline

    async def _run() -> PipelineReport:
        pipeline = await build_pipeline(profile)
        return await pipeline.execute()

    report = asyncio.run(_run())
    typer.echo(
        f"Vagas novas: {report.fetched} | matches: {report.matched} | "
        f"revisão manual: {report.manual_review} | erros: {report.errors}"
    )


@app.command()
def top(
    limit: int = typer.Option(10, help="Quantidade de vagas"),
    profile: str | None = typer.Option(None, help="Slug do perfil (padrão: todos)"),
) -> None:
    """Lista as vagas com maior score."""
    from src.container import build_top_matches

    matches = asyncio.run(build_top_matches().execute(limit, profile))
    for job, result in matches:
        typer.echo(f"[{result.score.value:>3}] {job.title} — {job.company} ({job.url})")


if __name__ == "__main__":
    app()
