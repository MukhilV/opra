# test_allocation_mechanisms.py

from django.test import TestCase
import numpy as np

from prefpy.mechanism import (
    MechanismRoundRobinAllocation,
    MechanismMaximumNashWelfare,
    MechanismMarketAllocation,
    MechanismLeximinAllocation,
    MechanismMarketEqAllocation,
    MechanismMaximumNashWelfareBinary
)

# import property checks (ef, ef1, po, etc.)
from prefpy.allocation_properties import *
from prefpy.allocation_utils import *

class TestAllocationMechanismsBase(TestCase):
    """
    base class for allocation mechanism tests.
    defines common valuation matrices for general working checks.
    """

    @classmethod
    def setUpClass(cls):
        """
        initializes general test matrices shared across all allocation algorithms.
        """
        super().setUpClass()
        
        # 2 agents, 2 items
        cls.V1 = np.array([
            [3, 1],
            [1, 3]
        ], dtype=float)

        # 2 agents, 3 items
        cls.V2 = np.array([
            [10, 5, 2],
            [5, 10, 2]
        ], dtype=float)

        # 3-agent scenario
        cls.V3 = np.array([
            [4, 2, 1],
            [2, 5, 3],
            [1, 3, 6]
        ], dtype=float)

    def check_allocation_validity(self, V, A):
        """
        ensures allocation matrix is valid (each item assigned exactly once).
        """
        self.assertTrue(valid_allocation(V, A), "allocation is invalid: some items are not assigned correctly.")

    def test_matrix_shapes(self):
        """
        ensures valuation matrices are correctly defined.
        """
        for V in [self.V1, self.V2, self.V3]:
            self.assertIsInstance(V, np.ndarray)
            self.assertGreaterEqual(V.shape[0], 2)  # at least 2 agents
            self.assertGreaterEqual(V.shape[1], 2)  # at least 2 items


# ------------------------------------------------------------------------
#  round robin allocation tests
# ------------------------------------------------------------------------

class TestRoundRobinAllocation(TestAllocationMechanismsBase):
    """
    tests for round robin allocation mechanism.
    """

    def setUp(self):
        """ initialize round robin allocation mechanism. """
        self.rr_alloc = MechanismRoundRobinAllocation()

    def test_round_robin_basic(self):
        """ test if round robin mechanism runs successfully. """
        for V in [self.V1, self.V2, self.V3]:
            result = self.rr_alloc.allocate(V)
            self.assertTrue(result.status, "round robin allocation failed to return a valid result.")

            A = np.array(result.A)

            # check that allocation matrix is valid
            self.check_allocation_validity(V, A)

            print("\n" + "=" * 70)
            print("ROUND ROBIN BASIC TEST")
            print("=" * 70 + "\n")
            print("Valuations:\n", V)
            print("Allocation Matrix (A):\n", A)
            print()

    def test_round_robin_ef1(self):
        """ check if round robin always satisfies EF1 (envy-freeness up to one item). """
        for V in [self.V1, self.V2, self.V3]:
            result = self.rr_alloc.allocate(V)
            self.assertTrue(result.status, "round robin allocation failed.")

            A = np.array(result.A)

            # round robin is known to always satisfy EF1
            self.assertTrue(is_ef1(V, A), "round robin should always be EF1 but failed.")

            print("\n" + "=" * 70)
            print("ROUND ROBIN EF1 CHECK")
            print("=" * 70 + "\n")
            print("Valuations:\n", V)
            print("Allocation Matrix (A):\n", A)
            print(f"EF1: {is_ef1(V, A)}\n")

    def test_round_robin_po(self):
        """ check if round robin produces a pareto optimal allocation. """
        for V in [self.V1, self.V2, self.V3]:
            result = self.rr_alloc.allocate(V)
            self.assertTrue(result.status, "round robin allocation failed.")

            A = np.array(result.A)

            # round robin is not guaranteed to be PO, but we still check
            po_flag = is_po(V, A)

            print("\n" + "=" * 70)
            print("ROUND ROBIN PO CHECK")
            print("=" * 70 + "\n")
            print("Valuations:\n", V)
            print("Allocation Matrix (A):\n", A)
            print(f"PO: {po_flag}\n")



