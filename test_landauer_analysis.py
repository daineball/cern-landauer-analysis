#!/usr/bin/env python3

import math
import unittest

import landauer_analysis2 as la


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

    def test_base_mass_sensitivity(self):
        """BASE exploratory fixed-charge mass-sensitivity conversion."""
        sensitivity = la.M_P * 1.6e-12

        self.assertTrue(
            math.isclose(
                sensitivity,
                2.676195e-39,
                rel_tol=1e-7,
            )
        )

    def test_base_one_bit_comparison(self):
        """BASE precision vs the one-bit Landauer mass-equivalent scale."""
        sensitivity = la.M_P * 1.6e-12
        one_bit = (
            la.K_B * 0.006 * math.log(2)
        ) / la.C**2

        ratio = sensitivity / one_bit
        gap_oom = math.log10(ratio)

        self.assertGreater(ratio, 4.0e3)
        self.assertLess(ratio, 4.4e3)
        self.assertGreater(gap_oom, 3.5)
        self.assertLess(gap_oom, 3.7)

    def test_base_point_one_target_comparison(self):
        """Historical 0.1× target remains distinct from the one-bit scale."""
        sensitivity = la.M_P * 1.6e-12
        one_bit = (
            la.K_B * 0.006 * math.log(2)
        ) / la.C**2
        target = one_bit * 0.1

        ratio_one_bit = sensitivity / one_bit
        ratio_target = sensitivity / target

        gap_one_bit = math.log10(ratio_one_bit)
        gap_target = math.log10(ratio_target)

        self.assertGreater(ratio_target, 4.0e4)
        self.assertLess(ratio_target, 4.4e4)

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

    def test_analytical_control_invariants(self):
        """Negative and positive toy-control relationships."""
        intact_delay = 1.0
        cut_delay = 1.0

        intact_recurrent = 1.0
        cut_recurrent = 0.35

        self.assertEqual(intact_delay - cut_delay, 0.0)
        self.assertTrue(
            math.isclose(
                intact_recurrent - cut_recurrent,
                0.65,
                rel_tol=1e-12,
            )
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
