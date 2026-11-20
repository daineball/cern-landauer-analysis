"""
CERN / Published-Result Landauer Analysis Sandbox
==================================================

Computational companion to:

    The Coalescence of Thought
    A Protocol for Measuring Feedback-Specific Causal Persistence

Author: Daine W. Ball
Revision: September 2026

DATA PROVENANCE POLICY
----------------------

This analysis uses public machine-readable experimental datasets where they
are available.

Where the underlying experimental dataset is not publicly released, the
analysis uses the collaboration's published measurement and reported
uncertainty as the experimental input.

Published results are never represented as raw-data reproductions.
Missing observations are never reconstructed or synthesized.

Every experimental input therefore carries an explicit source type:

    PUBLIC_DATASET
        A public machine-readable experimental dataset is available and may
        be queried or processed directly.

    PUBLISHED_RESULT
        The underlying raw measurements are not presently available through
        the queried public-data source. The peer-reviewed collaboration result
        and its reported uncertainty are used instead.

OBSERVABLE POLICY
-----------------

Different physical observables are not silently converted into mass
measurements.

BASE:
    antiproton/proton charge-to-mass ratio.
    Mass-comparable here only under the explicitly declared assumption that
    the charge magnitude is fixed when interpreting fractional q/m precision
    as fractional mass sensitivity.

ALPHA-2:
    antihydrogen 1S-2S transition frequency.
    Not treated as a direct mass measurement.

ATRAP:
    antiproton magnetic moment.
    Not treated as a direct mass measurement.

SCIENTIFIC SCOPE
----------------

Landauer's bound constrains the minimum dissipated energy associated with
logically irreversible information erasure:

    E >= k_B T ln(2)

The quantity E/c^2 can be expressed as a mass-equivalent bookkeeping value.
This sandbox explores numerical scales and experimental sensitivities.

It does NOT establish:
    - a new physical mass contribution,
    - a new gravitational coupling,
    - dark matter or dark energy from information,
    - consciousness from Landauer energy,
    - or empirical confirmation of The Coalescence of Thought.

The revised theoretical framework treats information thermodynamics as a
constraint on apparatus energy accounting, not as an additional energy
reservoir.

Requirements:
    pip install requests

Run:
    python3 landauer_analysis2.py

REVISION NOTE — 2026-11-20 (script verification, Phase A)
----------------------------------------------------------
Two numerical errors in the September 2026 revision were corrected here
(see script-verification-report-2026-11-20.md for the full before/after):

1.  BASE fractional precision was entered as 1.6e-12; the reported 16 ppt
    is 16e-12 = 1.6e-11. The mass-sensitivity chain now derives from the
    single corrected value (2.676e-38 kg, ratio 4.189e4, gaps 4.6/5.6 OOM).
2.  The analytical controls were bare literals (recurrent O_H = 0.65).
    They are now computed from the paper's Eq. C1: binary entropy and the
    Jensen-Shannon divergence of a Bernoulli register, q = 0.05, lags
    tau = 1..6, uniform weights (mean 0.418242; cut 0; O_H = 0.418).
    The delay line is derived from Proposition 1 (deterministic shift,
    disjoint support -> D_JS = 1), computed, not asserted.

No experimental input was invented. Temperatures are labelled with their
basis (sourced or assumed); see TEMPERATURE_NOTE below.
"""

import math
from datetime import datetime

import requests


# ── Physical constants ────────────────────────────────────────────────────────

K_B = 1.380649e-23       # Boltzmann constant [J/K], exact SI
C = 2.99792458e8         # speed of light [m/s], exact SI
LN2 = math.log(2)
# Proton mass [kg]. Verified digit-for-digit against NIST CODATA 2022:
# 1.672 621 925 95(52) x 10-27 kg (https://physics.nist.gov/cgi-bin/cuu/Value?mp).
M_P = 1.67262192595e-27  # proton mass [kg], CODATA 2022