# ------------------------------------------------------------------------
#  maximum nash welfare (mnw) allocation tests
# ------------------------------------------------------------------------

class TestMaximumNashWelfare(TestAllocationMechanismsBase):
    """
    tests for the maximum nash welfare (mnw) mechanism.
    """

    def setUp(self):
        """ initialize mnw allocation mechanism. """
        self.mnw_alloc = MechanismMaximumNashWelfare()

    def test_mnw_basic(self):
        """ test if mnw mechanism runs successfully. """
        for idx, V in enumerate([self.V1, self.V2, self.V3], start=1):
            result = self.mnw_alloc.allocate(V)
            self.assertTrue(result.status)

            A = result.A
            self.check_allocation_validity(V, A)

            # Compute Nash Welfare
            computed_nw = np.prod([np.sum(A[j] * V[j]) for j in range(V.shape[0])])

            print("\n" + "=" * 70)
            print(f"MNW BASIC TEST ({idx})")
            print("=" * 70 + "\n")
            print("Valuations:\n", V)
            print("Allocation Matrix (A):\n", A)
            print(f"Nash Welfare: {result.w} (Computed: {computed_nw})")
            print("Utilities:", result.U, "\n")

            self.assertEqual(result.w, computed_nw, "Incorrect Nash Welfare Calculation!")

    def test_mnw_properties(self):
        """ check which properties mnw satisfies. """
        for idx, V in enumerate([self.V1, self.V2, self.V3], start=1):
            result = self.mnw_alloc.allocate(V)
            self.assertTrue(result.status)

            A = result.A

            # Evaluate properties dynamically
            ef1_flag = is_ef1(V, A)
            efx_flag = is_efx(V, A)
            eq_flag = is_eq(V, A)
            po_flag = is_po(V, A)

            print("\n" + "=" * 70)
            print(f"MNW PROPERTY CHECK ({idx})")
            print("=" * 70 + "\n")
            print("Valuations:\n", V)
            print("Allocation Matrix (A):\n", A)
            print(f"EF1: {ef1_flag}")
            print(f"EFX: {efx_flag}")
            print(f"EQ: {eq_flag}")
            print(f"PO: {po_flag} \n")

            # Assert PO should always hold for MNW
            self.assertTrue(po_flag, "Expected MNW to always satisfy PO")



# ------------------------------------------------------------------------
#  Market Allocation Tests
# ------------------------------------------------------------------------

