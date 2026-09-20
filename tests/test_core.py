import unittest

from core.automaton import LAMBDA, Automaton
from core.simulator import TapeSimulator
from core.subset_construction import subset_construction
from core.validator import ConsistencyValidator


def afd_ends_in_b():
    """AFD: cadenas sobre {a,b} que terminan en b."""
    m = Automaton()
    m.alphabet = {"a", "b"}
    m.states = {"q0", "q1"}
    m.initial_state = "q0"
    m.final_states = {"q1"}
    m.add_transition("q0", "a", "q0")
    m.add_transition("q0", "b", "q1")
    m.add_transition("q1", "a", "q0")
    m.add_transition("q1", "b", "q1")
    return m


def afn_lambda_example():
    """AFN-lambda: (a|b)*abb, ejemplo clasico de subconjuntos."""
    m = Automaton()
    m.alphabet = {"a", "b"}
    m.states = {"q0", "q1", "q2", "q3"}
    m.initial_state = "q0"
    m.final_states = {"q3"}
    m.add_transition("q0", "a", "q0")
    m.add_transition("q0", "b", "q0")
    m.add_transition("q0", "a", "q1")
    m.add_transition("q1", "b", "q2")
    m.add_transition("q2", "b", "q3")
    return m


class TestAutomaton(unittest.TestCase):
    def test_is_deterministic(self):
        m = afd_ends_in_b()
        self.assertTrue(m.is_deterministic())
        self.assertEqual(m.kind(), "AFD")

    def test_accepts_afd(self):
        m = afd_ends_in_b()
        self.assertTrue(m.accepts("aabab")[0])
        self.assertFalse(m.accepts("aaba")[0])

    def test_accepts_afn(self):
        m = afn_lambda_example()
        self.assertFalse(m.is_deterministic())
        accepted, trace = m.accepts("aabb")
        self.assertTrue(accepted)
        self.assertFalse(m.accepts("aab")[0])

    def test_lambda_detection(self):
        m = Automaton()
        m.states = {"q0", "q1"}
        m.initial_state = "q0"
        m.final_states = {"q1"}
        m.add_transition("q0", LAMBDA, "q1")
        self.assertTrue(m.has_lambda)
        self.assertEqual(m.kind(), "AFN-lambda")

    def test_persistence_roundtrip(self):
        m = afd_ends_in_b()
        data = m.to_dict()
        m2 = Automaton.from_dict(data)
        self.assertEqual(m.states, m2.states)
        self.assertEqual(m.transitions, m2.transitions)
        self.assertEqual(m.accepts("aabab"), m2.accepts("aabab"))


class TestSubsetConstruction(unittest.TestCase):
    def test_conversion_preserves_language(self):
        nfa = afn_lambda_example()
        dfa = subset_construction(nfa)
        self.assertTrue(dfa.is_deterministic())
        for word in ["ab", "abb", "aabb", "babb", "", "a", "bbb"]:
            self.assertEqual(
                nfa.accepts(word)[0], dfa.accepts(word)[0], msg=f"word={word!r}"
            )


class TestValidator(unittest.TestCase):
    def test_valid_afd(self):
        m = afd_ends_in_b()
        report = ConsistencyValidator(m).run_all()
        self.assertTrue(report.is_valid)

    def test_missing_initial_state(self):
        m = afd_ends_in_b()
        m.initial_state = None
        report = ConsistencyValidator(m).run_all()
        self.assertFalse(report.is_valid)

    def test_unreachable_state_warning(self):
        m = afd_ends_in_b()
        m.states.add("q2")
        report = ConsistencyValidator(m).run_all()
        self.assertTrue(report.is_valid)
        self.assertTrue(any("no alcanzables" in w for w in report.warnings))

    def test_incomplete_afd_warning(self):
        m = afd_ends_in_b()
        del m.transitions[("q1", "b")]
        report = ConsistencyValidator(m).run_all()
        self.assertTrue(any("no total" in w for w in report.warnings))


class TestTapeSimulator(unittest.TestCase):
    def test_step_by_step_matches_accepts(self):
        m = afd_ends_in_b()
        sim = TapeSimulator(m, "aabab")
        frames = sim.run_to_end()
        self.assertTrue(frames[-1].finished)
        self.assertTrue(frames[-1].accepted)
        accepted, trace = m.accepts("aabab")
        self.assertEqual(len(frames), len(trace))


if __name__ == "__main__":
    unittest.main()