# ── Temperature basis ─────────────────────────────────────────────────────────
#
# The three apparatus temperatures are NOT all on the same footing, and the
# script now says so per experiment (field "temperature_basis").
#
#   BASE  0.006 K — ASSUMED operating temperature. No citable source was
#                   found for 0.006 K as the BASE apparatus temperature
#                   (searched 2026-11-20). Published BASE figures point
#                   elsewhere: trap surfaces cooled to 6 K, axial
#                   temperature Tz ~ 1.92 K (Borchert et al. 2019),
#                   T = -270 degC (~3 K) in collaboration slides.
#                   The Landauer scale is linear in T, so the BASE gap
#                   falls by 1 OOM for every 10x increase in T: at
#                   T = 1.92 K the 1-bit gap would be ~2.1 OOM, not 4.6.
#                   Treat the BASE gap as conditional on this assumption.
#   ALPHA 0.5 K   — ASSUMED operating temperature, set by the magnetic-trap
#                   depth scale: ALPHA trap well depth 0.54 K (ALPHA Collab.,
#                   Nature Physics 7, 558-564 (2011)); CERN ALPHA pages put
#                   the trap depth at "about 0.5 Kelvin". The trapped-atom
#                   distribution itself is ~200 mK truncated at that depth,
#                   so 0.5 K is an upper-scale choice, not a measured T.
#   ATRAP 4.2 K   — SOURCED electrode temperature: "Thermal contact with
#                   liquid helium keeps the electrodes at 4.2 K"
#                   (CERN Courier on DiSciacca et al. 2013).
#
# No Landauer number in this script depends on a temperature being anything
# other than the labelled operating-temperature assumption above.

TEMPERATURE_NOTE = (
    "Temperatures are labelled operating-temperature assumptions (see "
    "temperature_basis per experiment). The Landauer scale is linear in T: "
    "a 10x higher true temperature lowers the BASE 1-bit gap by 1 OOM."
)


# ── Provenance classes ────────────────────────────────────────────────────────

PUBLIC_DATASET = "PUBLIC_DATASET"
PUBLISHED_RESULT = "PUBLISHED_RESULT"


# ── CERN Open Data discovery ─────────────────────────────────────────────────

SEARCH_URL = "https://opendata.cern.ch/api/records/"

SEARCH_TERMS = [
    "penning trap",
    "BASE antiproton",
    "ALPHA antihydrogen",
    "proton antiproton mass ratio",
    "ATRAP",
    "antiproton magnetic moment",
]


# ── Experimental inputs ───────────────────────────────────────────────────────
#
# IMPORTANT:
#
# source_type describes what THIS PROGRAM actually consumes.
#
# A PUBLISHED_RESULT entry means we use the collaboration's reported observable
# and uncertainty. It does not mean that the collaboration lacked underlying
# data; it means this sandbox is not claiming to have reproduced that raw-data
# analysis.
#
# A PUBLIC_DATASET entry should identify the actual machine-readable dataset
# and the code path used to derive the observable from it.
#