class TestMarketAllocation(TestAllocationMechanismsBase):
    """
    Tests for market-based allocation mechanism.
    """

    def setUp(self):
        """ Initialize market allocation mechanism. """
        self.market_alloc = MechanismMarketAllocation()

    def test_market_basic(self):
        """ Test if market allocation mechanism runs successfully. """
        for idx, V in enumerate([self.V1, self.V2, self.V3], start=1):
            result = self.market_alloc.allocate(V)
            self.assertTrue(result.status, f"Market allocation failed on V{idx}")

            A = result.A
            print("\n" + "=" * 70)
            print(f"MARKET BASIC TEST ({idx})")
            print("=" * 70 + "\n")
            print("Valuations:\n", V)
            print("Allocation Matrix (A):\n", A)

            self.check_allocation_validity(V, A)

    def test_market_ef1(self):
        """ Check if market allocation satisfies EF1. """
        for idx, V in enumerate([self.V1, self.V2, self.V3], start=1):
            result = self.market_alloc.allocate(V)
            A = result.A

            ef1_flag = is_ef1(V, A)
            print("\n" + "=" * 70)
            print(f"MARKET EF1 CHECK ({idx})")
            print("=" * 70 + "\n")
            print("Valuations:\n", V)
            print("Allocation Matrix (A):\n", A)
            print(f"EF1: {ef1_flag} (Expected: Uncertain)\n")

            self.assertTrue(ef1_flag, f"Market allocation did not satisfy EF1 on V{idx}")

    def test_market_po(self):
        """ Check if market allocation produces a Pareto optimal allocation. """
        for idx, V in enumerate([self.V1, self.V2, self.V3], start=1):
            result = self.market_alloc.allocate(V)
            A = result.A

            po_flag = is_po(V, A)
            print("\n" + "=" * 70)
            print(f"MARKET PO CHECK ({idx})")
            print("=" * 70 + "\n")
            print("Valuations:\n", V)
            print("Allocation Matrix (A):\n", A)
            print(f"PO: {po_flag} (Expected: True)\n")

            self.assertTrue(po_flag, f"Market allocation did not satisfy PO on V{idx}")

    def test_market_eq(self):
        """ Check if market allocation satisfies equitability. """
        for idx, V in enumerate([self.V1, self.V2, self.V3], start=1):
            result = self.market_alloc.allocate(V)
            A = result.A

            eq_flag = is_eq(V, A)
            print("\n" + "=" * 70)
            print(f"MARKET EQ CHECK ({idx})")
            print("=" * 70 + "\n")
            print("Valuations:\n", V)
            print("Allocation Matrix (A):\n", A)
            print(f"EQ: {eq_flag} (Expected: Uncertain)\n")

            # self.assertTrue(eq_flag, f"Market allocation did not satisfy EQ on V{idx}")
            print(f"Market Allocation EQ result on V{idx}: {eq_flag}")
            

    def test_market_nash_welfare(self):
        """ Check if market allocation achieves a high Nash welfare. """
        for idx, V in enumerate([self.V1, self.V2, self.V3], start=1):
            result = self.market_alloc.allocate(V)
            A = result.A

            nw_value, _ = nw(V, A)
            print("\n" + "=" * 70)
            print(f"MARKET NASH WELFARE CHECK ({idx})")
            print("=" * 70 + "\n")
            print("Valuations:\n", V)
            print("Allocation Matrix (A):\n", A)
            print(f"Nash Welfare: {nw_value}\n")

            self.assertGreater(nw_value, 0, f"Market allocation produced a non-positive Nash Welfare on V{idx}")


# ------------------------------------------------------------------------
#  Leximin Allocation Tests
# ------------------------------------------------------------------------

