#!/usr/bin/env python3
"""
Regression tests for landauer_analysis2.py (revised 2026-11-20).

These tests check the numbers against INDEPENDENTLY stated values — the
paper's App. C Eq. C1 lag terms, the published BASE 16 ppt precision, and
the cited experimental results — not against literals copied out of the
module under test. Where a test needs an expected number it is written
out here, from the paper / publication, so that reintroducing either
September-2026 error makes the suite fail:

  * BASE fractional precision 1.6e-12 (10x error) -> test_base_* fail.
  * Recurrent control literals 1.0 / 0.35 / O_H 0.65 -> the Eq. C1 tests
    fail, because the old module has no register_lag_terms() at all
    (AttributeError) and no computed lag terms to match.
  * Delay-line bare literals -> test_delay_line_control fails on the old
    module for the same reason (no delay_line_control()).
"""

import math
import unittest

import landauer_analysis2 as la


# Paper, App. C Eq. C1: D_JS(tau) = 1 - h2(p_tau), p_tau = (1 + 0.9^tau)/2,
# tau = 1..6, q = 0.05. Values below are the Eq. C1 numbers as stated in
# the paper, to 6 decimal places.
EXPECTED_LAG_TERMS = [
    0.713603,
    0.547057,
    0.427669,
    0.337854,
    0.268663,
    0.214603,
]
EXPECTED_LAG_MEAN = 0.418242


