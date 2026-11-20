![banner](banner.jpg)

*Banner art: Gemini.*

# The Coalescence of Thought

## Computational Companion & Experimental-Data Sandbox

**Can persistent causal influence in a physical system be experimentally distinguished from persistence specifically sustained by identifiable feedback paths?**

That is the question this repository exists to make checkable. It is the computational companion to:

**Daine W. Ball, _The Coalescence of Thought: A Protocol for Measuring Feedback-Specific Causal Persistence_ (revised preprint, September 2026, rebuilt 20 November 2026).**

It also accompanies:

**Daine W. Ball, _The Ledger of Thought: Loop Closure, Substrate, and Equal Consideration in a Shared Physical Universe_ (revised essay, September 2026).**

Both papers live on Zenodo, record **22659382**. The programme began with an earlier paper, _The Theory Of A Macro Biological Universe_ (Zenodo record 20057118, May 2026).

The central quantity is loop-specific causal persistence:

\[
\mathcal O_H(P,M,F)=C_H(G)-C_H(G_{\mathrm{cut}}(F)).
\]

A positive value means the declared return edges contribute to the measured persistent effect under the specified intervention and matched-cut protocol.

**\(\mathcal O_H\) is an architectural/interventional quantity. It is not a consciousness score, intelligence score, or probability of personhood.**

---

## What this sandbox actually does

Three things, kept separate on purpose:

1. **Discovers** — queries the CERN Open Data catalogue for Penning-trap and antimatter records.
2. **Computes Landauer scales** — the energy cost of erasing a bit, \(E_{\min} = k_B T \ln 2\), and its mass-equivalent \(E/c^2\), for published antimatter results (BASE / ALPHA / ATRAP).
3. **Runs the controls** — a feed-forward delay line and a recurrent register, so persistence *without* feedback can be told apart from persistence *because of* feedback.

```
DESCRIPTION          observation maps, preparation kernels, response kernels
        ↓
BOUNDARY             selector agreement, interventional compatibility
        ↓
LOOP EFFECT          intact persistence minus matched feedback cut
        ↓
ENERGY               one control volume, non-overlapping fluxes, first-law residual
```

Persistence alone does not establish recurrence. A feed-forward delay line can preserve an earlier signal without containing a causal return path. The matched feedback-cut comparison is therefore essential.

## The headline numbers (November 2026, verified)

| Control | \(\mathcal O_H\) |
|---|---|
| Feed-forward delay line (negative control) | **0** |
| Recurrent register, computed from the paper's Eq. C1 | **0.418** |

The recurrent value is **computed**, not asserted: binary entropy and Jensen–Shannon divergence of a Bernoulli register (q = 0.05, lags τ = 1..6, uniform weights) — lag terms 0.713603, 0.547057, 0.427669, 0.337854, 0.268663, 0.214603; mean 0.418242; cut 0. The delay line is derived from Proposition 1 (deterministic shift, disjoint support → D_JS = 1 bit), also computed: C_H 1/1, O_H 0.

**BASE mass sensitivity: 2.676e-38 kg**, a ratio of 4.189e4 to the 1-bit Landauer scale — a gap of **4.6 orders of magnitude** at the assumed 0.006 K operating temperature. The Landauer scale is linear in T, so the gap falls 1 OOM per 10× in temperature, and the 0.006 K figure is an **assumption**, not a sourced apparatus temperature (see below).

These are analytical controls and published-result comparisons. They are **not** CERN experimental results and **not** measurements of consciousness.

---

## Running the sandbox