EXPERIMENTS = {
    "BASE (CERN AD)": {
        "description":
            "Baryon Antibaryon Symmetry Experiment — Penning trap",

        "observable":
            "antiproton/proton charge-to-mass ratio",

        "source_type": PUBLISHED_RESULT,

        "published_result":
            "-(q/m)_p / (q/m)_pbar = 1.000000000003(16)",

        "temperature_K": 0.006,

        "temperature_basis":
            "ASSUMED operating temperature. No citable source was found "
            "for 0.006 K as the BASE apparatus temperature (searched "
            "2026-11-20); published figures point to 6 K trap surfaces "
            "and Tz ~ 1.92 K. Landauer scale is linear in T — see "
            "TEMPERATURE_NOTE.",

        # 16 parts per trillion reported uncertainty scale.
        # 16 ppt = 16e-12 = 1.6e-11. (Corrected 2026-11-20: an earlier
        # revision entered 1.6e-12, a 10x transcription error.)
        "fractional_precision": 1.6e-11,

        # Exploratory mass-equivalent sensitivity. This is NOT an independent
        # direct mass measurement. Derived from fractional_precision below
        # (single source of truth); never a second literal.
        "mass_sensitivity_kg": None,  # set after EXPERIMENTS from M_P * precision

        "mass_comparable": True,

        "assumption":
            "For this exploratory comparison only, fractional q/m precision "
            "is treated as fractional mass sensitivity with charge magnitude "
            "held fixed. The reported BASE observable itself is q/m.",

        "reference":
            "Borchert, Ulmer et al., Nature 601, 53-57 (2022)",

        "doi":
            "https://doi.org/10.1038/s41586-021-04203-w",

        "note":
            "Published collaboration result used because the underlying "
            "measurement series is not being consumed as a public dataset "
            "by this sandbox.",

        "prospective_note":
            "PROSPECTIVE ONLY (no number plugged in): BASE demonstrated "
            "coherent spectroscopy of a single antiproton spin — the first "
            "antimatter qubit — with spin coherence times of about 50 s "
            "(Latacz et al., Nature 644, 64-68 (2025), "
            "DOI 10.1038/s41586-025-09323-1). This points to at least "
            "tenfold improved magnetic-moment tests in future; it changes "
            "no value in this sandbox.",
    },

    "BASE magnetic moment (Smorra 2017)": {
        "description":
            "Antiproton magnetic-moment measurement — Penning trap (BASE)",

        "observable":
            "antiproton magnetic moment",

        "source_type": PUBLISHED_RESULT,

        "published_result":
            "mu_pbar = -2.7928473441(42) mu_N",

        "temperature_K": 0.006,

        "temperature_basis":
            "ASSUMED operating temperature — same BASE assumption as the "
            "q/m row above; see TEMPERATURE_NOTE.",

        # 1.5 parts per billion (68% C.L.).
        "fractional_precision": 1.5e-9,

        "mass_sensitivity_kg": None,
        "mass_comparable": False,
        "assumption": None,

        "reference":
            "Smorra et al. (BASE), Nature 550, 371-374 (2017)",

        "doi":
            "https://doi.org/10.1038/nature24048",

        "note":
            "Current best antiproton magnetic-moment result; supersedes "
            "the ATRAP (2013) value for this observable. Magnetic moment "
            "is a different observable class and is excluded from the "
            "mass-sensitivity gap calculation.",
    },

    "ALPHA-2 (CERN AD)": {
        "description":
            "Antihydrogen 1S-2S laser spectroscopy — magnetic trap",

        "observable":
            "1S-2S transition frequency",

        "source_type": PUBLISHED_RESULT,

        "published_result":
            "f_d-d = 2,466,061,103,079.4(5.4) kHz "
            "(d-d hyperfine component of the 1S-2S transition)",

        "temperature_K": 0.5,

        "temperature_basis":
            "ASSUMED operating temperature, set by the magnetic-trap "
            "depth scale: ALPHA trap well depth 0.54 K (ALPHA Collab., "
            "Nature Physics 7, 558-564 (2011)); CERN ALPHA pages put the "
            "trap depth at 'about 0.5 Kelvin'. The trapped-atom "
            "distribution itself is ~200 mK truncated at that depth.",

        # ~2 parts per trillion (5.4 kHz on 2.466e12 kHz).
        "fractional_precision": 2.0e-12,

        "mass_sensitivity_kg": None,
        "mass_comparable": False,
        "assumption": None,

        "reference":
            "ALPHA Collaboration, Nature 557, 71-75 (2018)",

        "doi":
            "https://doi.org/10.1038/s41586-018-0017-2",

        "note":
            "Frequency precision is retained as spectroscopy precision. "
            "It is not converted into an absolute mass sensitivity.",
    },

    "ALPHA 1S-2S hyperfine components (2025)": {
        "description":
            "Antihydrogen 1S-2S hyperfine-component spectroscopy — magnetic trap",

        "observable":
            "1S-2S transition frequency, c-c and d-d hyperfine components",

        "source_type": PUBLISHED_RESULT,

        "published_result":
            "c-c component determined with the same precision as the d-d "
            "component (~2 ppt); combined with the 1S hyperfine splitting "
            "this yields the 2S hyperfine splitting",

        "temperature_K": 0.5,

        "temperature_basis":
            "ASSUMED operating temperature — same ALPHA trap-depth scale "
            "as the 1S-2S row above.",

        # Same ~2 ppt scale as the d-d component.
        "fractional_precision": 2.0e-12,

        "mass_sensitivity_kg": None,
        "mass_comparable": False,
        "assumption": None,

        "reference":
            "ALPHA Collaboration, Nature Physics 21 (2025)",

        "doi":
            "https://doi.org/10.1038/s41567-024-02712-9",

        "note":
            "Precision spectroscopy of the hyperfine components of the "
            "1S-2S transition. Frequency precision is retained as "
            "spectroscopy precision; not converted into a mass sensitivity.",
    },

    "ALPHA ground-state hyperfine splitting (2026)": {
        "description":
            "Antihydrogen ground-state hyperfine splitting — microwave "
            "spectroscopy in a 1-T magnetic field (ALPHA-2 apparatus)",

        "observable":
            "ground-state hyperfine splitting frequency a_1S/h",

        "source_type": PUBLISHED_RESULT,

        "published_result":
            "a_1S/h = 1,420,404.8 +/- 1.1 (stat.) +/- 5.6 (sys.) kHz "
            "in a 1-T magnetic field (4 ppm)",

        "temperature_K": 0.5,

        "temperature_basis":
            "ASSUMED operating temperature — same ALPHA trap-depth scale "
            "as the 1S-2S row above.",

        # 4 parts per million.
        "fractional_precision": 4.0e-6,

        "mass_sensitivity_kg": None,
        "mass_comparable": False,
        "assumption": None,

        "reference":
            "Akbari et al. (ALPHA Collaboration), Nature 653, 1022-1026 (2026)",

        "doi":
            "https://doi.org/10.1038/s41586-026-10556-x",

        "note":
            "4 ppm measurement from ~24,000 anti-atoms; two orders of "
            "magnitude better than the previous 400 ppm. At this level the "
            "measurement is sensitive to the internal structure of the "
            "antiproton (~40 ppm). Frequency precision is retained as "
            "spectroscopy precision; not converted into a mass sensitivity.",
    },

    "ATRAP (historical)": {
        "description":
            "Antiproton magnetic-moment measurement — Penning trap "
            "(HISTORICAL; superseded for this observable by Smorra et al., "
            "BASE, Nature 550, 371-374 (2017), 1.5 ppb)",

        "observable":
            "antiproton magnetic moment",

        "source_type": PUBLISHED_RESULT,

        "published_result":
            "mu_pbar / mu_N = -2.792845 +/- 0.000012",

        "temperature_K": 4.2,

        "temperature_basis":
            "SOURCED electrode temperature: 'Thermal contact with liquid "
            "helium keeps the electrodes at 4.2 K' (CERN Courier on "
            "DiSciacca et al. 2013).",

        # 4.4 parts per million.
        "fractional_precision": 4.4e-6,

        "mass_sensitivity_kg": None,
        "mass_comparable": False,
        "assumption": None,

        "reference":
            "DiSciacca et al. (ATRAP), Phys. Rev. Lett. 110, 130801 (2013)",

        "doi":
            "https://doi.org/10.1103/PhysRevLett.110.130801",

        "note":
            "HISTORICAL magnetic-moment result, retained for provenance. "
            "The current best value is Smorra et al. (BASE, 2017), "
            "1.5 ppb — ~2,900x more precise than ATRAP's 4.4 ppm. "
            "Magnetic moment is a different observable class and is excluded "
            "from the mass-sensitivity gap calculation.",
    },
}

