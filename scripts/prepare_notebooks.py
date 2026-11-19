"""Build lightweight research notebooks; computations stay in reusable modules."""
import json
from pathlib import Path

TOPICS = [
    ("01_market_overview", "Actual market observations", "reports/market_summary.json"),
    ("02_volatility_diagnostics", "Historical volatility; no log returns", "reports/volatility_metrics.parquet"),
    ("03_price_spikes", "Native negative-price episodes", "reports/negative_price_events.csv"),
    ("04_fundamental_drivers", "Fundamental coverage; analysis pending validated ENTSO-E data", "reports/data_availability_report.csv"),
    ("05_volatility_regimes", "Lagged states with 2023 calibration", "reports/regime_transitions.csv"),
    ("06_forecast_validation", "Exploratory walk-forward forecasts; vintage history unverified", "reports/model_comparison.csv"),
]

Path("notebooks").mkdir(exist_ok=True)
for name, title, source in TOPICS:
    imports = "import json\n" if source.endswith("json") else "import pandas as pd\n"
    code = ("from pathlib import Path\n" + imports +
            "root = Path.cwd() if Path('reports').exists() else Path.cwd().parent\n"
            f"path = root / {source!r}\n"
            "if not path.exists():\n    raise FileNotFoundError('Run the README pipeline first')\n")
    code += ("result = json.loads(path.read_text())\n" if source.endswith("json") else
             "result = pd.read_parquet(path)\n" if source.endswith("parquet") else "result = pd.read_csv(path)\n")
    code += "result\n"
    notebook = {"nbformat": 4, "nbformat_minor": 5,
                "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"}},
                "cells": [{"id": name + "-intro", "cell_type": "markdown", "metadata": {},
                           "source": [f"# {title}\n", "Generated outputs only. Source: Bundesnetzagentur | SMARD.de.\n",
                                      "Run project modules using the README commands; no synthetic research observations.\n"]},
                          {"id": name + "-read", "cell_type": "code", "metadata": {}, "execution_count": None,
                           "outputs": [], "source": code.splitlines(keepends=True)}]}
    Path(f"notebooks/{name}.ipynb").write_text(json.dumps(notebook, indent=2), encoding="utf-8")

for layer in ["raw", "processed", "features"]:
    Path(f"data/{layer}/.gitkeep").touch()