class TestLandauerAnalysis(unittest.TestCase):
    """Regression tests for the numerical bookkeeping in landauer_analysis2."""

    def test_landauer_energy_and_mass_equivalent(self):
        """E = k_B T ln(2), with m_eq = E/c²."""
        for temperature in (0.006, 0.5, 4.2):
            with self.subTest(temperature_K=temperature):
                energy = la.K_B * temperature * math.log(2)
                mass_eq = energy / la.C**2

                self.assertGreater(energy, 0.0)
                self.assertGreater(mass_eq, 0.0)
                self.assertTrue(
                    math.isclose(
                        mass_eq * la.C**2,
                        energy,
                        rel_tol=1e-12,
                    )
                )

    def test_configured_landauer_scales(self):
        """Guard the three Landauer mass-equivalent scales used in the report."""
        expected = {
            0.006: 6.388790e-43,
            0.5: 5.323991e-41,
            4.2: 4.472153e-40,
        }

        for temperature, expected_mass in expected.items():
            with self.subTest(temperature_K=temperature):
                actual = (
                    la.K_B * temperature * math.log(2)
                ) / la.C**2

                self.assertTrue(
                    math.isclose(
                        actual,
                        expected_mass,
                        rel_tol=1e-7,
                    )
                )

    # ── Eq. C1: binary entropy and Jensen–Shannon divergence ─────────────

    def test_binary_entropy_known_values(self):
        """h2(0.5) = 1 bit; h2(0.95) = 0.286397 (Eq. C1, tau = 1)."""
        self.assertTrue(
            math.isclose(la.binary_entropy(0.5), 1.0, rel_tol=1e-12)
        )
        self.assertTrue(
            math.isclose(la.binary_entropy(0.95), 0.286397, rel_tol=1e-6)
        )
        self.assertEqual(la.binary_entropy(0.0), 0.0)
        self.assertEqual(la.binary_entropy(1.0), 0.0)

    def test_jensen_shannon_divergence_known_values(self):
        """D_JS of disjoint point masses is 1 bit; D_JS(p, p) is 0."""
        self.assertTrue(
            math.isclose(
                la.jensen_shannon_divergence(0.0, 1.0),
                1.0,
                rel_tol=1e-12,
            )
        )
        self.assertTrue(
            math.isclose(
                la.jensen_shannon_divergence(0.3, 0.3),
                0.0,
                abs_tol=1e-12,
            )
        )
        # D_JS(Bern(p) || Bern(1-p)) == 1 - h2(p), the Eq. C1 identity.
        for p in (0.95, 0.905, 0.8645):
            with self.subTest(p=p):
                self.assertTrue(
                    math.isclose(
                        la.jensen_shannon_divergence(p, 1.0 - p),
                        1.0 - la.binary_entropy(p),
                        rel_tol=1e-12,
                    )
                )

    def test_register_lag_terms_eq_c1(self):
        """Lag terms match the paper's Eq. C1 values to 1e-6."""
        terms = la.register_lag_terms()
        self.assertEqual(len(terms), 6)
        for actual, expected in zip(terms, EXPECTED_LAG_TERMS):
            with self.subTest(expected=expected):
                self.assertTrue(
                    math.isclose(actual, expected, abs_tol=1e-6),
                    f"lag term {actual!r} != Eq. C1 value {expected!r}",
                )

    def test_recurrent_control_eq_c1(self):
        """Mean of lag terms 0.418242; cut 0; O_H 0.418 (Eq. C1)."""
        control = la.recurrent_control()
        self.assertTrue(
            math.isclose(
                control["c_h_intact"], EXPECTED_LAG_MEAN, abs_tol=1e-6
            )
        )
        self.assertEqual(control["c_h_cut"], 0.0)
        self.assertTrue(
            math.isclose(control["o_h"], 0.418, abs_tol=1e-3)
        )
        self.assertTrue(
            math.isclose(
                control["o_h"],
                control["c_h_intact"] - control["c_h_cut"],
                rel_tol=1e-12,
            )
        )
        # The old asserted O_H of 0.65 must NOT reappear.
        self.assertFalse(
            math.isclose(control["o_h"], 0.65, rel_tol=1e-9)
        )

    def test_delay_line_control_proposition_1(self):
        """Deterministic shift, disjoint support -> C_H 1/1, O_H 0."""
        control = la.delay_line_control()
        self.assertTrue(
            math.isclose(control["c_h_intact"], 1.0, rel_tol=1e-12)
        )
        self.assertTrue(
            math.isclose(control["c_h_cut"], 1.0, rel_tol=1e-12)
        )
        self.assertEqual(control["o_h"], 0.0)

    def test_analytical_controls_return_values(self):
        """analytical_controls() returns the computed controls it prints."""
        result = la.analytical_controls()
        self.assertTrue(
            math.isclose(
                result["recurrent"]["o_h"], 0.418, abs_tol=1e-3
            )
        )
        self.assertEqual(result["delay_line"]["o_h"], 0.0)

    # ── BASE: corrected 16 ppt chain ─────────────────────────────────────

    def test_base_fractional_precision_is_16_ppt(self):
        """16 ppt = 16e-12 = 1.6e-11 — not the old 1.6e-12."""
        precision = la.EXPERIMENTS["BASE (CERN AD)"]["fractional_precision"]
        self.assertEqual(precision, 1.6e-11)
        self.assertNotEqual(precision, 1.6e-12)

    def test_base_mass_sensitivity(self):
        """BASE exploratory fixed-charge mass-sensitivity conversion."""
        exp = la.EXPERIMENTS["BASE (CERN AD)"]
        sensitivity = exp["mass_sensitivity_kg"]

        # Must derive from the single configured precision, not a literal.
        self.assertTrue(
            math.isclose(
                sensitivity,
                la.M_P * exp["fractional_precision"],
                rel_tol=1e-12,
            )
        )
        self.assertTrue(
            math.isclose(
                sensitivity,
                2.676195e-38,
                rel_tol=1e-7,
            )
        )
        # The old wrong value must NOT reappear.
        self.assertFalse(
            math.isclose(sensitivity, 2.676195e-39, rel_tol=1e-7)
        )

    def test_base_one_bit_comparison(self):
        """BASE precision vs the one-bit Landauer mass-equivalent scale."""
        sensitivity = la.EXPERIMENTS["BASE (CERN AD)"]["mass_sensitivity_kg"]
        one_bit = (
            la.K_B * 0.006 * math.log(2)
        ) / la.C**2

        ratio = sensitivity / one_bit
        gap_oom = math.log10(ratio)

        self.assertGreater(ratio, 4.0e4)
        self.assertLess(ratio, 4.4e4)
        self.assertGreater(gap_oom, 4.5)
        self.assertLess(gap_oom, 4.7)
        # Old wrong ratio/gap (4.189e3, 3.6 OOM) must fail here.
        self.assertFalse(math.isclose(ratio, 4.189e3, rel_tol=1e-2))

    def test_base_point_one_target_comparison(self):
        """Historical 0.1× target remains distinct from the one-bit scale."""
        sensitivity = la.EXPERIMENTS["BASE (CERN AD)"]["mass_sensitivity_kg"]
        one_bit = (
            la.K_B * 0.006 * math.log(2)
        ) / la.C**2
        target = one_bit * 0.1

        ratio_one_bit = sensitivity / one_bit
        ratio_target = sensitivity / target

        gap_one_bit = math.log10(ratio_one_bit)
        gap_target = math.log10(ratio_target)

        self.assertGreater(ratio_target, 4.0e5)
        self.assertLess(ratio_target, 4.4e5)
        self.assertGreater(gap_target, 5.5)
        self.assertLess(gap_target, 5.7)

        # Moving the target down by 10× must increase the ratio by
        # exactly 10× and the logarithmic gap by exactly 1 OOM.
        self.assertTrue(
            math.isclose(
                ratio_target,
                ratio_one_bit * 10.0,
                rel_tol=1e-12,
            )
        )
        self.assertTrue(
            math.isclose(
                gap_target,
                gap_one_bit + 1.0,
                rel_tol=1e-12,
            )
        )

    def test_proton_mass_codadata_2022(self):
        """M_P matches NIST CODATA 2022: 1.67262192595(52)e-27 kg."""
        self.assertEqual(la.M_P, 1.67262192595e-27)

    # ── Data shortlist: new and relabelled rows ───────────────────────────

    def test_smorra_2017_row_present(self):
        """BASE 2017 magnetic-moment row (Smorra et al., 1.5 ppb)."""
        exp = la.EXPERIMENTS["BASE magnetic moment (Smorra 2017)"]
        self.assertIn("-2.7928473441(42)", exp["published_result"])
        self.assertEqual(exp["fractional_precision"], 1.5e-9)
        self.assertEqual(exp["doi"], "https://doi.org/10.1038/nature24048")
        self.assertFalse(exp["mass_comparable"])

    def test_atrap_labelled_historical(self):
        """ATRAP kept, labelled historical, superseded by Smorra 2017."""
        self.assertIn("ATRAP (historical)", la.EXPERIMENTS)
        self.assertNotIn("ATRAP", la.EXPERIMENTS)
        note = la.EXPERIMENTS["ATRAP (historical)"]["note"]
        self.assertIn("HISTORICAL", note)
        self.assertIn("Smorra", note)

    def test_alpha_numeric_value_filled_in(self):
        """ALPHA-2 d-d frequency now carries its numeric value."""
        exp = la.EXPERIMENTS["ALPHA-2 (CERN AD)"]
        self.assertIn("2,466,061,103,079.4(5.4)", exp["published_result"])
        self.assertNotIn("see cited paper", exp["published_result"])

    def test_alpha_2025_hyperfine_components_row(self):
        """ALPHA 2025 1S-2S hyperfine-components row present."""
        exp = la.EXPERIMENTS["ALPHA 1S-2S hyperfine components (2025)"]
        self.assertEqual(
            exp["doi"], "https://doi.org/10.1038/s41567-024-02712-9"
        )
        self.assertFalse(exp["mass_comparable"])

    def test_alpha_2026_hyperfine_row(self):
        """ALPHA 2026 4-ppm hyperfine row present with the paper's value."""
        exp = la.EXPERIMENTS["ALPHA ground-state hyperfine splitting (2026)"]
        self.assertIn("1,420,404.8", exp["published_result"])
        self.assertEqual(exp["fractional_precision"], 4.0e-6)
        self.assertEqual(
            exp["doi"], "https://doi.org/10.1038/s41586-026-10556-x"
        )
        self.assertFalse(exp["mass_comparable"])

    def test_base_2025_qubit_prospective_only(self):
        """BASE 2025 spin-qubit result is a footnote only — no number used."""
        exp = la.EXPERIMENTS["BASE (CERN AD)"]
        self.assertIn("prospective_note", exp)
        self.assertIn("50 s", exp["prospective_note"])
        self.assertIn("10.1038/s41586-025-09323-1", exp["prospective_note"])
        self.assertIn("PROSPECTIVE ONLY", exp["prospective_note"])

    def test_temperatures_carry_a_basis(self):
        """Every experiment labels its temperature as sourced or assumed."""
        for name, exp in la.EXPERIMENTS.items():
            with self.subTest(experiment=name):
                self.assertIn("temperature_basis", exp)
                self.assertTrue(
                    exp["temperature_basis"].startswith(
                        ("ASSUMED", "SOURCED")
                    ),
                    f"{name} temperature_basis must start ASSUMED/SOURCED",
                )


if __name__ == "__main__":
    unittest.main(verbosity=2)