# ── Derived BASE mass sensitivity ─────────────────────────────────────────────
# Single source of truth: the fractional precision in the BASE entry above.
# (Previously this was a second, independent literal — which is how the 10x
# transcription error survived: the two literals could disagree silently.)
EXPERIMENTS["BASE (CERN AD)"]["mass_sensitivity_kg"] = (
    M_P * EXPERIMENTS["BASE (CERN AD)"]["fractional_precision"]
)


# ── Landauer calculations ─────────────────────────────────────────────────────

def landauer_energy(T_kelvin, n_bits=1):
    """Landauer lower-bound energy for n_bits irreversible erasures [J]."""
    return n_bits * LN2 * K_B * T_kelvin


def landauer_mass_equivalent(T_kelvin, n_bits=1):
    """
    E/c^2 mass-equivalent of the Landauer lower-bound energy [kg].

    This is an energy-equivalent bookkeeping quantity. It is not asserted to
    constitute an additional physical mass reservoir.
    """
    return landauer_energy(T_kelvin, n_bits) / (C ** 2)


# ── CERN query ────────────────────────────────────────────────────────────────

def query_cern(term, max_results=5):
    """Query CERN Open Data. Return None on transport/API failure."""
    params = {
        "q": term,
        "size": max_results,
    }

    try:
        response = requests.get(
            SEARCH_URL,
            params=params,
            timeout=15,
        )
        response.raise_for_status()
        payload = response.json()
        return payload.get("hits", {}).get("hits", [])
    except (requests.RequestException, ValueError):
        return None