One dependency:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install requests
```

Run:

```bash
python3 landauer_analysis2.py
```

The program reports:

1. current CERN Open Data search results;
2. provenance for every configured experimental input;
3. the published observable and uncertainty;
4. Landauer energy and \(E/c^2\) scales;
5. mass-sensitivity comparisons only where the observable permits them;
6. feed-forward and recurrent analytical controls; and
7. explicit interpretation boundaries.

Network failure does not invalidate the published-result calculations. It only prevents the live CERN catalogue discovery step from completing.

Run the tests:

```bash
python3 -m unittest test_landauer_analysis
```

20 tests, all passing. They cover the Eq. C1 computation, the delay-line control, the corrected BASE precision, and the temperature labelling.

---

## Corrections — November 2026 script verification

Two numerical errors in the September 2026 revision were found by running the code and corrected in `landauer_analysis2.py` (2026-11-20; full detail in `script-verification-report-2026-11-20.md`):

1. **BASE precision, 10× transcription error.** The reported 16 ppt was entered as 1.6e-12; 16 ppt = 16e-12 = **1.6e-11**. Corrected mass sensitivity 2.676e-38 kg (was 2.676e-39 kg), ratio to the 1-bit Landauer scale 4.189e4 (was 4.189e3), gaps 4.6 / 5.6 OOM (were 3.6 / 4.6 OOM). The mass sensitivity is now derived from the single configured precision value, so the two can no longer disagree silently.
2. **Analytical controls were bare literals.** The recurrent control asserted C_H intact 1.0 / cut 0.35 / O_H 0.65. It is now **computed** from the paper's App. C Eq. C1 (see the table above). The delay line is derived from Proposition 1, computed, not asserted.
3. **Temperatures are now labelled by basis.** ALPHA 0.5 K is the magnetic-trap depth scale (well depth 0.54 K); ATRAP 4.2 K is the sourced electrode temperature (liquid-helium contact); BASE 0.006 K is an **assumed** operating temperature — no citable source was found for it (published BASE figures point to 6 K surfaces, T_z ≈ 1.92 K). The Landauer scale is linear in T, so the BASE gap falls 1 OOM per 10× in T; the script prints this sensitivity.

---

## Data provenance policy

This repository uses **public machine-readable experimental datasets whenever they are available and appropriate to the observable being analysed**.

Where the underlying experimental dataset is not publicly available through the queried source, the sandbox instead uses the collaboration's **peer-reviewed published measurement and reported uncertainty**.

Two source classes are used:

### `PUBLIC_DATASET`

The program consumes a public machine-readable experimental dataset. Where practical, the observable can be calculated from that dataset and compared with the collaboration's published result as a reproducibility or sanity check.

### `PUBLISHED_RESULT`

The program consumes the numerical result and uncertainty reported by the experimental collaboration. This does **not** mean the collaboration lacked underlying data. It means this repository is not claiming to possess or reproduce those underlying measurements.

> **Published results are never represented as raw-data reproductions, and missing observations are never reconstructed or synthesized.**

Every experimental input records its provenance explicitly. If a suitable public dataset becomes available later, an experiment can move from `PUBLISHED_RESULT` to `PUBLIC_DATASET` without changing this provenance rule.

---

## Current antimatter inputs

### BASE

**Observable:** antiproton/proton charge-to-mass ratio — **Current source:** `PUBLISHED_RESULT`

Reference: Borchert, Ulmer et al., _Nature_ **601**, 53–57 (2022).

The reported q/m precision may be used for an exploratory mass-sensitivity comparison only under the explicitly declared assumption that charge magnitude is held fixed. The program does not relabel the published q/m observable as a direct mass measurement.

**Prospective only (no number used):** BASE demonstrated coherent spectroscopy of a single antiproton spin — the first antimatter qubit — with spin coherence times of about 50 s (Latacz et al., _Nature_ **644**, 64–68 (2025), DOI: `10.1038/s41586-025-09323-1`). This points to at least tenfold improved magnetic-moment tests in future; it changes no value in this sandbox.

### BASE magnetic moment (Smorra et al. 2017)

**Observable:** antiproton magnetic moment — **Current source:** `PUBLISHED_RESULT`

Reference: Smorra et al., _Nature_ **550**, 371–374 (2017). DOI: `10.1038/nature24048`

μ_p̄ = −2.7928473441(42) μ_N, fractional precision 1.5 ppb (68% C.L.). This is the current best antiproton magnetic-moment result. Magnetic moment is a different observable class and is excluded from the mass-sensitivity gap calculation.

### ALPHA-2

**Observable:** antihydrogen 1S–2S transition frequency — **Current source:** `PUBLISHED_RESULT`

Reference: ALPHA Collaboration, _Nature_ **557**, 71–75 (2018).

f_d–d = 2,466,061,103,079.4(5.4) kHz (d–d hyperfine component). Spectroscopic frequency precision is retained as frequency precision. It is not silently converted into an absolute mass sensitivity.

### ALPHA 1S–2S hyperfine components (2025)

**Observable:** 1S–2S transition frequency, c–c and d–d hyperfine components — **Current source:** `PUBLISHED_RESULT`

Reference: ALPHA Collaboration, _Nature Physics_ **21** (2025). DOI: `10.1038/s41567-024-02712-9`

The c–c component was determined with the same precision as the d–d component (~2 ppt); combined with the 1S hyperfine splitting this yields the 2S hyperfine splitting.

### ALPHA ground-state hyperfine splitting (2026)

**Observable:** ground-state hyperfine splitting frequency a_1S/h — **Current source:** `PUBLISHED_RESULT`

Reference: Akbari et al. (ALPHA Collaboration), _Nature_ **653**, 1022–1026 (2026). DOI: `10.1038/s41586-026-10556-x`

a_1S/h = 1,420,404.8 ± 1.1 (stat.) ± 5.6 (sys.) kHz in a 1-T magnetic field — a 4 ppm measurement, two orders of magnitude better than the previous 400 ppm. At this level the measurement is sensitive to the internal structure of the antiproton (~40 ppm).

### ATRAP (historical)

**Observable:** antiproton magnetic moment — **Current source:** `PUBLISHED_RESULT`

Reference: DiSciacca et al., _Physical Review Letters_ **110**, 130801 (2013).

Historical magnetic-moment result, retained for provenance. The current best value is Smorra et al. (BASE, 2017), 1.5 ppb — ~2,900× more precise than ATRAP's 4.4 ppm. Magnetic-moment precision is a different observable class and is therefore excluded from the mass-sensitivity gap calculation.

---

## CERN Open Data discovery

`landauer_analysis2.py` queries the CERN Open Data catalogue for relevant records.

**Discovery and scientific input are intentionally separate.** A CERN search hit does not automatically become an experimental input. Before a public dataset is used, its experiment, observable, provenance, and analysis path must match the calculation being performed.

During the September 2026 audit, catalogue searches for the target Penning-trap and antimatter terms did not return the desired BASE, ALPHA, or ATRAP measurement datasets. That statement describes the result of those CERN Open Data catalogue queries. It is **not** a claim that the underlying collaboration data do not exist or cannot be available through another archive or by request. The discovery code remains live so the catalogue can be re-tested.

---

## Landauer numerical sandbox

The repository retains Landauer calculations as an information-thermodynamic numerical analysis. For logically irreversible erasure,

\[
E_{\min}=k_B T\ln 2.
\]

The script also reports

\[
m_{\mathrm{eq}}=\frac{E_{\min}}{c^2}
\]

as a **mass-equivalent energy scale**. This is bookkeeping through mass-energy equivalence. The repository does not interpret this quantity as evidence for an additional physical mass reservoir. Landauer bounds and feedback thermodynamics constrain apparatus energy accounting; they are not added as independent energy channels.

One distinction the papers are explicit about: Landauer's bound states the energy cost of erasing a bit. That alone does not establish that a particle loses rest mass on erasure — that is a separate conjecture under test, not a consequence of the bound.

---

## Claims and nonclaims

This repository investigates recurrent causal organization within ordinary physical systems.

It does **not** currently claim evidence for:

- a new spacetime current or field;
- a new physical mass contribution;
- a new gravitational coupling;
- an informational explanation of dark matter;
- an informational explanation of dark energy;
- consciousness from Landauer energy; or
- consciousness, moral status, or personhood from a large value of \(\mathcal O_H\).

Earlier exploratory versions of this repository contained speculative dark-matter, dark-energy, and information-mass interpretations. Those calculations remain available in Git history but are **not claims of the revised framework**. The repository's old description advertising a dark-matter claim is superseded and does not describe this work.

The revised research programme instead asks whether feedback-dependent causal persistence, multiscale compatibility, and complete-apparatus energy closure can be measured independently and falsifiably.

---

## References

- Borchert, Ulmer et al., _Nature_ **601**, 53–57 (2022). DOI: `10.1038/s41586-021-04203-w`
- Smorra et al. (BASE), _Nature_ **550**, 371–374 (2017). DOI: `10.1038/nature24048`
- Latacz et al. (BASE), _Nature_ **644**, 64–68 (2025). DOI: `10.1038/s41586-025-09323-1`
- ALPHA Collaboration, _Nature_ **557**, 71–75 (2018). DOI: `10.1038/s41586-018-0017-2`
- ALPHA Collaboration, _Nature Physics_ **21** (2025). DOI: `10.1038/s41567-024-02712-9`
- Akbari et al. (ALPHA Collaboration), _Nature_ **653**, 1022–1026 (2026). DOI: `10.1038/s41586-026-10556-x`
- DiSciacca et al., _Physical Review Letters_ **110**, 130801 (2013). DOI: `10.1103/PhysRevLett.110.130801`
- R. Landauer, “Irreversibility and Heat Generation in the Computing Process,” _IBM Journal of Research and Development_ **5** (1961).
- Proton mass: NIST CODATA 2022, 1.67262192595(52)e-27 kg. <https://physics.nist.gov/cgi-bin/cuu/Value?mp>

---

## Status

This repository is an evolving computational research companion. **The revised papers are the source of truth for the scope and interpretation of the framework.** The code is intended to make assumptions, provenance, controls, and failure modes inspectable rather than to extend the papers' claims implicitly.
