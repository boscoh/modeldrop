import logging
from pathlib import Path
from typing import Annotated

import cyclopts

from modeldrop.app import open_url_in_background

app = cyclopts.App(
    name="modeldrop",
    help="Mathematical modeling with interactive Dash visualizations.",
)


@app.command
def serve(
    *,
    port: int = 8050,
    open: Annotated[bool, cyclopts.Parameter(name=["-o", "--open"])] = False,
    reload: Annotated[bool, cyclopts.Parameter(name=["-r", "--reload"])] = False,
) -> None:
    """Start the Dash server."""
    logging.basicConfig(level=logging.DEBUG if reload else logging.WARNING)
    from modeldrop.main import dash_app

    if open:
        open_url_in_background(f"http://127.0.0.1:{port}/")
    dash_app.run_server(port=str(port), is_debug=reload)


@app.command
def graph(
    model: str,
    output_dir: Path = Path("."),
    *,
    transparent: bool = False,
) -> None:
    """Generate PNG graphs for a model.

    Parameters
    ----------
    model
        Model name. One of: growth, spring, ecology, epi, goodwin, keen,
        turchin, demo, fathers, property.
    output_dir
        Directory to write PNG files into.
    transparent
        Render graph backgrounds as transparent.
    """
    from modeldrop.main import MODEL_REGISTRY
    from modeldrop.modelgraph import make_graphs_from_model

    if model not in MODEL_REGISTRY:
        names = ", ".join(MODEL_REGISTRY)
        raise SystemExit(f"Unknown model '{model}'. Available: {names}")

    instance = MODEL_REGISTRY[model]()
    output_dir.mkdir(parents=True, exist_ok=True)
    make_graphs_from_model(instance, str(output_dir), transparent=transparent)


def main() -> None:
    app()
