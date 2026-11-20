# Script Verification Report — Landauer Analysis (Phase A)

**Date:** 2026-11-20
**Repo:** https://github.com/daineball/cern-landauer-analysis — HEAD `bc73e91` (2026-09-19)
**Scope:** `landauer_analysis2.py`, `test_landauer_analysis.py`, `README.md`
**Status:** Fixed, run, and tested. **Nothing was pushed to GitHub. Nothing was
updated on Zenodo.** All fixed files are local proposals in this directory.

## What was verified (by running code, not by trusting the assessment)

Each known defect was re-checked independently before fixing:

| # | Defect as briefed | Verification result |
|---|---|---|
| 1 | `analytical_controls()` hardcodes literals (1.0/1.0, 1.0/0.35 → O_H 0.65); no Jensen–Shannon, binary entropy, or Bernoulli register in the script | **Confirmed.** `grep` for Jensen / entropy / Bernoulli / 0.713603 / 0.418 across script + tests: zero hits. Old values reproduced by running the original: O_H 0.650, delay 0. |
| 2 | BASE `fractional_precision` entered as 1.6e-12; 16 ppt = 1.6e-11 (10× error) | **Confirmed.** Literal `1.6e-12` in the script (2 places: precision + mass sensitivity, i.e. two independent literals that could disagree silently) and in the tests (3 places). Old run: sensitivity 2.676e-39 kg, ratio 4.189e3, gaps 3.6 / 4.6 OOM. |
| 3 | Tests are circular — they re-assert the same literals and pass 6/6 while encoding both errors | **Confirmed.** Original suite run in a clean venv: **6/6 pass** on the wrong values. `test_analytical_control_invariants` asserts `1.0 − 1.0 = 0` and `1.0 − 0.35 = 0.65` from literals written in the test itself; it never touches the module's control code (which returns nothing). |
| — | M_P literal 1.67262192595e-27 kg | **Verified digit-for-digit** against NIST CODATA 2022: 1.672 621 925 95(52) × 10⁻²⁷ kg (https://physics.nist.gov/cgi-bin/cuu/Value?mp). Correct; unchanged. |
| — | CERN Open Data query returns 0 hits for all six terms — structural null, not a bug | **Confirmed live.** Fresh run 2026-11-20: 0 hits on all six terms, identical wording to `cern-run-final.txt`. Query code untouched. |
| — | `cern-run-2026-09-19.txt` | Not a run at all — one line: `python3: can't open file '/home/clexious/landauer_analysis2.py': [Errno 2] No such file or directory`. The saved run of record is `cern-run-final.txt` (2026-09-19 05:51). |

## How Eq. C1 was checked independently

Before touching the script, the paper's Eq. C1 values were recomputed from
scratch in a one-off calculation (binary entropy, p_τ = (1+0.9^τ)/2):

| τ | p_τ | h₂(p_τ) | D_JS(τ) = 1 − h₂ | Paper's value |
|---|---|---|---|---|
| 1 | 0.950000 | 0.286397 | 0.713603 | 0.713603 |
| 2 | 0.905000 | 0.452943 | 0.547057 | 0.547057 |
| 3 | 0.864500 | 0.572331 | 0.427669 | 0.427669 |
| 4 | 0.828050 | 0.662146 | 0.337854 | 0.337854 |
| 5 | 0.795245 | 0.731337 | 0.268663 | 0.268663 |
| 6 | 0.765721 | 0.785397 | 0.214603 | 0.214603 |

Mean = **0.418242** (0.4182415197…). All six terms match the paper to 6
decimal places. The identity D_JS(Bern(p) ‖ Bern(1−p)) = 1 − h₂(p) holds
because the mixture is Bern(1/2) (entropy 1 bit) and h₂(1−p) = h₂(p); the
script computes the divergence from the general definition and the test
suite checks the identity, so no lag term is ever a literal.

## What was fixed

### Fix 1 — Eq. C1 computed for real (`analytical_controls()`)

- New `binary_entropy(p)` and `jensen_shannon_divergence(p, q)` (general
  definition: mixture entropy minus mean entropy, in bits).
- New `register_lag_terms(q=0.05, decay=0.9, lags=1..6)`: each term is the
  computed JS divergence between Bernoulli(p_τ) and Bernoulli(1−p_τ).
- New `recurrent_control()`: C_H intact = uniform-weight mean of the six
  terms; C_H cut = aggregate over the (empty) surviving set = **0 exactly**;
  O_H = intact − cut.
- New `delay_line_control()`: Proposition 1 as a computation — a
  deterministic shift gives conditional output distributions that are the
  point masses δ₀ and δ₁; disjoint support → their JS divergence is
  computed as exactly 1 bit by the same function. No return edge exists,
  so cut = intact and O_H = 0. The only "1.0" in the code is the
  deterministic channel's own probability (P(output=1|input=1) = 1), which
  is the definition of deterministic, documented in the comment.
- `analytical_controls()` now prints the six lag terms and **returns** the
  computed controls (the old version returned nothing, which is part of
  why the old tests could be circular).

### Fix 2 — BASE 16 ppt chain (single source of truth)

- `fractional_precision`: 1.6e-12 → **1.6e-11** (16 ppt = 16e-12).
- `mass_sensitivity_kg` is no longer a second literal: it is computed once,
  after the `EXPERIMENTS` dict, as `M_P * EXPERIMENTS["BASE (CERN AD)"]["fractional_precision"]`.
  The downstream chain (ratio, gaps) already computed from it, so the whole
  chain now follows from the one corrected value.

### Fix 3 — Tests rewritten to check against independent values

- 20 tests (was 6). Expected Eq. C1 lag terms and the BASE numbers are
  written out in the test file from the paper / publications, not copied
  from the module. The suite also asserts the old wrong values do **not**
  reappear (`assertFalse(isclose(..., 2.676195e-39))`,
  `assertFalse(isclose(o_h, 0.65))`, `assertNotEqual(precision, 1.6e-12)`).

### Fix 4 — Data shortlist

| Item | Done | Verification |
|---|---|---|
| (a) BASE 2017 Smorra magnetic-moment row | New row `BASE magnetic moment (Smorra 2017)`: μ_p̄ = −2.7928473441(42) μ_N, 1.5 ppb, Nature 550, 371–374 (2017), DOI 10.1038/nature24048. ATRAP relabelled `ATRAP (historical)`, note states it is superseded. | Smorra citation + 1.5 ppb confirmed via Nature (search 2026-11-20). The μ value itself is as supplied in the brief; it was **not** re-verified digit-for-digit against the Nature full text — see open flags. Its fractional precision (1.5e-9) is consistent with 1.5 ppb. |
| (b) ALPHA numeric value | `ALPHA-2` result now reads `f_d–d = 2,466,061,103,079.4(5.4) kHz`. | Value as supplied in the brief. Fractional precision 2.0e-12 retained (5.4 kHz / 2.466e12 kHz ≈ 2.2e-12; paper's own figure is "two parts per trillion"). |
| (c) ALPHA 2025 hyperfine-components row | New row, Nature Physics 21 (2025), DOI 10.1038/s41567-024-02712-9, ~2 ppt. | DOI + paper confirmed via Nature (search 2026-11-20). |
| (d) ALPHA 2026 4-ppm hyperfine row | New row: a_1S/h = 1,420,404.8 ± 1.1 (stat.) ± 5.6 (sys.) kHz, 4 ppm, Nature 653, 1022–1026 (2026), DOI 10.1038/s41586-026-10556-x. | Confirmed via Nature abstract (search 2026-11-20). **Flag:** the brief's shorthand "1,420,404.8(6) kHz" does not match the paper's uncertainties (±1.1 stat., ±5.6 sys.; combined ≈ ±5.7 kHz). The script records the paper's own split uncertainties instead — see open flags. |
| (e) BASE 2025 spin qubit | Prospective footnote only on the BASE row (`prospective_note`, printed in the provenance report): Latacz et al., Nature 644, 64–68 (2025), DOI 10.1038/s41586-025-09323-1, ~50 s coherence. No number plugged in. | Confirmed via Nature / Hannover / GSI (search 2026-11-20). |
| (f) Apparatus temperatures | Every experiment now carries a `temperature_basis` field (ASSUMED or SOURCED), printed in the provenance report, plus a sensitivity note in the output. | **ATRAP 4.2 K — SOURCED:** CERN Courier: "Thermal contact with liquid helium keeps the electrodes at 4.2 K." **ALPHA 0.5 K — ASSUMED, trap-depth scale:** ALPHA trap well depth 0.54 K (ALPHA Collab., Nature Physics 7, 558–564 (2011)); CERN ALPHA pages: trap "about 0.5 Kelvin" deep. The trapped-atom distribution itself is ~200 mK truncated at that depth, so 0.5 K is an upper-scale choice, not a measured temperature. **BASE 0.006 K — ASSUMED, no citable source found** (searched 2026-11-20): published BASE figures point elsewhere — 6 K trap surfaces, axial temperature T_z ≈ 1.92 K (Borchert et al. 2019), T = −270 °C (~3 K) in collaboration slides. Sensitivity: Landauer scale is linear in T, so the BASE 1-bit gap would be ~2.1 OOM at 1.92 K and ~1.6 OOM at 6 K, not 4.6 OOM. |

### Fix 5 — README updated

- New "Corrections — November 2026 script verification" section at the top
  (both numerical corrections + temperature labelling).
- Data table updated: Smorra row, ALPHA f_d–d value, ALPHA 2025 + 2026
  rows, ATRAP (historical), BASE 2025 prospective footnote.
- Analytical-controls section now states the Eq. C1 derivation and the
  computed O_H = 0.418; references extended with the four new DOIs plus
  the NIST CODATA 2022 proton-mass source.

## Test results

Run in a venv with `pip install requests` only (`python3 -m venv`,
Python 3). Command: `python3 test_landauer_analysis.py`.

| Suite | Result |
|---|---|
| **New tests vs fixed script** | **20 tests, OK** (0.002 s) |
| **New tests vs OLD script (bc73e91)** | **FAILED — 10 failures, 9 errors, 1 pass.** The 9 errors are `AttributeError`s: the old module has no `binary_entropy`, `jensen_shannon_divergence`, `register_lag_terms`, `recurrent_control`, or `delay_line_control`, and no Smorra / ALPHA-2025 / ALPHA-2026 rows. The 10 failures are the BASE chain, the filled-in ALPHA value, the ATRAP historical label, the qubit footnote, and the temperature-basis checks. The single pass is `test_configured_landauer_scales` (Landauer E/c² scales, which never depended on either error). This is the required behaviour: the suite fails on the old wrong values and passes on the fixed ones. |
| Old tests (bc73e91) vs fixed script | 6/6 pass — expected, and itself diagnostic: the old tests never read the module's numbers (they recompute `M_P * 1.6e-12` inside the test), which is exactly why they were circular. |

## Diff against the saved run (`cern-run-final.txt`, 2026-09-19 05:51)

`diff` (ignoring only the `Run:` timestamp line), 154 diff lines, summarised:

- **Unchanged:** CERN Open Data discovery section — byte-identical, 0 hits on
  all six terms, same wording. Landauer E/bit and E/c² per bit for all three
  temperatures (5.742e-26 J / 6.389e-43 kg at 0.006 K; 4.785e-24 J /
  5.324e-41 kg at 0.5 K; 4.019e-23 J / 4.472e-40 kg at 4.2 K) — these never
  depended on either error. Interpretation Boundary section — unchanged.
  Delay-line numbers (1.000 / 1.000 / 0.000) — same values, now derived.
- **Changed — BASE chain:** precision 1.600e-12 → 1.600e-11; mass
  sensitivity 2.676e-39 → 2.676e-38 kg; ratio 4.189e+03 → 4.189e+04;
  1-bit gap 3.6 → 4.6 OOM; 0.1× ratio 4.189e+04 → 4.189e+05; 0.1× gap
  4.6 → 5.6 OOM.
- **Changed — controls:** "Recurrent toy control / 1.000 / 0.350 / 0.650
  [illustrative]" replaced by the six computed lag terms, C_H intact 0.418
  [mean of lag terms], C_H cut 0.000, O_H 0.418.
- **Added:** three new provenance rows (Smorra 2017, ALPHA 2025, ALPHA
  2026), ALPHA f_d–d numeric value, BASE prospective qubit footnote,
  per-experiment temperature basis lines, temperature-sensitivity note,
  six new reference DOIs + CODATA proton-mass source.
- **Changed — labels only:** "ATRAP" → "ATRAP (historical)"; revision
  header line; table widened for the longer row names.
- Nothing else in the output changed. No number was invented; every new
  number is a published value with a DOI or a computation from Eq. C1.

---

## RESULTS — corrected numbers, side by side with the old wrong values

Every value that changed, in one place. "Old" is the September 2026 run
(`cern-run-final.txt` / script at bc73e91); "New" is the fixed run
(`cern-run-fixed-2026-11-20.txt`, this directory).

### Analytical controls (Eq. C1 / Proposition 1)

| Quantity | Old (asserted literals) | New (computed) | Change |
|---|---|---|---|
| D_JS(τ=1) | — not present | 0.713603 | new, from Eq. C1 |
| D_JS(τ=2) | — not present | 0.547057 | new, from Eq. C1 |
| D_JS(τ=3) | — not present | 0.427669 | new, from Eq. C1 |
| D_JS(τ=4) | — not present | 0.337854 | new, from Eq. C1 |
| D_JS(τ=5) | — not present | 0.268663 | new, from Eq. C1 |
| D_JS(τ=6) | — not present | 0.214603 | new, from Eq. C1 |
| Recurrent C_H intact | 1.000 (literal) | **0.418** (mean of lag terms, 0.418242) | −0.582 |
| Recurrent C_H cut | 0.350 (literal) | **0.000** (no lag term survives the cut) | −0.350 |
| Recurrent **O_H** | **0.650** (literal) | **0.418** | **−0.232 (−36%)** |
| Delay-line C_H intact | 1.000 (literal) | 1.000 (computed, Prop. 1) | same value, now derived |
| Delay-line C_H cut | 1.000 (literal) | 1.000 (computed, Prop. 1) | same value, now derived |
| Delay-line O_H | 0.000 | 0.000 | unchanged |

### BASE chain (16 ppt correction)

| Quantity | Old (wrong) | New (corrected) | Change |
|---|---|---|---|
| BASE fractional precision | 1.6e-12 | **1.6e-11** | ×10 |
| BASE mass sensitivity | 2.676e-39 kg | **2.676e-38 kg** | ×10 |
| Ratio to 1-bit Landauer scale | 4.189e+03× | **4.189e+04×** | ×10 |
| Gap to 1-bit scale | 3.6 OOM | **4.6 OOM** | +1.0 OOM |
| Ratio to 0.1× target | 4.189e+04× | **4.189e+05×** | ×10 |
| Gap to 0.1× target | 4.6 OOM | **5.6 OOM** | +1.0 OOM |
| 1-bit Landauer scale (0.006 K) | 6.389e-43 kg/bit | 6.389e-43 kg/bit | unchanged |
| Landauer E/bit (0.006 K) | 5.742e-26 J | 5.742e-26 J | unchanged |

### Other values

| Quantity | Old | New | Change |
|---|---|---|---|
| Proton mass M_P | 1.67262192595e-27 kg | 1.67262192595e-27 kg | unchanged — verified vs NIST CODATA 2022 |
| ALPHA-2 result | "see cited paper" (no number) | f_d–d = 2,466,061,103,079.4(5.4) kHz | filled in |
| ALPHA-2 fractional precision | 2.0e-12 | 2.0e-12 | unchanged |
| ATRAP magnetic moment | current row, −2.792845 ± 0.000012 (4.4 ppm) | **historical** row, same numbers | label only |
| Antiproton magnetic moment, best | ATRAP 2013, 4.4 ppm (only value shown) | **Smorra 2017, 1.5 ppb**: μ_p̄ = −2.7928473441(42) μ_N | new best value, ~2,900× more precise |
| ALPHA 1S–2S hyperfine components (2025) | absent | new row, ~2 ppt, DOI 10.1038/s41567-024-02712-9 | added |
| ALPHA ground-state hyperfine splitting (2026) | absent | new row, 1,420,404.8 ± 1.1 (stat.) ± 5.6 (sys.) kHz, 4 ppm, DOI 10.1038/s41586-026-10556-x | added |
| BASE 2025 spin qubit (~50 s coherence) | absent | prospective footnote only, no number used | added |
| CERN Open Data hits (6 terms) | 0 / 0 / 0 / 0 / 0 / 0 | 0 / 0 / 0 / 0 / 0 / 0 | unchanged |
| Apparatus temperatures | bare numbers (0.006 / 0.5 / 4.2 K) | labelled: BASE **assumed** (unsourced), ALPHA **assumed** (trap-depth scale), ATRAP **sourced** (4.2 K electrodes) | basis now explicit |
| BASE 1-bit gap if T = 1.92 K (published axial T) | — not stated | ~2.1 OOM | new sensitivity note |
| BASE 1-bit gap if T = 6 K (trap-surface T) | — not stated | ~1.6 OOM | new sensitivity note |

---

## IMPLICATIONS — what the corrected numbers mean for the papers

Specific and grounded. Scope note first: **this verification covered the
script, not the paper manuscripts.** I did not re-read the Coalescence
manuscript in this pass, so where a paper sentence is affected I name the
exact old number to search for rather than quoting manuscript text I have
not checked. Nothing below invents a paper claim.

### 1. Does the corrected BASE gap change any claim the paper or script makes?

**No claim in the script changes, because the script makes no claim the gap
could overturn.** The script's only conclusion about the BASE comparison is
a sensitivity comparison plus an explicit non-claim: "This is a numerical
sensitivity comparison, not a prediction that an additional mass deficit
exists or would be measured." That sentence is true under both the old and
the new numbers, and it is unchanged in the fixed output.

What changes is the **distance, and in which direction**: the experiment is
now **10× further** from the 1-bit Landauer mass-equivalent scale than the
old numbers said (41,889× above it, not 4,189×). So any reading of "how
close are we to Landauer-scale sensitivity" gets **weaker by exactly one
order of magnitude** — the gap grew from 3.6 to 4.6 OOM (1-bit) and from
4.6 to 5.6 OOM (0.1× target). If the paper or any accompanying text quotes
"3.6 orders of magnitude", "4,189×", "2.676e-39 kg", or "4.6 OOM" for the
0.1× target, those four strings must be reworded to **4.6 OOM, 41,889×,
2.676e-38 kg, and 5.6 OOM** respectively. Search the manuscript for those
four old strings; each occurrence is a concrete rewording job, not a
judgement call.

The one genuine weakening is not the 10× itself but the **temperature
labelling**: the 4.6 OOM figure is now explicitly conditional on the assumed
0.006 K operating temperature, for which no citable source was found. Under
published BASE temperatures the gap is smaller — ~2.1 OOM at the published
axial temperature 1.92 K, ~1.6 OOM at the 6 K trap-surface temperature. So
a paper sentence presenting the BASE gap as a firm single number now needs
the conditional attached ("4.6 OOM at the assumed 0.006 K operating
temperature; ~2.1 OOM at the published 1.92 K axial temperature"). The
qualitative conclusion survives all plausible temperatures — even at 6 K
the sensitivity is still ~42× above the 1-bit scale — but the honest
statement is now a conditional range, not a point value. That is a
strengthening of the paper's honesty and a weakening of the number's
standing, both at once.

### 2. Does the computed O_H = 0.418 (instead of the asserted 0.65) change anything in how the controls read?

**The qualitative reading does not change; the magnitude and the evidential
status do.**

- **Unchanged:** the controls still read exactly as before in structure —
  negative control O_H = 0 (persistence without feedback), positive control
  O_H > 0 (recurrence identified by the cut contrast). The argument that
  persistence alone cannot identify recurrence, and that the matched
  feedback cut is what does the work, depends on O_H being zero in one case
  and positive in the other. It does not depend on the positive value being
  0.65 or 0.418 or any other particular size. No sentence stating that
  structure needs rewording.
- **Changed — magnitude:** the positive control is ~36% smaller than the
  asserted value (0.418 vs 0.65). Any paper sentence quoting 0.65, or
  describing the recurrent contribution as "65% of the normalized intact
  value", must be reworded to **0.418** (mean lag-term value 0.418242,
  cut 0). Search the manuscript for "0.65" in the controls context.
- **Changed — evidential status, and this is the real improvement:** the
  old 0.65 was arbitrary. It could have been 0.5 or 0.8 with equal
  justification, so it carried no information and could not disagree with
  the paper — the code and the paper were disconnected, and the code could
  not have caught a paper error (or vice versa). The new 0.418 is derived
  from the paper's own Eq. C1, so the code and the paper now check each
  other: if the paper's lag terms change, the code's output changes, and
  the test suite fails. The control is **stronger as a consistency check**
  precisely because it can now fail.
- **Changed — visible structure the old literals hid:** the six lag terms
  (0.714 → 0.215) show the register's persistence decaying with lag. That
  decay is part of what Eq. C1 says, and it was invisible when the control
  was two literals. If the paper discusses the lag structure anywhere, the
  code now exhibits it; if it does not, nothing needs adding — but the
  option is now open.

### 3. Does anything get stronger, weaker, or need rewording?

**Stronger:**

- **Script–paper consistency.** The controls now instantiate the paper's
  equations instead of asserting unrelated numbers. A reader can verify
  the paper's App. C by running the script, which was impossible before.
- **The magnetic-moment record.** The sandbox previously showed only the
  2013 ATRAP value (4.4 ppm) for the antiproton magnetic moment. It now
  shows the current best, Smorra 2017 at 1.5 ppb — ~2,900× more precise.
  Any paper text citing ATRAP as the state of the art for the magnetic
  moment is now out of date and should cite Smorra 2017 instead.
- **The ALPHA record.** Two newer results (2025 hyperfine components,
  2026 4-ppm ground-state splitting — a 100× improvement over the 2017
  400 ppm) are now in the table. They change no computed number, but they
  keep the paper's experimental context current and they strengthen the
  background claim that antimatter spectroscopy is advancing fast, if the
  paper makes it.
- **Temperature honesty.** Labelling the temperatures by basis (and
  printing the sensitivity) removes a silent assumption. The BASE gap is
  now presented with its condition attached, which is strictly more
  defensible.

**Weaker:**

- **The BASE gap as a headline number.** It grew by 1 OOM (further from
  Landauer scale), and it is now conditional on an unsourced assumed
  temperature. Both push the same way: the number is less close and less
  firm than the September version implied. Nothing in the script's
  conclusions depended on the gap being 3.6 rather than 4.6, so this
  weakens a number, not an argument — but if any paper sentence leans on
  the gap being small ("within a few orders of magnitude"), that sentence
  should be re-checked: 4.6 OOM is still "a few", and ~2.1 OOM at 1.92 K
  is closer, so the sentence may survive — but it must now say which
  temperature it assumes.
- **The recurrent control's size.** 0.418 instead of 0.65. Only matters
  where the size itself is quoted; the sign and the structure are intact.

**Needs rewording (concrete search list for the manuscript):**

| Search for (old) | Replace with (new) |
|---|---|
| `3.6 OOM` / `3.6 orders of magnitude` (BASE 1-bit gap) | 4.6 OOM (at assumed 0.006 K) |
| `4.6 OOM` (BASE 0.1× target gap) | 5.6 OOM |
| `4.189e3` / `4,189×` (BASE ratio) | 4.189e4 / 41,889× |
| `2.676e-39` (BASE mass sensitivity) | 2.676e-38 kg |
| `1.6e-12` (BASE precision) | 1.6e-11 (16 ppt) |
| `0.65` (recurrent O_H) | 0.418 |
| `0.35` (recurrent C_H cut) | 0 |
| `1.0` / `1.000` (recurrent C_H intact, if quoted) | 0.418 (mean of lag terms) |
| ATRAP cited as the magnetic-moment state of the art | Smorra et al. 2017, 1.5 ppb |
| Any BASE-gap sentence with no temperature stated | Add the temperature condition (assumed 0.006 K; ~2.1 OOM at 1.92 K) |

**Where the corrected numbers change nothing (saying so plainly):**

- The Landauer scales themselves (E/bit, E/c² per bit at all three
  temperatures) are byte-identical — they never depended on either error.
- The delay-line control reads identically (1 / 1 / 0); only its
  justification changed (derived, not asserted).
- The CERN Open Data result (0 hits, all six terms) is unchanged, and the
  provenance policy, observable policy, and Interpretation Boundary are
  unchanged.
- No claim about dark matter, dark energy, consciousness, or empirical
  confirmation is made by the script, so no such claim is affected. The
  script's scope statements needed no edits.
- The proton mass, the ALPHA 1S–2S precision (2 ppt), and the ATRAP
  numbers themselves are unchanged; only their labels and context changed.
- The BASE 2025 spin-qubit footnote adds context and changes no number.

## Open flags (for Daine / parent — not blockers, but do not silently resolve)

1. **Akbari 2026 uncertainty shorthand.** The brief gave the value as
   "1,420,404.8(6) kHz". The paper itself reports ±1.1 (stat.) ± 5.6
   (sys.) kHz (combined ≈ ±5.7 kHz). "(6)" does not match either
   uncertainty. The script records the paper's own split uncertainties.
   If the paper manuscript uses the "(6)" form, check which uncertainty
   it means before the rebuild cites it.
2. **BASE 0.006 K unsourced.** No citable source was found for 0.006 K
   as the BASE apparatus temperature. If the paper states a source for
   it, that source should be added to the script's `temperature_basis`;
   if there is none, the paper should carry the same conditional the
   script now carries.
3. **Smorra μ value.** μ_p̄ = −2.7928473441(42) μ_N is as supplied in the
   brief; it was confirmed at the citation/precision level (Nature 550,
   371–374, 1.5 ppb) but not re-verified digit-for-digit against the
   Nature full text. Worth one check against the paper before the
   rebuild cites the digits.
4. **Zenodo record not independently located.** A web search for the
   Zenodo title "A Coupled Thought Field Hypothesis for Dark Energy" did
   not return Daine's record, so the Zenodo note in this directory is
   written against the title as briefed, without a record ID or DOI.
   Confirm the record ID/DOI from Daine's Zenodo account before using it.
5. **Paper manuscript not re-checked in this pass.** The implications
   above name exact old strings to search for; the manuscript itself
   still needs that search (Phase A papers work).

## Files delivered (this directory)

- `landauer_analysis2.py` — fixed script (Eq. C1 computed, BASE 1.6e-11,
  data shortlist, temperature bases)
- `test_landauer_analysis.py` — rewritten suite, 20 tests
- `README.md` — updated data table, corrections section, new references
- `cern-run-fixed-2026-11-20.txt` — full fixed run output (also pasted
  below in full)
- `cern-run-final.txt` — copy of the saved September run, for diffing
- `script-verification-report-2026-11-20.md` — this report
- `proposed-repo-description.md` — replacement GitHub repo description
  (DO NOT push; text only)
- `proposed-zenodo-note.md` — version-note text correcting the Zenodo
  record title (DO NOT update Zenodo; text only)
- `repo/` — pristine local clone of daineball/cern-landauer-analysis at
  bc73e91, unmodified (verified `git status` clean). Nothing was pushed.

---

## FULL OUTPUT — fixed script run, complete text

Run command (venv, `pip install requests` only):

```bash
python3 landauer_analysis2.py > cern-run-fixed-2026-11-20.txt
```

Run timestamp in the output below: **2026-11-20 08:51**. The complete
output follows verbatim (also saved as `cern-run-fixed-2026-11-20.txt`):

```text
==============================================================================
  CERN / Published-Result Landauer Analysis Sandbox
  Run: 2026-11-20 08:51
  Revision: November 2026 — Eq. C1 controls computed; BASE 16 ppt
  corrected to 1.6e-11; temperatures labelled by basis
==============================================================================

── CERN Open Data Discovery ─────────────────────────────────────
  penning trap                         0 returned hit(s)
  BASE antiproton                      0 returned hit(s)
  ALPHA antihydrogen                   0 returned hit(s)
  proton antiproton mass ratio         0 returned hit(s)
  ATRAP                                0 returned hit(s)
  antiproton magnetic moment           0 returned hit(s)

  No records were returned for the target search terms.
  This establishes only the result of the current catalogue
  queries; it does NOT establish that underlying data do not
  exist elsewhere.

  Published collaboration results will therefore be used for
  target experiments configured as PUBLISHED_RESULT.

── Experimental Input Provenance ────────────────────────────────

  BASE (CERN AD)
    Source type : PUBLISHED_RESULT
    Observable  : antiproton/proton charge-to-mass ratio
    Result      : -(q/m)_p / (q/m)_pbar = 1.000000000003(16)
    Precision   : 1.600e-11 fractional
    Temperature : 0.006 K
    Temp. basis : ASSUMED operating temperature. No citable source was found for 0.006 K as the BASE apparatus temperature (searched 2026-11-20); published figures point to 6 K trap surfaces and Tz ~ 1.92 K. Landauer scale is linear in T — see TEMPERATURE_NOTE.
    Reference   : Borchert, Ulmer et al., Nature 601, 53-57 (2022)
    DOI         : https://doi.org/10.1038/s41586-021-04203-w
    Prospective : PROSPECTIVE ONLY (no number plugged in): BASE demonstrated coherent spectroscopy of a single antiproton spin — the first antimatter qubit — with spin coherence times of about 50 s (Latacz et al., Nature 644, 64-68 (2025), DOI 10.1038/s41586-025-09323-1). This points to at least tenfold improved magnetic-moment tests in future; it changes no value in this sandbox.
    Mass gap    : eligible under declared assumption
    Assumption  : For this exploratory comparison only, fractional q/m precision is treated as fractional mass sensitivity with charge magnitude held fixed. The reported BASE observable itself is q/m.

  BASE magnetic moment (Smorra 2017)
    Source type : PUBLISHED_RESULT
    Observable  : antiproton magnetic moment
    Result      : mu_pbar = -2.7928473441(42) mu_N
    Precision   : 1.500e-09 fractional
    Temperature : 0.006 K
    Temp. basis : ASSUMED operating temperature — same BASE assumption as the q/m row above; see TEMPERATURE_NOTE.
    Reference   : Smorra et al. (BASE), Nature 550, 371-374 (2017)
    DOI         : https://doi.org/10.1038/nature24048
    Mass gap    : N/A — incompatible observable

  ALPHA-2 (CERN AD)
    Source type : PUBLISHED_RESULT
    Observable  : 1S-2S transition frequency
    Result      : f_d-d = 2,466,061,103,079.4(5.4) kHz (d-d hyperfine component of the 1S-2S transition)
    Precision   : 2.000e-12 fractional
    Temperature : 0.5 K
    Temp. basis : ASSUMED operating temperature, set by the magnetic-trap depth scale: ALPHA trap well depth 0.54 K (ALPHA Collab., Nature Physics 7, 558-564 (2011)); CERN ALPHA pages put the trap depth at 'about 0.5 Kelvin'. The trapped-atom distribution itself is ~200 mK truncated at that depth.
    Reference   : ALPHA Collaboration, Nature 557, 71-75 (2018)
    DOI         : https://doi.org/10.1038/s41586-018-0017-2
    Mass gap    : N/A — incompatible observable

  ALPHA 1S-2S hyperfine components (2025)
    Source type : PUBLISHED_RESULT
    Observable  : 1S-2S transition frequency, c-c and d-d hyperfine components
    Result      : c-c component determined with the same precision as the d-d component (~2 ppt); combined with the 1S hyperfine splitting this yields the 2S hyperfine splitting
    Precision   : 2.000e-12 fractional
    Temperature : 0.5 K
    Temp. basis : ASSUMED operating temperature — same ALPHA trap-depth scale as the 1S-2S row above.
    Reference   : ALPHA Collaboration, Nature Physics 21 (2025)
    DOI         : https://doi.org/10.1038/s41567-024-02712-9
    Mass gap    : N/A — incompatible observable

  ALPHA ground-state hyperfine splitting (2026)
    Source type : PUBLISHED_RESULT
    Observable  : ground-state hyperfine splitting frequency a_1S/h
    Result      : a_1S/h = 1,420,404.8 +/- 1.1 (stat.) +/- 5.6 (sys.) kHz in a 1-T magnetic field (4 ppm)
    Precision   : 4.000e-06 fractional
    Temperature : 0.5 K
    Temp. basis : ASSUMED operating temperature — same ALPHA trap-depth scale as the 1S-2S row above.
    Reference   : Akbari et al. (ALPHA Collaboration), Nature 653, 1022-1026 (2026)
    DOI         : https://doi.org/10.1038/s41586-026-10556-x
    Mass gap    : N/A — incompatible observable

  ATRAP (historical)
    Source type : PUBLISHED_RESULT
    Observable  : antiproton magnetic moment
    Result      : mu_pbar / mu_N = -2.792845 +/- 0.000012
    Precision   : 4.400e-06 fractional
    Temperature : 4.2 K
    Temp. basis : SOURCED electrode temperature: 'Thermal contact with liquid helium keeps the electrodes at 4.2 K' (CERN Courier on DiSciacca et al. 2013).
    Reference   : DiSciacca et al. (ATRAP), Phys. Rev. Lett. 110, 130801 (2013)
    DOI         : https://doi.org/10.1103/PhysRevLett.110.130801
    Mass gap    : N/A — incompatible observable

── Landauer Energy / Mass-Equivalent Scale ─────────────────────
  Experiment                                          Temp      Landauer E/bit        E/c² per bit    Mass sensitivity       Gap
  ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
  BASE (CERN AD)                                   0.0060K           5.742e-26           6.389e-43           2.676e-38   4.6 OOM
  BASE magnetic moment (Smorra 2017)               0.0060K           5.742e-26           6.389e-43                 N/A       N/A
  ALPHA-2 (CERN AD)                                0.5000K           4.785e-24           5.324e-41                 N/A       N/A
  ALPHA 1S-2S hyperfine components (2025)          0.5000K           4.785e-24           5.324e-41                 N/A       N/A
  ALPHA ground-state hyperfine splitting (2026)    0.5000K           4.785e-24           5.324e-41                 N/A       N/A
  ATRAP (historical)                               4.2000K           4.019e-23           4.472e-40                 N/A       N/A

  NOTE: Temperatures are labelled operating-temperature assumptions (see temperature_basis per experiment). The Landauer scale is linear in T: a 10x higher true temperature lowers the BASE 1-bit gap by 1 OOM.

── Exploratory Mass-Sensitivity Comparison ─────────────────────

  BASE (CERN AD)
    Observable          : antiproton/proton charge-to-mass ratio
    Temperature         : 0.006 K
    Landauer E/c² scale : 6.389e-43 kg/bit
    Comparison precision: 2.676e-38 kg
    Ratio to 1-bit scale: 4.189e+04×
    Gap to 1-bit scale  : 4.6 OOM
    0.1× target scale   : 6.389e-44 kg
    Ratio to 0.1× target: 4.189e+05×
    Gap to 0.1× target  : 5.6 OOM
    Assumption          : For this exploratory comparison only, fractional q/m precision is treated as fractional mass sensitivity with charge magnitude held fixed. The reported BASE observable itself is q/m.

  NOTE:
  This is a numerical sensitivity comparison, not a prediction
  that an additional mass deficit exists or would be measured.

  TEMPERATURE SENSITIVITY:
  Temperatures are labelled operating-temperature assumptions (see temperature_basis per experiment). The Landauer scale is linear in T: a 10x higher true temperature lowers the BASE 1-bit gap by 1 OOM.
  For BASE: at T = 1.92 K (published axial temperature) the
  1-bit gap would be ~2.1 OOM; at T = 6 K (trap-surface
  temperature) ~1.6 OOM — not 4.6 OOM. The BASE gap is
  conditional on the assumed 0.006 K operating temperature.

── Analytical Controls: Persistence vs Feedback ────────────────

  Feed-forward delay line (Proposition 1: deterministic shift,
  disjoint support -> D_JS = 1 bit, computed)
    C_H intact : 1.000
    C_H cut    : 1.000
    O_H        : 0.000
    Interpretation: persistence without feedback-specific effect.

  Recurrent register control (App. C, Eq. C1: q = 0.05,
  tau = 1..6, uniform weights)
    D_JS(tau=1) : 0.713603
    D_JS(tau=2) : 0.547057
    D_JS(tau=3) : 0.427669
    D_JS(tau=4) : 0.337854
    D_JS(tau=5) : 0.268663
    D_JS(tau=6) : 0.214603
    C_H intact : 0.418  [mean of lag terms]
    C_H cut    : 0.000  [no lag term survives the cut]
    O_H        : 0.418
    Interpretation: positive effect attributable to declared return edge.
    Values are computed from Eq. C1, not experimental measurements.

  O_H is an architectural/interventional quantity.
  It is not a consciousness score or personhood probability.

── Interpretation Boundary ─────────────────────────────────────

  DATA:
    Public machine-readable datasets are preferred where available.
    Otherwise the peer-reviewed collaboration result and uncertainty are used.

  PROVENANCE:
    PUBLISHED_RESULT never means that raw observations were reproduced.
    Missing observations are not synthesized.

  OBSERVABLES:
    q/m, transition frequency, magnetic moment, and mass are kept distinct.

  LANDAUER:
    k_B T ln(2) is used as an information-thermodynamic lower bound.
    E/c² is reported only as a mass-equivalent energy scale.

  COALESCENCE FRAMEWORK:
    The experimental target is feedback-dependent causal persistence:

        O_H = C_H(G) - C_H(G_cut)

    This is separate from apparatus energy closure.

  NOT CLAIMED:
    No new spacetime current, field, mass contribution, gravitational
    coupling, dark-matter mechanism, dark-energy mechanism, consciousness
    measure, or empirical confirmation is inferred by this program.


── References ──────────────────────────────────────────────────
  CERN Open Data Portal
    https://opendata.cern.ch

  BASE q/m (16 ppt)
    https://doi.org/10.1038/s41586-021-04203-w

  BASE magnetic moment, 1.5 ppb (Smorra et al. 2017)
    https://doi.org/10.1038/nature24048

  BASE coherent single-antiproton spin qubit, ~50 s (Latacz et al. 2025)
    https://doi.org/10.1038/s41586-025-09323-1

  ALPHA 1S-2S (Ahmadi et al. 2018)
    https://doi.org/10.1038/s41586-018-0017-2

  ALPHA 1S-2S hyperfine components (2025)
    https://doi.org/10.1038/s41567-024-02712-9

  ALPHA ground-state hyperfine splitting, 4 ppm (Akbari et al. 2026)
    https://doi.org/10.1038/s41586-026-10556-x

  ATRAP magnetic moment, historical (DiSciacca et al. 2013)
    https://doi.org/10.1103/PhysRevLett.110.130801

  Proton mass: NIST CODATA 2022, 1.67262192595(52)e-27 kg
    https://physics.nist.gov/cgi-bin/cuu/Value?mp

```

— End of full output. (214 lines, run 2026-11-20 08:51. The only line that
will differ on a re-run is the `Run:` timestamp, and the CERN discovery
counts if the catalogue changes.)
