"""Project-wide experiment design constants."""

# These constants make the assumptions behind the experiment explicit:
# alpha is the tolerated false-positive rate, power is the desired chance of
# detecting the minimum detectable effect, and the base rate describes current
# performance. Sample size and seed support reproducible planning and demos;
# the output directory keeps generated charts separate from source code.
ALPHA = 0.05
POWER = 0.80
BASE_CONVERSION_RATE = 0.10
MINIMUM_DETECTABLE_EFFECT = 0.02
SAMPLE_SIZE_PER_GROUP = 3000
RANDOM_SEED = 42
PLOT_OUTPUT_DIR = "plots/"
