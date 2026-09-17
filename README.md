# A/B Testing Toolkit

> A hands-on Python toolkit for understanding, implementing, and stress-testing
> A/B testing concepts used in product analytics and data science.

## Why This Project

This project was built to deeply understand experiment design concepts used in
product data science roles. It emphasizes implementation, simulation, and clear
communication so statistical knowledge is demonstrated rather than memorized.

## Concepts Covered

- **Hypothesis Testing** — z-test, t-test, chi-square from scratch with intuitive explanations
- **Power & Sample Size** — calculating required N before launching an experiment
- **The Peeking Problem** — simulating how p-hacking inflates false positive rates
- **Multiple Comparisons** — Bonferroni and FDR correction
- **Simpson's Paradox** — when aggregate results lie
- **Stakeholder Reporting** — translating statistical results into business language

## Project Structure

```text
ab_testing_toolkit/
├── main.py                 # Runs the complete educational workflow
├── config.py               # Central experiment-design constants
├── logger.py               # Consistent, auditable runtime logging
├── requirements.txt        # Python dependencies
├── README.md               # Project guide and statistical takeaways
├── .gitignore              # Python and generated-artifact exclusions
├── src/
│   ├── __init__.py         # Source package marker
│   ├── simulation.py       # Reproducible experiment data generation
│   ├── stats.py             # Proportion, t, and chi-square tests
│   ├── power.py             # Sample-size planning and power plots
│   ├── pitfalls.py          # Peeking, comparisons, and Simpson's paradox
│   └── reporting.py         # Plain-English experiment summaries
├── notebooks/
│   ├── README.md            # Notebook purpose and concept guide
│   └── exploration.ipynb    # Interactive module-by-module walkthrough
└── plots/
    └── .gitkeep             # Keeps the generated-chart directory in Git
```

## How to Run

1. Clone the repository and enter the project directory.
2. Create and activate a virtual environment: `python -m venv .venv`.
3. Install dependencies: `pip install -r requirements.txt`.
4. Run the end-to-end workflow: `python main.py`.
5. Open `notebooks/exploration.ipynb` in Jupyter or VS Code for the interactive walkthrough.

## Example Output

See the `plots/` folder and run `main.py` to generate charts.

## Key Takeaways

- Sample size must be calculated **before** the experiment, not adjusted after seeing early results.
- A statistically significant result can still be too small to matter to the business.
- Repeatedly checking an experiment changes the false-positive rate unless the analysis plan accounts for it.
- Testing many metrics creates more chances to find a misleading result by accident.
- Aggregate results should be checked by meaningful segments before turning them into product decisions.

## Tech Stack

Python · NumPy · Pandas · SciPy · Statsmodels · Matplotlib · Seaborn
