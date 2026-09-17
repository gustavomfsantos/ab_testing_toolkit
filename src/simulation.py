"""Reproducible experiment data generation."""

import numpy as np
import pandas as pd

from logger import get_logger

logger = get_logger(__name__)


def generate_experiment_data(
    n_control: int,
    n_treatment: int,
    base_rate: float,
    true_effect: float,
    random_seed: int,
) -> pd.DataFrame:
    """Generate binary outcomes for a controlled experiment.

    Simulation lets us control the ground truth, so we can check whether a
    statistical method finds a known effect instead of learning from one noisy
    historical outcome.

    Args:
        n_control: Number of users assigned to the control group.
        n_treatment: Number of users assigned to the treatment group.
        base_rate: Conversion probability for the control group.
        true_effect: Absolute change in conversion probability for treatment.
        random_seed: Seed for reproducible random assignment and outcomes.

    Returns:
        A DataFrame with user identifiers, assignments, and binary outcomes.
    """
    if n_control <= 0 or n_treatment <= 0:
        raise ValueError("Group sizes must be positive.")
    treatment_rate = base_rate + true_effect
    if not 0 <= base_rate <= 1 or not 0 <= treatment_rate <= 1:
        raise ValueError("Both conversion rates must be between 0 and 1.")

    rng = np.random.default_rng(random_seed)
    control_outcomes = rng.binomial(1, base_rate, n_control)
    treatment_outcomes = rng.binomial(1, treatment_rate, n_treatment)
    data = pd.DataFrame(
        {
            "user_id": np.arange(n_control + n_treatment),
            "group": ["control"] * n_control + ["treatment"] * n_treatment,
            "converted": np.concatenate([control_outcomes, treatment_outcomes]),
        }
    )
    rates = data.groupby("group")["converted"].mean()
    logger.info(
        "Generated experiment data: control_rate=%.4f, treatment_rate=%.4f, "
        "observed_delta=%.4f",
        rates["control"],
        rates["treatment"],
        rates["treatment"] - rates["control"],
    )
    return data


def generate_null_experiment_data(
    n_per_group: int,
    base_rate: float,
    random_seed: int,
) -> pd.DataFrame:
    """Generate an experiment in which treatment has no true effect.

    Args:
        n_per_group: Number of users in each group.
        base_rate: Shared conversion probability under the null hypothesis.
        random_seed: Seed for reproducible outcomes.

    Returns:
        A DataFrame with equal-sized control and treatment groups.
    """
    logger.info(
        "Generating null experiment — no true effect exists. "
        "Used to study false positives."
    )
    return generate_experiment_data(
        n_control=n_per_group,
        n_treatment=n_per_group,
        base_rate=base_rate,
        true_effect=0.0,
        random_seed=random_seed,
    )
