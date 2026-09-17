# 🧪 A/B Testing Toolkit

> A hands-on Python toolkit for understanding, implementing, and stress-testing A/B testing concepts used in product analytics and data science.

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Status](https://img.shields.io/badge/status-educational-orange)

---

## Why I Built This

Most people learn A/B testing by reading about it. I wanted to learn it by breaking it.

This project came from a question I kept asking myself: **"What does a p-value actually mean?"** Not the textbook definition — the real intuition. It turns out the answer is subtle enough that even experienced practitioners get it wrong, and the consequences of misunderstanding it show up in bad product decisions every day.

So I built a toolkit that simulates experiments from scratch, runs statistical tests, and deliberately demonstrates the ways experiments fail — p-hacking, peeking at data too early, multiple comparisons, Simpson's Paradox. Each module is written to be read, not just run.

If you are a PM, a stakeholder, or someone curious about how data scientists make decisions from experiment data — this README is written for you.

---

## What is an A/B Test?

Imagine you work at a company and someone suggests changing the color of the "Buy Now" button from grey to green. You think it might increase purchases, but you are not sure.

An A/B test is the structured way to find out.

You split your users into two groups randomly:
- **Group A (Control):** sees the original grey button
- **Group B (Treatment):** sees the new green button

After enough time, you compare conversion rates between the two groups and ask: **is the difference real, or just random noise?**

That question — "is this real or noise?" — is what all the statistics is trying to answer.

---

## The P-Value: The Most Misunderstood Number in Data Science

Before running any experiment, you set up two competing claims:

- **H₀ (Null Hypothesis):** The button color makes no difference. Any gap we observe is random.
- **H₁ (Alternative Hypothesis):** The green button genuinely performs differently.

After collecting data, you get a **p-value**. Here is where most people go wrong.

### What the p-value IS:

> The probability of seeing a result as extreme as yours **assuming the null hypothesis is true** — assuming there is no real effect.

A p-value of 0.03 means: *"If the button color truly made no difference, there would only be a 3% chance of observing this gap by random luck."* That is suspicious enough to doubt the null hypothesis.

### What the p-value IS NOT:

| Common Misconception | Reality |
|---|---|
| "There is a 3% chance our result is due to chance" | ❌ Wrong framing — the p-value assumes chance already |
| "There is a 97% chance the green button is better" | ❌ The p-value says nothing about probability of H₁ |
| "p < 0.05 means the effect is large or important" | ❌ Statistical significance ≠ business significance |
| "p > 0.05 means there is no effect" | ❌ It means you don't have enough evidence — not the same thing |

The p-value is only one piece of information. It tells you how surprised you should be under the null. Nothing more.

---

## Alpha (α), Beta (β), and the Two Ways You Can Be Wrong

Every experiment has two possible mistakes you can make. Understanding them is essential because **they trade off against each other** — reducing one increases the other.

### The 2×2 Reality of Every Experiment

|  | Button truly makes NO difference | Button truly DOES make a difference |
|---|---|---|
| **You conclude: "It works, ship it"** | ❌ **Type I Error** — False Positive | ✅ Correct decision |
| **You conclude: "No effect, don't ship"** | ✅ Correct decision | ❌ **Type II Error** — False Negative |

---

### Alpha (α) — Your tolerance for False Positives

**α is the maximum probability of a Type I Error you are willing to accept.**

In plain English: how often are you okay with *thinking something works when it actually doesn't?*

The industry standard is **α = 0.05**, meaning you accept a 5% chance of being fooled by randomness into shipping something that does nothing.

> 💡 **Intuition:** If you run 100 experiments where the treatment has zero real effect, with α = 0.05, you will incorrectly declare 5 of them "significant" purely by chance. Those are 5 bad features that get shipped.

Lowering α (e.g. to 0.01) makes you more conservative — you demand stronger evidence before concluding something works. But it also means you will miss more real effects (more Type II Errors).

---

### Beta (β) — Your tolerance for False Negatives

**β is the probability of a Type II Error — missing a real effect.**

In plain English: how often are you okay with *failing to detect something that actually works?*

The industry standard is **β = 0.20**, meaning you accept a 20% chance of missing a real improvement.

> 💡 **Intuition:** If the green button genuinely increases conversions, with β = 0.20, you will fail to detect it 20% of the time and incorrectly conclude "no effect — don't ship." That is a real improvement left on the table.

---

### Power (1 − β) — The Probability of Catching Real Effects

**Power is simply 1 minus beta.** With β = 0.20, power = 0.80.

> Power = the probability your test will detect a real effect **when one truly exists.**

Targeting 80% power means: if there is a genuine improvement out there, you have an 80% chance of finding it.

---

### The Tension Between α and β

Here is the core tradeoff, visualized as a dial:

```
Strict (conservative)                    Lenient (liberal)
α = 0.01 ←————————————————————————→ α = 0.10
More false negatives                 More false positives
Miss real effects                    Ship things that don't work
```

The only way to reduce **both** errors simultaneously is to collect **more data**. That is exactly what sample size calculation does — it finds the N where you hit your targets for both α and β simultaneously.

---

## Power & Sample Size: Deciding N Before You Start

One of the most common mistakes in practice: **running an experiment and then calculating whether you had enough data.** That is backwards.

Sample size must be determined *before* the experiment launches, based on:

1. **α** — your significance threshold (usually 0.05)
2. **Desired Power (1−β)** — usually 0.80
3. **Minimum Detectable Effect (MDE)** — the smallest improvement that would be worth shipping

The MDE is a business decision, not a statistical one. You ask: *"What is the smallest conversion lift that would justify the engineering cost of shipping this?"* If the answer is 2 percentage points, that is your MDE.

The math then tells you: **to detect a 2pp lift with 80% power at α = 0.05, you need ~3,800 users per group.**

This module generates plots showing how required N grows as MDE shrinks — detecting smaller effects requires exponentially more data.

---

## The Peeking Problem: How Good Intentions Break Experiments

Imagine you launch a test and check results every day. On day 5, p = 0.04. Exciting — you call it significant and stop the test.

The problem: **every time you check and apply the 0.05 threshold, you are effectively running a new test.** With enough peeks, you will cross 0.05 eventually, even if the treatment does nothing.

The `pitfalls.py` module simulates this directly. With a null experiment (zero true effect) and daily peeking over 20 days:

- No peeking → False Positive Rate ≈ 5% ✅
- Peek at day 5 → FPR inflates to ~14% ⚠️
- Peek at day 1, 3, 5, 10, 20 → FPR inflates to ~25%+ ❌

This is called **p-hacking** — not necessarily intentional, but the statistical damage is the same.

**The fix:** pre-register your sample size and stop date before launching. Do not look at results until you have hit N.

---

## Multiple Comparisons and Simpson's Paradox

### Multiple Comparisons

If you test 20 metrics in one experiment at α = 0.05, you expect **1 false positive by pure chance**, even if none of the metrics were truly affected.

This module demonstrates the correction methods:
- **Bonferroni:** divide α by number of tests — very conservative
- **Benjamini-Hochberg (FDR):** controls the false discovery rate — more practical

### Simpson's Paradox

One of the most counterintuitive results in statistics: a treatment can look **better in aggregate but worse in every single segment**, due to imbalanced group sizes.

The `pitfalls.py` module generates a dataset that shows this paradox clearly — a reminder that always checking subgroup results before concluding anything.

---

## Project Structure

```
ab_testing_toolkit/
├── main.py              # Runs the full pipeline end to end
├── config.py            # All experiment parameters as named constants
├── logger.py            # Centralized logging setup
├── src/
│   ├── simulation.py    # Generate synthetic experiment data
│   ├── stats.py         # Z-test, t-test, chi-square with explanatory comments
│   ├── power.py         # Sample size calculator and power curve plots
│   ├── pitfalls.py      # P-hacking, multiple comparisons, Simpson's Paradox
│   └── reporting.py     # Stakeholder-friendly plain-English summaries
├── notebooks/
│   └── exploration.ipynb  # Interactive walkthrough, one cell per concept
└── plots/               # Generated charts saved here
```

---

## How to Run

```bash
# Clone the repo
git clone https://github.com/gustavomfsantos/ab_testing_toolkit.git
cd ab_testing_toolkit

# Install dependencies
pip install -r requirements.txt

# Run the full pipeline
python main.py

# Or explore interactively
jupyter notebook notebooks/exploration.ipynb
```

---

## Example Log Output

```
[2026-09-17 10:00:01] [INFO] [main] — ════════════ SECTION 1: DATA SIMULATION ════════════
[2026-09-17 10:00:01] [INFO] [simulation] — Generated 3000 control users. Observed conversion: 10.2%
[2026-09-17 10:00:01] [INFO] [simulation] — Generated 3000 treatment users. Observed conversion: 12.1%
[2026-09-17 10:00:02] [INFO] [stats] — Running two-proportion z-test...
[2026-09-17 10:00:02] [INFO] [stats] — z=2.84 | p=0.0045 | Significant: True ✓
[2026-09-17 10:00:02] [INFO] [pitfalls] — Peeking simulation: FPR at peek 1 = 14.3% (nominal: 5.0%) ⚠️
[2026-09-17 10:00:03] [INFO] [main] — All plots saved to plots/
```

---

## Key Takeaways

- **A p-value is not the probability your result is due to chance** — it is the probability of your data given that there is no effect. The difference matters enormously in practice.
- **Sample size must be calculated before the experiment** — not adjusted after seeing early results. Pre-registration is not bureaucracy, it is statistical integrity.
- **Peeking at results inflates your false positive rate** — a test that should have a 5% error rate can silently become a 25% error rate through repeated checking.
- **Statistical significance is not business significance** — a 0.1% lift can be significant with enough users, but may not be worth shipping.
- **Aggregate results can hide the truth** — always inspect subgroups before drawing conclusions. Simpson's Paradox is not exotic; it shows up regularly in real product data.

---

## Tech Stack

`Python 3.10+` · `NumPy` · `Pandas` · `SciPy` · `Statsmodels` · `Matplotlib` · `Seaborn`

---

## Author

Built by [Gustavo Santos](https://github.com/gustavomfsantos) as an independent study project to deeply understand experiment design in product analytics.