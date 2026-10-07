import importlib.util
import pathlib
import sys
import unittest

import oci

MODULE_PATH = pathlib.Path(__file__).resolve().parents[1] / "monitor.py"
spec = importlib.util.spec_from_file_location("monitor", MODULE_PATH)
monitor = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules["monitor"] = monitor
spec.loader.exec_module(monitor)


class CapacityTests(unittest.TestCase):
    def test_available_when_available_count_positive(self):
        results = [
            monitor.CapacityResult(
                availability_domain="AD-1",
                fault_domain=None,
                status="AVAILABLE",
                available_count=1,
            )
        ]
        self.assertTrue(monitor.capacity_is_available(results))

    def test_available_when_count_unknown_but_status_available(self):
        results = [
            monitor.CapacityResult(
                availability_domain="AD-1",
                fault_domain=None,
                status="AVAILABLE",
                available_count=None,
            )
        ]
        self.assertTrue(monitor.capacity_is_available(results))

    def test_unavailable_when_count_zero(self):
        results = [
            monitor.CapacityResult(
                availability_domain="AD-1",
                fault_domain=None,
                status="AVAILABLE",
                available_count=0,
            )
        ]
        self.assertFalse(monitor.capacity_is_available(results))

    def test_unavailable_for_out_of_host_capacity(self):
        results = [
            monitor.CapacityResult(
                availability_domain="AD-1",
                fault_domain=None,
                status="OUT_OF_HOST_CAPACITY",
                available_count=0,
            )
        ]
        self.assertFalse(monitor.capacity_is_available(results))

    def test_oci_sdk_accepts_a1_flex_configuration(self):
        shape_config = oci.core.models.CapacityReportInstanceShapeConfig(
            ocpus=monitor.OCPUS,
            memory_in_gbs=monitor.MEMORY_GB,
            baseline_ocpu_utilization="BASELINE_1_1",
        )
        self.assertEqual(shape_config.ocpus, 1.0)
        self.assertEqual(shape_config.memory_in_gbs, 6.0)
        self.assertEqual(shape_config.baseline_ocpu_utilization, "BASELINE_1_1")


if __name__ == "__main__":
    unittest.main()
