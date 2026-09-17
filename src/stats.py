"""Classical hypothesis tests for A/B testing metrics."""

from math import sqrt

import numpy as np
from scipy import stats

from logger import get_logger

logger = get_logger(__name__)

# A two-sample proportions z-test uses a normal approximation to the sampling
# distribution of a difference in rates. It is appropriate for binary outcomes
# with sufficiently large expected counts; use a t-test for continuous values.


def run_proportions_ztest(
    control_conversions: int,
    control_n: int,
    treatment_conversions: int,
    treatment_n: int,
) -> dict:
    """Test whether two independent conversion rates differ.

    Args:
        control_conversions: Number of conversions in control.
        control_n: Number of control observations.
        treatment_conversions: Number of conversions in treatment.
        treatment_n: Number of treatment observations.

    Returns:
        A dictionary containing the z statistic, p-value, significance verdict,
        and a 95 percent confidence interval for treatment minus control.
    """
    if control_n <= 0 or treatment_n <= 0:
        raise ValueError("Sample sizes must be positive.")
    if not 0 <= control_conversions <= control_n:
        raise ValueError("Control conversions must be within the sample size.")
    if not 0 <= treatment_conversions <= treatment_n:
        raise ValueError("Treatment conversions must be within the sample size.")

    control_rate = control_conversions / control_n
    treatment_rate = treatment_conversions / treatment_n
    pooled_rate = (control_conversions + treatment_conversions) / (
        control_n + treatment_n
    )
    standard_error = sqrt(
        pooled_rate * (1 - pooled_rate) * (1 / control_n + 1 / treatment_n)
    )
    difference = treatment_rate - control_rate
    z_statistic = difference / standard_error if standard_error else 0.0
    p_value = 2 * stats.norm.sf(abs(z_statistic))
    unpooled_error = sqrt(
        control_rate * (1 - control_rate) / control_n
        + treatment_rate * (1 - treatment_rate) / treatment_n
    )
    margin = stats.norm.ppf(0.975) * unpooled_error
    result = {
        "z_statistic": z_statistic,
        "p_value": p_value,
        "significant": bool(p_value < 0.05),
        "confidence_interval_diff": (
            difference - margin,
            difference + margin,
        ),
    }
    logger.debug(
        "Two-proportion z-test: z=%.3f, p=%.4g, significant=%s",
        z_statistic,
        p_value,
        result["significant"],
    )
    return result


def run_ttest(control_values: list[float], treatment_values: list[float]) -> dict:
    """Test whether two independent continuous metric means differ.

    A t-test is preferable to the proportions z-test for metrics such as
    revenue per user because the observations are numeric rather than binary.
    Welch's version does not assume equal variance between groups.

    Args:
        control_values: Continuous observations from the control group.
        treatment_values: Continuous observations from the treatment group.

    Returns:
        A dictionary with the t statistic, p-value, significance verdict, and
        a 95 percent confidence interval for treatment minus control.
    """
    if not control_values or not treatment_values:
        raise ValueError("Both groups must contain observations.")

    control = np.asarray(control_values, dtype=float)
    treatment = np.asarray(treatment_values, dtype=float)
    test = stats.ttest_ind(treatment, control, equal_var=False)
    difference = float(np.mean(treatment) - np.mean(control))
    control_variance = np.var(control, ddof=1) / len(control)
    treatment_variance = np.var(treatment, ddof=1) / len(treatment)
    standard_error = sqrt(control_variance + treatment_variance)
    degrees_of_freedom = (control_variance + treatment_variance) ** 2 / (
        control_variance**2 / (len(control) - 1)
        + treatment_variance**2 / (len(treatment) - 1)
    )
    margin = stats.t.ppf(0.975, degrees_of_freedom) * standard_error
    result = {
        "t_statistic": float(test.statistic),
        "p_value": float(test.pvalue),
        "significant": bool(test.pvalue < 0.05),
        "confidence_interval_diff": (
            difference - margin,
            difference + margin,
        ),
    }
    logger.info(
        "Welch t-test: t=%.3f, p=%.4g, significant=%s",
        result["t_statistic"],
        result["p_value"],
        result["significant"],
    )
    return result


def run_chi_square(contingency_table: list[list[int]]) -> dict:
    """Test independence between categorical group and binary outcome.

    A contingency table contains observed counts for combinations such as
    group and conversion status. Chi-square compares those counts with the
    counts expected if the categories were independent.

    Args:
        contingency_table: Two-dimensional table of non-negative counts.

    Returns:
        A dictionary containing the chi-square statistic, p-value, and verdict.
    """
    table = np.asarray(contingency_table, dtype=int)
    if table.ndim != 2 or np.any(table < 0):
        raise ValueError("The contingency table must contain non-negative counts.")
    chi2_statistic, p_value, _, _ = stats.chi2_contingency(table)
    result = {
        "chi2_statistic": float(chi2_statistic),
        "p_value": float(p_value),
        "significant": bool(p_value < 0.05),
    }
    logger.info(
        "Chi-square test: chi2=%.3f, p=%.4g, significant=%s",
        result["chi2_statistic"],
        p_value,
        result["significant"],
    )
    return result