def find_datasets():
    """
    Discovery only.

    A search hit is NOT automatically treated as experimental input.
    A dataset becomes authoritative input only after its provenance,
    observable, and analysis path have been explicitly validated.
    """

    print("\n── CERN Open Data Discovery ─────────────────────────────────────")

    total_hits = 0

    for term in SEARCH_TERMS:
        results = query_cern(term)

        if results is None:
            print(f"  {term:<36} API unavailable")
            continue

        print(f"  {term:<36} {len(results)} returned hit(s)")
        total_hits += len(results)

        for hit in results:
            meta = hit.get("metadata", {})
            recid = hit.get("id", "?")
            title = meta.get("title", "untitled")
            experiment = ", ".join(meta.get("experiment") or ["unknown"])

            print(f"      [{experiment}] record {recid}: {title}")
            print(f"      https://opendata.cern.ch/record/{recid}")

    if total_hits == 0:
        print()
        print("  No records were returned for the target search terms.")
        print("  This establishes only the result of the current catalogue")
        print("  queries; it does NOT establish that underlying data do not")
        print("  exist elsewhere.")
        print()
        print("  Published collaboration results will therefore be used for")
        print("  target experiments configured as PUBLISHED_RESULT.")

    return total_hits


# ── Provenance report ─────────────────────────────────────────────────────────

def provenance_report():
    print("\n── Experimental Input Provenance ────────────────────────────────")

    for name, exp in EXPERIMENTS.items():
        print(f"\n  {name}")
        print(f"    Source type : {exp['source_type']}")
        print(f"    Observable  : {exp['observable']}")
        print(f"    Result      : {exp['published_result']}")
        print(f"    Precision   : {exp['fractional_precision']:.3e} fractional")
        print(f"    Temperature : {exp['temperature_K']} K")
        print(f"    Temp. basis : {exp['temperature_basis']}")
        print(f"    Reference   : {exp['reference']}")
        print(f"    DOI         : {exp['doi']}")

        if exp.get("prospective_note"):
            print(f"    Prospective : {exp['prospective_note']}")

        if exp["mass_comparable"]:
            print("    Mass gap    : eligible under declared assumption")
            print(f"    Assumption  : {exp['assumption']}")
        else:
            print("    Mass gap    : N/A — incompatible observable")


# ── Mass-equivalent comparison ────────────────────────────────────────────────

def feasibility_report():
    print("\n── Landauer Energy / Mass-Equivalent Scale ─────────────────────")

    print(
        f"  {'Experiment':<46}"
        f"{'Temp':>10}"
        f"{'Landauer E/bit':>20}"
        f"{'E/c² per bit':>20}"
        f"{'Mass sensitivity':>20}"
        f"{'Gap':>10}"
    )

    print("  " + "─" * 126)

    rows = []

    for name, exp in EXPERIMENTS.items():
        temperature = exp["temperature_K"]

        energy = landauer_energy(temperature)
        mass_eq = landauer_mass_equivalent(temperature)

        sensitivity = exp["mass_sensitivity_kg"]

        if exp["mass_comparable"] and sensitivity is not None:
            gap = math.log10(sensitivity / mass_eq)
            sensitivity_text = f"{sensitivity:.3e}"
            gap_text = f"{gap:.1f} OOM"
        else:
            gap = None
            sensitivity_text = "N/A"
            gap_text = "N/A"

        rows.append({
            "name": name,
            "temperature_K": temperature,
            "landauer_energy_J": energy,
            "landauer_mass_equivalent_kg": mass_eq,
            "mass_sensitivity_kg": sensitivity,
            "gap_oom": gap,
            "experiment": exp,
        })

        print(
            f"  {name:<46}"
            f"{temperature:>9.4f}K"
            f"{energy:>20.3e}"
            f"{mass_eq:>20.3e}"
            f"{sensitivity_text:>20}"
            f"{gap_text:>10}"
        )

    print()
    print("  NOTE: " + TEMPERATURE_NOTE)

    return rows


