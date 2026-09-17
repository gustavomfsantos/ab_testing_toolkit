"""Power and sample-size planning utilities."""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from statsmodels.stats.power import NormalIndPower
from statsmodels.stats.proportion import proportion_effectsize

from logger import get_logger

logger = get_logger(__name__)


def calculate_sample_size(
    base_rate: float,
    mde: float,
    alpha: float,
    power: float,
) -> int:
    """Calculate users needed in each group for a binary metric.

    Args:
        base_rate: Current conversion probability in the control group.
        mde: Minimum absolute conversion-rate change worth detecting.
        alpha: Type-I error rate for the planned two-sided test.
        power: Desired probability of detecting the MDE.

    Returns:
        The rounded-up sample size required per group.
    """
    treatment_rate = base_rate + mde
    if not 0 < base_rate < 1 or not 0 < treatment_rate < 1:
        raise ValueError("Both rates must be strictly between 0 and 1.")
    effect_size = proportion_effectsize(base_rate, treatment_rate)
    analysis = NormalIndPower()
    sample_size = int(
        np.ceil(
            analysis.solve_power(
                effect_size=abs(effect_size),
                alpha=alpha,
                power=power,
                ratio=1.0,
                alternative="two-sided",
            )
        )
    )
    logger.info(
        "At MDE=%.3f, you need %d users per group to detect the effect "
        "%.0f%% of the time",
        mde,
        sample_size,
        power * 100,
    )
    return sample_size


def calculate_power_for_n(
    n: int,
    base_rate: float,
    mde: float,
    alpha: float,
) -> float:
    """Calculate achieved power for a proposed group size.

    Args:
        n: Number of users in each experiment group.
        base_rate: Current conversion probability in control.
        mde: Absolute effect to detect.
        alpha: Type-I error rate for the planned test.

    Returns:
        Achieved statistical power as a value between zero and one.
    """
    if n <= 0:
        raise ValueError("Sample size must be positive.")
    effect_size = proportion_effectsize(base_rate, base_rate + mde)
    power = NormalIndPower().power(
        effect_size=abs(effect_size),
        nobs1=n,
        alpha=alpha,
        ratio=1.0,
        alternative="two-sided",
    )
    return float(power)


def plot_power_curve(
    base_rate: float,
    mde: float,
    alpha: float,
    n_range: range,
    output_path: str,
) -> None:
    """Save a chart showing power as the sample size increases.

    Args:
        base_rate: Current conversion probability in control.
        mde: Absolute effect to detect.
        alpha: Type-I error rate for the planned test.
        n_range: Candidate per-group sample sizes to plot.
        output_path: File path where the chart should be saved.

    Returns:
        None.
    """
    sample_sizes = list(n_range)
    powers = [calculate_power_for_n(n, base_rate, mde, alpha) for n in sample_sizes]
    planned_n = calculate_sample_size(base_rate, mde, alpha, 0.80)
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    plt.figure(figsize=(9, 5))
    plt.plot(sample_sizes, powers, color="#176b87", linewidth=2)
    plt.axhline(0.80, color="#c44e52", linestyle="--", label="Target Power")
    plt.axvline(planned_n, color="#4c8c4a", linestyle=":", label=f"N = {planned_n}")
    plt.xlabel("Users per group")
    plt.ylabel("Chance of detecting the planned effect")
    plt.title("More users increase the chance of detecting a real effect")
    plt.ylim(0, 1.05)
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()
    logger.info("Saved power curve to %s", output_path)


def plot_sample_size_vs_mde(
    base_rate: float,
    alpha: float,
    power: float,
    mde_range: list[float],
    output_path: str,
) -> None:
    """Save a chart showing the sample-size cost of smaller effects.

    Args:
        base_rate: Current conversion probability in control.
        alpha: Type-I error rate for the planned test.
        power: Desired probability of detecting each effect.
        mde_range: Absolute effects to compare.
        output_path: File path where the chart should be saved.

    Returns:
        None.
    """
    sample_sizes = [
        calculate_sample_size(base_rate, mde, alpha, power) for mde in mde_range
    ]
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    plt.figure(figsize=(9, 5))
    plt.plot(mde_range, sample_sizes, marker="o", color="#d17a22")
    plt.xlabel("Minimum detectable effect (absolute conversion-rate change)")
    plt.ylabel("Users needed per group")
    plt.title("Detecting smaller effects requires exponentially more data")
    for mde, sample_size in zip(mde_range, sample_sizes):
        plt.annotate(f"{sample_size:,}", (mde, sample_size), xytext=(0, 7),
                     textcoords="offset points", ha="center")
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()
    logger.info("Saved sample-size sensitivity chart to %s", output_path)
