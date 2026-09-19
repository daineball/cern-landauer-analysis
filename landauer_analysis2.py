"""
CERN / Published-Result Landauer Analysis Sandbox
==================================================

Computational companion to:

    The Coalescence of Thought
    A Multiscale Causal Framework for Persistent Self-Influence
    in Physical Systems

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
"""

import math
from datetime import datetime

import requests


# ── Physical constants ────────────────────────────────────────────────────────

K_B = 1.380649e-23       # Boltzmann constant [J/K], exact SI
C = 2.99792458e8         # speed of light [m/s], exact SI
LN2 = math.log(2)
M_P = 1.67262192595e-27  # proton mass [kg], numerical reference value


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

        # 16 parts per trillion reported uncertainty scale.
        "fractional_precision": 1.6e-12,

        # Exploratory mass-equivalent sensitivity. This is NOT an independent
        # direct mass measurement.
        "mass_sensitivity_kg": M_P * 1.6e-12,

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
    },

    "ALPHA-2 (CERN AD)": {
        "description":
            "Antihydrogen 1S-2S laser spectroscopy — magnetic trap",

        "observable":
            "1S-2S transition frequency",

        "source_type": PUBLISHED_RESULT,

        "published_result":
            "Published ALPHA 1S-2S spectroscopy result; see cited paper.",

        "temperature_K": 0.5,
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

    "ATRAP": {
        "description":
            "Antiproton magnetic-moment measurement — Penning trap",

        "observable":
            "antiproton magnetic moment",

        "source_type": PUBLISHED_RESULT,

        "published_result":
            "mu_pbar / mu_N = -2.792845 +/- 0.000012",

        "temperature_K": 4.2,
        "fractional_precision": 4.4e-6,

        "mass_sensitivity_kg": None,
        "mass_comparable": False,
        "assumption": None,

        "reference":
            "DiSciacca et al. (ATRAP), Phys. Rev. Lett. 110, 130801 (2013)",

        "doi":
            "https://doi.org/10.1103/PhysRevLett.110.130801",

        "note":
            "Magnetic moment is a different observable class and is excluded "
            "from the mass-sensitivity gap calculation.",
    },
}


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
        print(f"    Reference   : {exp['reference']}")
        print(f"    DOI         : {exp['doi']}")

        if exp["mass_comparable"]:
            print("    Mass gap    : eligible under declared assumption")
            print(f"    Assumption  : {exp['assumption']}")
        else:
            print("    Mass gap    : N/A — incompatible observable")


# ── Mass-equivalent comparison ────────────────────────────────────────────────

def feasibility_report():
    print("\n── Landauer Energy / Mass-Equivalent Scale ─────────────────────")

    print(
        f"  {'Experiment':<22}"
        f"{'Temp':>10}"
        f"{'Landauer E/bit':>20}"
        f"{'E/c² per bit':>20}"
        f"{'Mass sensitivity':>20}"
        f"{'Gap':>10}"
    )

    print("  " + "─" * 102)

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
            f"  {name:<22}"
            f"{temperature:>9.4f}K"
            f"{energy:>20.3e}"
            f"{mass_eq:>20.3e}"
            f"{sensitivity_text:>20}"
            f"{gap_text:>10}"
        )

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

        # Historical sandbox convention: target sensitivity one tenth of the
        # one-bit mass-equivalent scale.
        required = row["landauer_mass_equivalent_kg"] * 0.1
        improvement = row["mass_sensitivity_kg"] / required

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
        print(f"    0.1× target scale   : {required:.3e} kg")
        print(f"    Scale ratio         : {improvement:.3e}×")
        print(f"    Gap                 : {row['gap_oom']:.1f} OOM")
        print(f"    Assumption          : {exp['assumption']}")

    print()
    print("  NOTE:")
    print("  This is a numerical sensitivity comparison, not a prediction")
    print("  that an additional mass deficit exists or would be measured.")


# ── Analytical controls ───────────────────────────────────────────────────────

def analytical_controls():
    """
    Minimal computational controls aligned with the revised framework.

    Persistence alone cannot identify recurrence:
      * feed-forward storage can preserve an earlier signal;
      * recurrence requires an intact-vs-feedback-cut contrast.

    These are analytical demonstrations, not empirical CERN results.
    """

    print("\n── Analytical Controls: Persistence vs Feedback ────────────────")

    # Negative control:
    # Six-stage perfect delay line. An input persists six steps downstream,
    # but there is no return edge to cut.
    intact_delay = 1.0
    cut_delay = 1.0
    o_delay = intact_delay - cut_delay

    # Positive toy control:
    # A normalized recurrent contribution is present in the intact toy system
    # and absent after its declared return edge is cut.
    intact_recurrent = 1.0
    cut_recurrent = 0.35
    o_recurrent = intact_recurrent - cut_recurrent

    print()
    print("  Feed-forward delay line")
    print(f"    C_H intact : {intact_delay:.3f}")
    print(f"    C_H cut    : {cut_delay:.3f}")
    print(f"    O_H        : {o_delay:.3f}")
    print("    Interpretation: persistence without feedback-specific effect.")

    print()
    print("  Recurrent toy control")
    print(f"    C_H intact : {intact_recurrent:.3f}  [illustrative normalized value]")
    print(f"    C_H cut    : {cut_recurrent:.3f}  [illustrative normalized value]")
    print(f"    O_H        : {o_recurrent:.3f}")
    print("    Interpretation: positive effect attributable to declared return edge.")
    print("    Values are illustrative control parameters, not experimental measurements.")

    print()
    print("  O_H is an architectural/interventional quantity.")
    print("  It is not a consciousness score or personhood probability.")


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
    print("  Revision: September 2026 provenance + observable audit")
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
    print("  BASE")
    print("    https://doi.org/10.1038/s41586-021-04203-w")
    print()
    print("  ALPHA")
    print("    https://doi.org/10.1038/s41586-018-0017-2")
    print()
    print("  ATRAP")
    print("    https://doi.org/10.1103/PhysRevLett.110.130801")
    print()


if __name__ == "__main__":
    main()