# ── Detection / scale report ──────────────────────────────────────────────────

def detection_requirements(rows):
    print("\n── Exploratory Mass-Sensitivity Comparison ─────────────────────")

    comparable = [row for row in rows if row["gap_oom"] is not None]

    if not comparable:
        print("  No configured observable is mass-comparable.")
        return

    for row in comparable:
        exp = row["experiment"]

        # Report the one-bit Landauer comparison separately from the
        # historical sandbox target of one tenth of that scale.
        landauer_scale = row["landauer_mass_equivalent_kg"]
        ratio_to_landauer = row["mass_sensitivity_kg"] / landauer_scale

        required = landauer_scale * 0.1
        ratio_to_target = row["mass_sensitivity_kg"] / required
        target_gap_oom = math.log10(ratio_to_target)

        print(f"\n  {row['name']}")
        print(f"    Observable          : {exp['observable']}")
        print(f"    Temperature         : {row['temperature_K']} K")
        print(
            "    Landauer E/c² scale : "
            f"{row['landauer_mass_equivalent_kg']:.3e} kg/bit"
        )
        print(
            "    Comparison precision: "
            f"{row['mass_sensitivity_kg']:.3e} kg"
        )
        print(f"    Ratio to 1-bit scale: {ratio_to_landauer:.3e}×")
        print(f"    Gap to 1-bit scale  : {row['gap_oom']:.1f} OOM")
        print(f"    0.1× target scale   : {required:.3e} kg")
        print(f"    Ratio to 0.1× target: {ratio_to_target:.3e}×")
        print(f"    Gap to 0.1× target  : {target_gap_oom:.1f} OOM")
        print(f"    Assumption          : {exp['assumption']}")

    print()
    print("  NOTE:")
    print("  This is a numerical sensitivity comparison, not a prediction")
    print("  that an additional mass deficit exists or would be measured.")
    print()
    print("  TEMPERATURE SENSITIVITY:")
    print("  " + TEMPERATURE_NOTE)
    print("  For BASE: at T = 1.92 K (published axial temperature) the")
    print("  1-bit gap would be ~2.1 OOM; at T = 6 K (trap-surface")
    print("  temperature) ~1.6 OOM — not 4.6 OOM. The BASE gap is")
    print("  conditional on the assumed 0.006 K operating temperature.")


# ── Analytical controls ───────────────────────────────────────────────────────
#
# Coalescence §5, Eq. 13–15, App. C Eq. C1.
#
# The recurrent register is a Bernoulli register. At lag tau the register
# holds the input bit with flip probability q, so the lag-tau register
# distribution is Bernoulli(p_tau) with
#
#     p_tau = (1 + 0.9^tau) / 2,   tau = 1..6,   q = 0.05.
#
# The lag term is the Jensen–Shannon divergence (in bits) between that
# distribution and its flipped counterpart:
#
#     D_JS(tau) = D_JS(Bern(p_tau) || Bern(1 - p_tau))
#               = 1 - h2(p_tau),
#
# where h2 is the binary entropy. The identity holds because the mixture
# of Bern(p) and Bern(1-p) is Bern(1/2), whose entropy is 1 bit, and
# h2(1-p) = h2(p). The code computes the divergence from the general
# definition (mixture entropy minus mean entropy) and the identity is
# checked in the test suite — no lag term is ever a literal.
#
# Aggregation uses the paper's uniform weights: C_H intact is the MEAN of
# the six lag terms. After the matched feedback cut no lag term survives,
# so C_H cut is the sum over the (empty) surviving set: exactly 0.
#
# Delay line (Proposition 1): a deterministic shift reproduces the input
# bit exactly, so conditional on the input the output distributions are
# the point masses delta_0 and delta_1. Their supports are disjoint, so
# their Jensen–Shannon divergence is exactly 1 bit — computed below from
# the same divergence function, not asserted. A delay line has no return
# edge to cut, so intact and cut coincide and O_H = 0.

