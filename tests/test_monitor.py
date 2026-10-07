import importlib.util
import pathlib
import sys
import types
import unittest

# Las funciones puras del monitor se pueden probar sin llamar a OCI.
# Si el SDK no está instalado localmente, creamos un módulo mínimo para importar el archivo.
try:
    import oci  # noqa: F401
except ImportError:
    sys.modules["oci"] = types.SimpleNamespace()

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


if __name__ == "__main__":
    unittest.main()
