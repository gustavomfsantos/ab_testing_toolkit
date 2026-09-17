"""Plain-English translations of statistical results."""

import pandas as pd

from logger import get_logger

logger = get_logger(__name__)


def summarize_test_result(
    test_result: dict,
    metric_name: str,
    control_rate: float,
    treatment_rate: float,
) -> str:
    """Translate an experiment result into a paragraph for a PM.

    Args:
        test_result: Result dictionary containing at least p_value and significant.
        metric_name: Human-readable name of the outcome metric.
        control_rate: Observed control metric value.
        treatment_rate: Observed treatment metric value.

    Returns:
        A plain-English summary with lifts, evidence, and a recommendation.

    Example:
        ``"Conversion rate increased by 2.0 percentage points (20.0% relative
        lift). The p-value was 0.01, so the result is statistically significant.
        Recommendation: consider rolling out treatment."``
    """
    absolute_lift = treatment_rate - control_rate
    relative_lift = absolute_lift / control_rate if control_rate else 0.0
    p_value = float(test_result["p_value"])
    significant = bool(test_result["significant"])
    direction = "increased" if absolute_lift >= 0 else "decreased"
    evidence = (
        "statistically significant"
        if significant
        else "not statistically significant"
    )
    if significant and absolute_lift > 0:
        recommendation = "consider rolling out the treatment"
    elif significant and absolute_lift < 0:
        recommendation = "do not roll out the treatment"
    else:
        recommendation = "collect more evidence before making a rollout decision"
    return (
        f"{metric_name} {direction} by {absolute_lift * 100:.2f} "
        f"percentage points ({relative_lift:.1%} relative lift). "
        f"The p-value was {p_value:.4f}, "
        f"so the result is {evidence}. Recommendation: {recommendation}."
    )


def summarize_power_analysis(
    sample_size: int,
    mde: float,
    alpha: float,
    power: float,
) -> str:
    """Explain an experiment's sample-size plan in business language.

    Args:
        sample_size: Planned users per group.
        mde: Smallest absolute effect worth detecting.
        alpha: Planned false-positive tolerance.
        power: Planned probability of detecting the MDE.

    Returns:
        A concise explanation of the sample-size decision.
    """
    return (
        f"We need {sample_size:,} users per group to have a {power:.0%} chance "
        f"of detecting a real conversion-rate change of at least {mde:.1%}. "
        f"The plan uses a {alpha:.1%} false-positive threshold, so smaller "
        "effects may be real but are intentionally outside this decision rule."
    )


def print_experiment_report(
    simulation_df: pd.DataFrame,
    test_result: dict,
    power_summary: str,
) -> None:
    """Log an end-to-end experiment report with readable section headers.

    Args:
        simulation_df: Simulated experiment data with group and converted columns.
        test_result: Statistical test result for the simulated data.
        power_summary: Plain-English power analysis summary.

    Returns:
        None.
    """
    rates = simulation_df.groupby("group")["converted"].mean()
    summary = summarize_test_result(
        test_result,
        "Conversion rate",
        rates["control"],
        rates["treatment"],
    )
    logger.info("=" * 60)
    logger.info("STAKEHOLDER EXPERIMENT REPORT")
    logger.info("Sample: %d users across %d groups", len(simulation_df), 2)
    logger.info("Result: %s", summary)
    logger.info("Power plan: %s", power_summary)
    logger.info("=" * 60)