REGISTER_FLIP_Q = 0.05      # Bernoulli register flip probability (App. C)
REGISTER_DECAY = 0.9        # per-lag persistence factor (App. C)
REGISTER_LAGS = (1, 2, 3, 4, 5, 6)


def binary_entropy(p):
    """Binary entropy h2(p) in bits. 0*log2(0) is taken as 0."""
    if p <= 0.0 or p >= 1.0:
        return 0.0
    return -p * math.log2(p) - (1.0 - p) * math.log2(1.0 - p)


def jensen_shannon_divergence(p, q):
    """
    Jensen–Shannon divergence in bits between Bernoulli(p) and
    Bernoulli(q), from the definition: H(mixture) - mean(H(p), H(q)).
    """
    m = 0.5 * (p + q)
    return binary_entropy(m) - 0.5 * (
        binary_entropy(p) + binary_entropy(q)
    )


def register_lag_terms(q=REGISTER_FLIP_Q, decay=REGISTER_DECAY,
                       lags=REGISTER_LAGS):
    """
    Eq. C1 lag terms D_JS(tau) = 1 - h2(p_tau), p_tau = (1 + decay^tau)/2.

    Computed as the Jensen–Shannon divergence between Bernoulli(p_tau)
    and its flipped counterpart Bernoulli(1 - p_tau). Returns the list of
    terms in lag order. (The flip probability q enters the paper's
    register construction; the lag terms as stated in App. C are the
    D_JS values above.)
    """
    terms = []
    for tau in lags:
        p_tau = (1.0 + decay ** tau) / 2.0
        terms.append(jensen_shannon_divergence(p_tau, 1.0 - p_tau))
    return terms


def aggregate_lag_terms(terms):
    """Uniform-weight aggregate (mean) of lag terms; 0.0 for an empty set."""
    if not terms:
        return 0.0
    return sum(terms) / len(terms)


def recurrent_control():
    """
    Recurrent register control (Eq. C1).

    Returns dict with the six lag terms, C_H intact (mean of the terms),
    C_H cut (0: no lag term survives the matched feedback cut), and
    O_H = intact - cut.
    """
    terms = register_lag_terms()
    intact = aggregate_lag_terms(terms)
    surviving_after_cut = []  # the cut removes every lag term
    cut = aggregate_lag_terms(surviving_after_cut)
    return {
        "lag_terms": terms,
        "c_h_intact": intact,
        "c_h_cut": cut,
        "o_h": intact - cut,
    }


def delay_line_control(n_stages=6):
    """
    Feed-forward delay line, Proposition 1 (computed, not asserted).

    A deterministic shift maps input bit b to output b with probability 1,
    so the conditional output distributions are the point masses [1, 0]
    (input 0) and [0, 1] (input 1). Disjoint support -> their
    Jensen–Shannon divergence is exactly 1 bit. The delay line has no
    return edge, so the matched cut changes nothing: intact == cut == 1
    (per stage; reported as the single-stage value) and O_H = 0.
    """
    p_given_0 = 0.0  # P(output = 1 | input = 0) for a deterministic shift
    p_given_1 = 1.0  # P(output = 1 | input = 1) for a deterministic shift
    c_h = jensen_shannon_divergence(p_given_0, p_given_1)
    # No return edge exists in a feed-forward line, so the cut is identical.
    return {
        "n_stages": n_stages,
        "c_h_intact": c_h,
        "c_h_cut": c_h,
        "o_h": c_h - c_h,
    }