class TestLeximinAllocation(TestAllocationMechanismsBase):
    """
    Tests for Leximin allocation.
    """

    def setUp(self):
        """ Initialize leximin allocation mechanism. """
        self.leximin_alloc = MechanismLeximinAllocation()

    def test_leximin_basic(self):
        """ Test if Leximin mechanism runs successfully. """
        for idx, V in enumerate([self.V1, self.V2, self.V3], start=1):
            result = self.leximin_alloc.allocate(V)
            self.assertTrue(result.status, f"Leximin allocation failed on V{idx}")

            A = result.A
            print("\n" + "=" * 70)
            print(f"LEXIMIN BASIC TEST ({idx})")
            print("=" * 70 + "\n")
            print("Valuations:\n", V)
            print("Allocation Matrix (A):\n", A)

            self.check_allocation_validity(V, A)

    def test_leximin_ef1(self):
        """ Check if Leximin allocation satisfies EF1. """
        for idx, V in enumerate([self.V1, self.V2, self.V3], start=1):
            result = self.leximin_alloc.allocate(V)
            A = result.A

            ef1_flag = is_ef1(V, A)
            print("\n" + "=" * 70)
            print(f"LEXIMIN EF1 CHECK ({idx})")
            print("=" * 70 + "\n")
            print("Valuations:\n", V)
            print("Allocation Matrix (A):\n", A)
            print(f"EF1: {ef1_flag}\n")

            self.assertTrue(ef1_flag, f"Leximin allocation did not satisfy EF1 on V{idx}")

    def test_leximin_efx(self):
        """ Check if Leximin allocation satisfies EFX (Envy-Freeness up to any item). """
        for idx, V in enumerate([self.V1, self.V2, self.V3], start=1):
            result = self.leximin_alloc.allocate(V)
            A = result.A

            efx_flag = is_efx(V, A)
            print("\n" + "=" * 70)
            print(f"LEXIMIN EFX CHECK ({idx})")
            print("=" * 70 + "\n")
            print("Valuations:\n", V)
            print("Allocation Matrix (A):\n", A)
            print(f"EFX: {efx_flag}\n")

            print(f"Leximin Allocation EFX result on V{idx}: {efx_flag}")

    def test_leximin_po(self):
        """ Check if Leximin allocation produces a Pareto optimal allocation. """
        for idx, V in enumerate([self.V1, self.V2, self.V3], start=1):
            result = self.leximin_alloc.allocate(V)
            A = result.A

            po_flag = is_po(V, A)
            print("\n" + "=" * 70)
            print(f"LEXIMIN PO CHECK ({idx})")
            print("=" * 70 + "\n")
            print("Valuations:\n", V)
            print("Allocation Matrix (A):\n", A)
            print(f"PO: {po_flag}\n")

            self.assertTrue(po_flag, f"Leximin allocation did not satisfy PO on V{idx}")

    def test_leximin_eq(self):
        """ Check if Leximin allocation satisfies Equitability (EQ). """
        for idx, V in enumerate([self.V1, self.V2, self.V3], start=1):
            result = self.leximin_alloc.allocate(V)
            A = result.A

            eq_flag = is_eq(V, A)
            print("\n" + "=" * 70)
            print(f"LEXIMIN EQ CHECK ({idx})")
            print("=" * 70 + "\n")
            print("Valuations:\n", V)
            print("Allocation Matrix (A):\n", A)
            print(f"EQ: {eq_flag}\n")

            print(f"Leximin Allocation EQ result on V{idx}: {eq_flag}")

    def test_leximin_nash_welfare(self):
        """ Check if Leximin allocation achieves a high Nash welfare. """

        for idx, V in enumerate([self.V1, self.V2, self.V3], start=1):
            result = self.leximin_alloc.allocate(V)
            A = result.A

            nw_value, _ = nw(V, A)  # Extract only the Nash welfare value
            print("\n" + "=" * 70)
            print(f"LEXIMIN NASH WELFARE CHECK ({idx})")
            print("=" * 70 + "\n")
            print("Valuations:\n", V)
            print("Allocation Matrix (A):\n", A)
            print(f"Nash Welfare: {nw_value}\n")

            self.assertGreater(nw_value, 0, f"Leximin allocation produced a non-positive Nash Welfare on V{idx}")
 
 

# ------------------------------------------------------------------------
#  Market Equilibrium Allocation Tests (Fixed Version)
# ------------------------------------------------------------------------

