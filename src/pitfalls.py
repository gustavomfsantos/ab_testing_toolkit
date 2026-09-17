"""Simulations of common mistakes in experiment analysis."""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from logger import get_logger
from src.stats import run_proportions_ztest

logger = get_logger(__name__)


def simulate_peeking(
    n_simulations: int,
    n_per_group: int,
    base_rate: float,
    peek_intervals: list[int],
    alpha: float,
    random_seed: int,
) -> pd.DataFrame:
    """Estimate false-positive inflation from repeatedly checking results.

    Each simulation creates one null experiment and evaluates growing prefixes
    of the same data. The reported rate is the chance of having seen a false
    positive by each checkpoint, which captures the optional-stopping problem.

    Args:
        n_simulations: Number of null experiments to simulate.
        n_per_group: Maximum users available per group.
        base_rate: Shared conversion probability under the null hypothesis.
        peek_intervals: Cumulative per-group sample sizes to inspect.
        alpha: Nominal significance threshold.
        random_seed: Seed for reproducible simulation.

    Returns:
        A DataFrame with the checkpoint, cumulative false-positive rate, and
        count of simulations that had crossed the threshold.
    """
    if not peek_intervals or max(peek_intervals) > n_per_group:
        raise ValueError("Peek intervals must be non-empty and fit within n_per_group.")
    intervals = sorted(set(peek_intervals))
    rng = np.random.default_rng(random_seed)
    crossed_counts = np.zeros(len(intervals), dtype=int)

    logger.info(
        "Under H0 with no peeking, FPR should be 5%%. Peeking inflates this."
    )
    for _ in range(n_simulations):
        control = rng.binomial(1, base_rate, n_per_group)
        treatment = rng.binomial(1, base_rate, n_per_group)
        already_significant = False
        for index, interval in enumerate(intervals):
            result = run_proportions_ztest(
                int(control[:interval].sum()),
                interval,
                int(treatment[:interval].sum()),
                interval,
            )
            already_significant = already_significant or result["p_value"] < alpha
            crossed_counts[index] += int(already_significant)

    results = pd.DataFrame(
        {
            "peek_interval": intervals,
            "false_positive_rate": crossed_counts / n_simulations,
            "false_positives": crossed_counts,
            "n_simulations": n_simulations,
        }
    )
    for row in results.itertuples(index=False):
        logger.info(
            "Peek at n=%d per group: cumulative FPR=%.3f",
            row.peek_interval,
            row.false_positive_rate,
        )
    return results


def simulate_multiple_comparisons(
    n_metrics: int,
    n_simulations: int,
    alpha: float,
    random_seed: int,
) -> dict:
    """Estimate false positives when many null metrics are tested together.

    Args:
        n_metrics: Number of independent metrics tested per experiment.
        n_simulations: Number of simulated experiments.
        alpha: Per-metric significance threshold.
        random_seed: Seed for reproducible simulation.

    Returns:
        A dictionary containing observed and theoretical family-wise false
        positive rates and the expected false positives per experiment.
    """
    rng = np.random.default_rng(random_seed)
    p_values = rng.uniform(0, 1, size=(n_simulations, n_metrics))
    observed_fpr = float(np.mean(np.any(p_values < alpha, axis=1)))
    theoretical_fpr = float(1 - (1 - alpha) ** n_metrics)
    expected_false_positives = n_metrics * alpha
    logger.info(
        "With %d metrics at alpha=%.2f, expected false positives per "
        "experiment: %.1f",
        n_metrics,
        alpha,
        expected_false_positives,
    )
    logger.info(
        "Multiple-comparison FPR: observed=%.3f, theoretical=%.3f",
        observed_fpr,
        theoretical_fpr,
    )
    return {
        "observed_fpr": observed_fpr,
        "theoretical_fpr": theoretical_fpr,
        "expected_false_positives": expected_false_positives,
    }


def generate_simpsons_paradox_data(random_seed: int) -> pd.DataFrame:
    """Create a table where aggregate and segment conclusions disagree.

    The paradox is like comparing two hospitals when one receives mostly easy
    cases and the other mostly complex cases: the mix of cases can reverse the
    overall ranking even when treatment performs worse in every segment.

    Args:
        random_seed: Seed accepted for a reproducible educational API.

    Returns:
        A DataFrame containing group, segment, conversions, totals, and rates.
    """
    np.random.default_rng(random_seed)
    records = [
        {"group": "control", "segment": "high_intent", "conversions": 90,
         "total": 100},
        {"group": "treatment", "segment": "high_intent", "conversions": 17,
         "total": 20},
        {"group": "control", "segment": "low_intent", "conversions": 180,
         "total": 900},
        {"group": "treatment", "segment": "low_intent", "conversions": 12,
         "total": 80},
    ]
    data = pd.DataFrame(records)
    data["conversion_rate"] = data["conversions"] / data["total"]
    logger.info(
        "Generated Simpson's paradox data: treatment loses within each "
        "segment but wins in the aggregate because allocation differs."
    )
    return data


def plot_peeking_fpr(
    peeking_results: pd.DataFrame,
    alpha: float,
    output_path: str,
) -> None:
    """Save a chart showing false-positive inflation during peeking.

    Args:
        peeking_results: Output from :func:`simulate_peeking`.
        alpha: Nominal per-look significance threshold.
        output_path: File path where the chart should be saved.

    Returns:
        None.
    """
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    plt.figure(figsize=(9, 5))
    plt.bar(
        peeking_results["peek_interval"].astype(str),
        peeking_results["false_positive_rate"],
        color="#7a5195",
    )
    plt.axhline(alpha, color="#c44e52", linestyle="--",
                label=f"Nominal alpha ({alpha:.2f})")
    plt.xlabel("Users per group checked")
    plt.ylabel("Chance of a false positive by this check")
    plt.title("Repeatedly checking an experiment raises false-positive risk")
    plt.ylim(0, 1)
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()
    logger.info("Saved peeking false-positive chart to %s", output_path)