def analytical_controls():
    """
    Computational controls aligned with the revised framework.

    Persistence alone cannot identify recurrence:
      * feed-forward storage can preserve an earlier signal;
      * recurrence requires an intact-vs-feedback-cut contrast.

    These are analytical demonstrations, not empirical CERN results.
    Every number below is computed from Eq. C1 / Proposition 1.
    """

    print("\n── Analytical Controls: Persistence vs Feedback ────────────────")

    # Negative control: six-stage perfect delay line (Proposition 1).
    delay = delay_line_control()
    o_delay = delay["o_h"]

    # Positive control: Bernoulli register, Eq. C1.
    recurrent = recurrent_control()
    lag_terms = recurrent["lag_terms"]

    print()
    print("  Feed-forward delay line (Proposition 1: deterministic shift,")
    print("  disjoint support -> D_JS = 1 bit, computed)")
    print(f"    C_H intact : {delay['c_h_intact']:.3f}")
    print(f"    C_H cut    : {delay['c_h_cut']:.3f}")
    print(f"    O_H        : {o_delay:.3f}")
    print("    Interpretation: persistence without feedback-specific effect.")

    print()
    print("  Recurrent register control (App. C, Eq. C1: q = 0.05,")
    print("  tau = 1..6, uniform weights)")
    for tau, term in zip(REGISTER_LAGS, lag_terms):
        print(f"    D_JS(tau={tau}) : {term:.6f}")
    print(f"    C_H intact : {recurrent['c_h_intact']:.3f}  [mean of lag terms]")
    print(f"    C_H cut    : {recurrent['c_h_cut']:.3f}  [no lag term survives the cut]")
    print(f"    O_H        : {recurrent['o_h']:.3f}")
    print("    Interpretation: positive effect attributable to declared return edge.")
    print("    Values are computed from Eq. C1, not experimental measurements.")

    print()
    print("  O_H is an architectural/interventional quantity.")
    print("  It is not a consciousness score or personhood probability.")

    return {"delay_line": delay, "recurrent": recurrent}


# ── Scope summary ─────────────────────────────────────────────────────────────

def scope_summary():
    print("\n── Interpretation Boundary ─────────────────────────────────────")

    print("""
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
""")


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    print("=" * 78)
    print("  CERN / Published-Result Landauer Analysis Sandbox")
    print(f"  Run: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("  Revision: November 2026 — Eq. C1 controls computed; BASE 16 ppt")
    print("  corrected to 1.6e-11; temperatures labelled by basis")
    print("=" * 78)

    find_datasets()
    provenance_report()

    rows = feasibility_report()
    detection_requirements(rows)

    analytical_controls()
    scope_summary()

    print("\n── References ──────────────────────────────────────────────────")
    print("  CERN Open Data Portal")
    print("    https://opendata.cern.ch")
    print()
    print("  BASE q/m (16 ppt)")
    print("    https://doi.org/10.1038/s41586-021-04203-w")
    print()
    print("  BASE magnetic moment, 1.5 ppb (Smorra et al. 2017)")
    print("    https://doi.org/10.1038/nature24048")
    print()
    print("  BASE coherent single-antiproton spin qubit, ~50 s (Latacz et al. 2025)")
    print("    https://doi.org/10.1038/s41586-025-09323-1")
    print()
    print("  ALPHA 1S-2S (Ahmadi et al. 2018)")
    print("    https://doi.org/10.1038/s41586-018-0017-2")
    print()
    print("  ALPHA 1S-2S hyperfine components (2025)")
    print("    https://doi.org/10.1038/s41567-024-02712-9")
    print()
    print("  ALPHA ground-state hyperfine splitting, 4 ppm (Akbari et al. 2026)")
    print("    https://doi.org/10.1038/s41586-026-10556-x")
    print()
    print("  ATRAP magnetic moment, historical (DiSciacca et al. 2013)")
    print("    https://doi.org/10.1103/PhysRevLett.110.130801")
    print()
    print("  Proton mass: NIST CODATA 2022, 1.67262192595(52)e-27 kg")
    print("    https://physics.nist.gov/cgi-bin/cuu/Value?mp")
    print()


if __name__ == "__main__":
    main()