class TestMarketEqAllocation(TestAllocationMechanismsBase):
    """
    Tests for Market Equilibrium allocation.
    """

    def setUp(self):
        """Initialize Market Equilibrium allocation mechanism."""
        self.market_eq_alloc = MechanismMarketEqAllocation()

    def test_market_eq_basic(self):
        """Test if Market Equilibrium mechanism runs successfully."""
        for idx, V in enumerate([self.V1, self.V2, self.V3], start=1):
            result = self.market_eq_alloc.allocate(V)
            self.assertTrue(result.status, f"Market Equilibrium allocation failed on V{idx}")

            A = result.A
            print(f"\n{'=' * 70}\nMARKET EQUILIBRIUM BASIC TEST ({idx})\n{'=' * 70}\n")
            print("Valuations:\n", V)
            print("Allocation Matrix (A):\n", A)

            self.check_allocation_validity(V, A)

    def test_market_eq_ef1(self):
        """Check if Market Equilibrium allocation satisfies EF1."""
        for idx, V in enumerate([self.V1, self.V2, self.V3], start=1):
            result = self.market_eq_alloc.allocate(V)
            A = result.A

            ef1_flag = is_ef1(V, A)
            print(f"\n{'=' * 70}\nMARKET EQUILIBRIUM EF1 CHECK ({idx})\n{'=' * 70}\n")
            print("Valuations:\n", V)
            print("Allocation Matrix (A):\n", A)
            print(f"EF1: {ef1_flag}\n")

            self.assertTrue(ef1_flag, f"Market Equilibrium allocation did not satisfy EF1 on V{idx}")

    def test_market_eq_efx(self):
        """Check if Market Equilibrium allocation satisfies EFX."""
        for idx, V in enumerate([self.V1, self.V2, self.V3], start=1):
            result = self.market_eq_alloc.allocate(V)
            A = result.A

            efx_flag = is_efx(V, A)
            print(f"\n{'=' * 70}\nMARKET EQUILIBRIUM EFX CHECK ({idx})\n{'=' * 70}\n")
            print("Valuations:\n", V)
            print("Allocation Matrix (A):\n", A)
            print(f"EFX: {efx_flag}\n")

    def test_market_eq_po(self):
        """Check if Market Equilibrium allocation produces a Pareto optimal allocation."""
        for idx, V in enumerate([self.V1, self.V2, self.V3], start=1):
            result = self.market_eq_alloc.allocate(V)
            A = result.A

            po_flag = is_po(V, A)
            print(f"\n{'=' * 70}\nMARKET EQUILIBRIUM PO CHECK ({idx})\n{'=' * 70}\n")
            print("Valuations:\n", V)
            print("Allocation Matrix (A):\n", A)
            print(f"PO: {po_flag}\n")

            self.assertTrue(po_flag, f"Market Equilibrium allocation did not satisfy PO on V{idx}")

    def test_market_eq_eq(self):
        """Check if Market Equilibrium allocation satisfies Equitability (EQ)."""
        for idx, V in enumerate([self.V1, self.V2, self.V3], start=1):
            result = self.market_eq_alloc.allocate(V)
            A = result.A

            eq_flag = is_eq(V, A)
            print(f"\n{'=' * 70}\nMARKET EQUILIBRIUM EQ CHECK ({idx})\n{'=' * 70}\n")
            print("Valuations:\n", V)
            print("Allocation Matrix (A):\n", A)
            print(f"EQ: {eq_flag}\n")

    def test_market_eq_nash_welfare(self):
        """Check if Market Equilibrium allocation achieves a high Nash welfare."""
        for idx, V in enumerate([self.V1, self.V2, self.V3], start=1):
            result = self.market_eq_alloc.allocate(V)
            A = result.A
            nw_value, _ = nw(V, A)
            print(f"\n{'=' * 70}\nMARKET EQUILIBRIUM NASH WELFARE CHECK ({idx})\n{'=' * 70}\n")
            print("Valuations:\n", V)
            print("Allocation Matrix (A):\n", A)
            print(f"Nash Welfare: {nw_value}\n")

            self.assertGreater(nw_value, 0, f"Market Equilibrium allocation produced a non-positive Nash Welfare on V{idx}")



# ------------------------------------------------------------------------
#  Maximum Nash Welfare Binary Allocation Tests (Fixed Version)
# ------------------------------------------------------------------------

