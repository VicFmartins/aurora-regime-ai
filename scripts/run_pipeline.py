"""CLI entrypoint for the Aurora end-to-end pipeline."""

from __future__ import annotations

import argparse

from aurora import format_pipeline_summary, load_config, run_full_pipeline, run_offline_pipeline


def build_parser() -> argparse.ArgumentParser:
    """Create the command-line parser for pipeline execution."""
    parser = argparse.ArgumentParser(description="Executa o pipeline completo do Aurora Regime AI.")
    parser.add_argument(
        "--force-download",
        action="store_true",
        help="Ignora o cache local e tenta baixar novamente os dados online.",
    )
    parser.add_argument(
        "--offline",
        action="store_true",
        help="Executa o pipeline em modo offline usando CSV de exemplo ou dados sinteticos.",
    )
    return parser


def main() -> None:
    """Run the Aurora pipeline from the command line."""
    args = build_parser().parse_args()
    config = load_config()

    try:
        if args.offline:
            result = run_offline_pipeline(config)
        else:
            result = run_full_pipeline(config, force_download=args.force_download)
    except (FileNotFoundError, RuntimeError, ValueError) as exc:
        raise SystemExit(f"Erro ao executar o pipeline Aurora: {exc}") from exc

    print(format_pipeline_summary(result))


if __name__ == "__main__":
    main()
