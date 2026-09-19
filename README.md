# The Coalescence of Thought
## Computational Companion & Experimental-Data Sandbox

This repository contains computational controls, experimental-data discovery, and numerical analysis supporting the research programme developed in:

**Daine W. Ball, _The Coalescence of Thought: A Multiscale Causal Framework for Persistent Self-Influence in Physical Systems_ (revised preprint, September 2026).**

It also accompanies:

**Daine W. Ball, _The Ledger of Thought: Loop Closure, Substrate, and Equal Consideration in a Shared Physical Universe_ (revised essay, September 2026).**

The central scientific question is:

> Can persistent causal influence in a physical system be experimentally distinguished from persistence specifically sustained by identifiable feedback paths?

The primary quantity is loop-specific causal persistence:

\[
\mathcal O_H(P,M,F)=C_H(G)-C_H(G_{\mathrm{cut}}(F)).
\]

A positive value means that the declared return edges contribute to the measured persistent effect under the specified intervention and matched-cut protocol.

**\(\mathcal O_H\) is an architectural/interventional quantity. It is not a consciousness score, intelligence score, or probability of personhood.**

---

## Experimental structure

The revised framework separates four obligations:

```text
DESCRIPTION
observation maps
preparation kernels
response kernels
        ↓
BOUNDARY
selector agreement
interventional compatibility
        ↓
LOOP EFFECT
intact persistence
minus matched feedback cut
        ↓
ENERGY
one control volume
non-overlapping fluxes
first-law residual
```

These questions are deliberately kept separate.

Persistence alone does not establish recurrence. A feed-forward delay line can preserve an earlier signal without containing a causal return path. The matched feedback-cut comparison is therefore essential.

---

## Data provenance policy

This repository uses **public machine-readable experimental datasets whenever they are available and appropriate to the observable being analysed**.

Where the underlying experimental dataset is not publicly available through the queried source, the sandbox instead uses the collaboration's **peer-reviewed published measurement and reported uncertainty**.

Two source classes are used:

### `PUBLIC_DATASET`

The program consumes a public machine-readable experimental dataset.

Where practical, the observable can be calculated from that dataset and compared with the collaboration's published result as a reproducibility or sanity check.

### `PUBLISHED_RESULT`

The program consumes the numerical result and uncertainty reported by the experimental collaboration.

This does **not** mean the collaboration lacked underlying data. It means this repository is not claiming to possess or reproduce those underlying measurements.

> **Published results are never represented as raw-data reproductions, and missing observations are never reconstructed or synthesized.**

Every experimental input records its provenance explicitly.

If a suitable public dataset becomes available later, an experiment can move from `PUBLISHED_RESULT` to `PUBLIC_DATASET` without changing this provenance rule.

---

## Current antimatter inputs

### BASE

**Observable:** antiproton/proton charge-to-mass ratio
**Current source:** `PUBLISHED_RESULT`

Reference: Borchert, Ulmer et al., _Nature_ **601**, 53–57 (2022).

The reported q/m precision may be used for an exploratory mass-sensitivity comparison only under the explicitly declared assumption that charge magnitude is held fixed.

The program does not relabel the published q/m observable as a direct mass measurement.

### ALPHA-2

**Observable:** antihydrogen 1S–2S transition frequency
**Current source:** `PUBLISHED_RESULT`

Reference: ALPHA Collaboration, _Nature_ **557**, 71–75 (2018).

Spectroscopic frequency precision is retained as frequency precision. It is not silently converted into an absolute mass sensitivity.

### ATRAP

**Observable:** antiproton magnetic moment
**Current source:** `PUBLISHED_RESULT`

Reference: DiSciacca et al., _Physical Review Letters_ **110**, 130801 (2013).

Magnetic-moment precision is a different observable class and is therefore excluded from the mass-sensitivity gap calculation.

---

## CERN Open Data discovery

`landauer_analysis2.py` queries the CERN Open Data catalogue for relevant records.

**Discovery and scientific input are intentionally separate.**

A CERN search hit does not automatically become an experimental input. Before a public dataset is used, its experiment, observable, provenance, and analysis path must match the calculation being performed.

During the September 2026 audit, catalogue searches for the target Penning-trap and antimatter terms did not return the desired BASE, ALPHA, or ATRAP measurement datasets.

That statement describes the result of those CERN Open Data catalogue queries. It is **not** a claim that the underlying collaboration data do not exist or cannot be available through another archive or by request.

The discovery code remains live so the catalogue can be re-tested.

---

## Landauer numerical sandbox

The repository retains Landauer calculations as an information-thermodynamic numerical analysis.

For logically irreversible erasure,

\[
E_{\min}=k_B T\ln 2.
\]

The script also reports

\[
m_{\mathrm{eq}}=\frac{E_{\min}}{c^2}
\]

as a **mass-equivalent energy scale**.

This is bookkeeping through mass-energy equivalence. The repository does not interpret this quantity as evidence for an additional physical mass reservoir.

Landauer bounds and feedback thermodynamics constrain apparatus energy accounting; they are not added as independent energy channels.

---

## Analytical controls

The sandbox contains simple controls illustrating why persistence alone is insufficient.

### Feed-forward delay line

A signal can survive into the future while the feedback-specific contrast remains

\[
\mathcal O_H=0.
\]

This is the negative control.

### Recurrent control

When a declared return edge contributes to the later state, the intact response differs from the matched feedback-cut response:

\[
\mathcal O_H>0.
\]

This supplies the positive-control structure.

These controls are analytical demonstrations, **not CERN experimental results**.

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

Earlier exploratory versions of this repository contained speculative dark-matter, dark-energy, and information-mass interpretations. Those calculations remain available in Git history but are **not claims of the revised framework**.

The revised research programme instead asks whether feedback-dependent causal persistence, multiscale compatibility, and complete-apparatus energy closure can be measured independently and falsifiably.

---

## Running the sandbox

Create and activate a Python environment:

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

---

## References

- Borchert, Ulmer et al., _Nature_ **601**, 53–57 (2022). DOI: `10.1038/s41586-021-04203-w`
- ALPHA Collaboration, _Nature_ **557**, 71–75 (2018). DOI: `10.1038/s41586-018-0017-2`
- DiSciacca et al., _Physical Review Letters_ **110**, 130801 (2013). DOI: `10.1103/PhysRevLett.110.130801`
- R. Landauer, “Irreversibility and Heat Generation in the Computing Process,” _IBM Journal of Research and Development_ **5** (1961).

---

## Status

This repository is an evolving computational research companion.

**The revised papers are the source of truth for the scope and interpretation of the framework.** The code is intended to make assumptions, provenance, controls, and failure modes inspectable rather than to extend the papers' claims implicitly.
