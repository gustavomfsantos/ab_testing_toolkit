"""Run a complete educational A/B testing analysis from simulation to report.

This project demonstrates how experiment data is generated, tested, planned,
and stress-tested against common statistical pitfalls. Every result is
reproducible from the configuration constants so the workflow can serve as a
portfolio example and a compact learning reference.
"""

from pathlib import Path

from config import (
    ALPHA,
    BASE_CONVERSION_RATE,
    MINIMUM_DETECTABLE_EFFECT,
    PLOT_OUTPUT_DIR,
    POWER,
    RANDOM_SEED,
    SAMPLE_SIZE_PER_GROUP,
)
from logger import get_logger
from src.pitfalls import (
    generate_simpsons_paradox_data,
    plot_peeking_fpr,
    simulate_multiple_comparisons,
    simulate_peeking,
)
from src.power import (
    calculate_sample_size,
    plot_power_curve,
    plot_sample_size_vs_mde,
)
from src.reporting import print_experiment_report, summarize_power_analysis
from src.simulation import generate_experiment_data
from src.stats import run_proportions_ztest

logger = get_logger(__name__)


def main() -> None:
    """Run all toolkit demonstrations and save their plots.

    Args:
        None.

    Returns:
        None.
    """
    Path(PLOT_OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

    logger.info("=" * 60)
    logger.info("SECTION 1: DATA SIMULATION")
    simulation_df = generate_experiment_data(
        SAMPLE_SIZE_PER_GROUP,
        SAMPLE_SIZE_PER_GROUP,
        BASE_CONVERSION_RATE,
        MINIMUM_DETECTABLE_EFFECT,
        RANDOM_SEED,
    )

    logger.info("=" * 60)
    logger.info("SECTION 2: STATISTICAL TESTS")
    control = simulation_df[simulation_df["group"] == "control"]
    treatment = simulation_df[simulation_df["group"] == "treatment"]
    test_result = run_proportions_ztest(
        int(control["converted"].sum()),
        len(control),
        int(treatment["converted"].sum()),
        len(treatment),
    )

    logger.info("=" * 60)
    logger.info("SECTION 3: POWER ANALYSIS & PLOTS")
    sample_size = calculate_sample_size(
        BASE_CONVERSION_RATE,
        MINIMUM_DETECTABLE_EFFECT,
        ALPHA,
        POWER,
    )
    plot_power_curve(
        BASE_CONVERSION_RATE,
        MINIMUM_DETECTABLE_EFFECT,
        ALPHA,
        range(500, 6001, 500),
        str(Path(PLOT_OUTPUT_DIR) / "power_curve.png"),
    )
    plot_sample_size_vs_mde(
        BASE_CONVERSION_RATE,
        ALPHA,
        POWER,
        [0.005, 0.01, 0.02, 0.03, 0.04],
        str(Path(PLOT_OUTPUT_DIR) / "sample_size_vs_mde.png"),
    )

    logger.info("=" * 60)
    logger.info("SECTION 4: PITFALL SIMULATIONS & PLOTS")
    peeking_results = simulate_peeking(
        500,
        SAMPLE_SIZE_PER_GROUP,
        BASE_CONVERSION_RATE,
        [500, 1000, 1500, 2000, 3000],
        ALPHA,
        RANDOM_SEED,
    )
    plot_peeking_fpr(
        peeking_results,
        ALPHA,
        str(Path(PLOT_OUTPUT_DIR) / "peeking_false_positive_rate.png"),
    )
    simulate_multiple_comparisons(20, 1000, ALPHA, RANDOM_SEED)
    generate_simpsons_paradox_data(RANDOM_SEED)

    logger.info("=" * 60)
    logger.info("SECTION 5: STAKEHOLDER REPORT")
    power_summary = summarize_power_analysis(
        sample_size,
        MINIMUM_DETECTABLE_EFFECT,
        ALPHA,
        POWER,
    )
    print_experiment_report(simulation_df, test_result, power_summary)
    logger.info(
        "All plots saved to plots/ — run notebooks/exploration.ipynb "
        "for interactive walkthrough"
    )


if __name__ == "__main__":
    main()