class TestMaximumNashWelfareBinary(TestAllocationMechanismsBase):
    """
    Tests for Maximum Nash Welfare Binary allocation.
    """

    def setUp(self):
        """Initialize MNW Binary allocation mechanism."""
        self.mnw_binary_alloc = MechanismMaximumNashWelfareBinary()

    def test_mnw_binary_basic(self):
        """Test if MNW Binary mechanism runs successfully."""
        for idx, V in enumerate([self.V1, self.V2, self.V3], start=1):
            result = self.mnw_binary_alloc.allocate(V)
            self.assertTrue(result.status, f"MNW Binary allocation failed on V{idx}")

            A = result.A
            print(f"\n{'=' * 70}\nMNW BINARY BASIC TEST ({idx})\n{'=' * 70}\n")
            print("Valuations:\n", V)
            print("Allocation Matrix (A):\n", A)

            self.check_allocation_validity(V, A)

    def test_mnw_binary_ef1(self):
        """Check if MNW Binary allocation satisfies EF1."""
        for idx, V in enumerate([self.V1, self.V2, self.V3], start=1):
            result = self.mnw_binary_alloc.allocate(V)
            A = result.A

            ef1_flag = is_ef1(V, A)
            print(f"\n{'=' * 70}\nMNW BINARY EF1 CHECK ({idx})\n{'=' * 70}\n")
            print("Valuations:\n", V)
            print("Allocation Matrix (A):\n", A)
            print(f"EF1: {ef1_flag}\n")

            self.assertTrue(ef1_flag, f"MNW Binary allocation did not satisfy EF1 on V{idx}")

    def test_mnw_binary_efx(self):
        """Check if MNW Binary allocation satisfies EFX."""
        for idx, V in enumerate([self.V1, self.V2, self.V3], start=1):
            result = self.mnw_binary_alloc.allocate(V)
            A = result.A

            efx_flag = is_efx(V, A)
            print(f"\n{'=' * 70}\nMNW BINARY EFX CHECK ({idx})\n{'=' * 70}\n")
            print("Valuations:\n", V)
            print("Allocation Matrix (A):\n", A)
            print(f"EFX: {efx_flag}\n")

    def test_mnw_binary_po(self):
        """Check if MNW Binary allocation produces a Pareto optimal allocation."""
        for idx, V in enumerate([self.V1, self.V2, self.V3], start=1):
            result = self.mnw_binary_alloc.allocate(V)
            A = result.A

            po_flag = is_po(V, A)
            print(f"\n{'=' * 70}\nMNW BINARY PO CHECK ({idx})\n{'=' * 70}\n")
            print("Valuations:\n", V)
            print("Allocation Matrix (A):\n", A)
            print(f"PO: {po_flag}\n")

            self.assertTrue(po_flag, f"MNW Binary allocation did not satisfy PO on V{idx}")

    def test_mnw_binary_eq(self):
        """Check if MNW Binary allocation satisfies Equitability (EQ)."""
        for idx, V in enumerate([self.V1, self.V2, self.V3], start=1):
            result = self.mnw_binary_alloc.allocate(V)
            A = result.A

            eq_flag = is_eq(V, A)
            print(f"\n{'=' * 70}\nMNW BINARY EQ CHECK ({idx})\n{'=' * 70}\n")
            print("Valuations:\n", V)
            print("Allocation Matrix (A):\n", A)
            print(f"EQ: {eq_flag}\n")

    def test_mnw_binary_nash_welfare(self):
        """Check if MNW Binary allocation achieves a high Nash welfare."""

        for idx, V in enumerate([self.V1, self.V2, self.V3], start=1):
            result = self.mnw_binary_alloc.allocate(V)
            A = result.A

            nw_value, _ = nw(V, A)
            print(f"\n{'=' * 70}\nMNW BINARY NASH WELFARE CHECK ({idx})\n{'=' * 70}\n")
            print("Valuations:\n", V)
            print("Allocation Matrix (A):\n", A)
            print(f"Nash Welfare: {nw_value}\n")

            self.assertGreater(nw_value, 0, f"MNW Binary allocation produced a non-positive Nash Welfare on V{idx}")
