from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.parse
import urllib.request
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import oci

REGION = "eu-madrid-1"
SHAPE = "VM.Standard.A1.Flex"
OCPUS = 1.0
MEMORY_GB = 6.0
STATE_FILE = Path(__file__).with_name("state.json")


@dataclass(frozen=True)
class CapacityResult:
    availability_domain: str
    fault_domain: str | None
    status: str
    available_count: int | None


def now_utc_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def load_state() -> dict[str, Any]:
    if not STATE_FILE.exists():
        return {"state": "UNKNOWN", "last_change_utc": None, "last_capacity": []}
    try:
        data = json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {"state": "UNKNOWN", "last_change_utc": None, "last_capacity": []}
    if not isinstance(data, dict):
        return {"state": "UNKNOWN", "last_change_utc": None, "last_capacity": []}
    return data


def save_state(state: str, results: list[CapacityResult]) -> None:
    previous = load_state()
    if previous.get("state") == state:
        return

    payload = {
        "state": state,
        "last_change_utc": now_utc_iso(),
        "last_capacity": [asdict(result) for result in results],
    }
    STATE_FILE.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def telegram_send(text: str) -> None:
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    chat_id = os.environ.get("TELEGRAM_CHAT_ID", "").strip()
    if not token or not chat_id:
        raise RuntimeError("Faltan TELEGRAM_BOT_TOKEN o TELEGRAM_CHAT_ID.")

    body = urllib.parse.urlencode(
        {
            "chat_id": chat_id,
            "text": text,
            "disable_web_page_preview": "true",
        }
    ).encode("utf-8")
    request = urllib.request.Request(
        f"https://api.telegram.org/bot{token}/sendMessage",
        data=body,
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=20) as response:
        payload = json.loads(response.read().decode("utf-8"))
    if not payload.get("ok"):
        raise RuntimeError(f"Telegram rechazó el mensaje: {payload}")


def get_oci_config() -> dict[str, str]:
    config_file = os.environ.get("OCI_CONFIG_FILE")
    if config_file:
        return oci.config.from_file(file_location=config_file)

    # Fallback estándar para ejecución local.
    return oci.config.from_file()


def query_capacity() -> list[CapacityResult]:
    config = get_oci_config()
    identity = oci.identity.IdentityClient(config)
    compute = oci.core.ComputeClient(config)

    tenancy_id = config["tenancy"]
    availability_domains = identity.list_availability_domains(tenancy_id).data
    if not availability_domains:
        raise RuntimeError("OCI no devolvió ningún Availability Domain.")

    results: list[CapacityResult] = []
    for availability_domain in availability_domains:
        details = oci.core.models.CreateComputeCapacityReportDetails(
            compartment_id=tenancy_id,
            availability_domain=availability_domain.name,
            shape_availabilities=[
                oci.core.models.CreateCapacityReportShapeAvailabilityDetails(
                    instance_shape=SHAPE,
                    instance_shape_config=oci.core.models.CapacityReportInstanceShapeConfig(
                        ocpus=OCPUS,
                        memory_in_gbs=MEMORY_GB,
                        baseline_ocpu_utilization="BASELINE_1_1",
                    ),
                )
            ],
        )

        report = compute.create_compute_capacity_report(details).data
        for item in report.shape_availabilities:
            results.append(
                CapacityResult(
                    availability_domain=availability_domain.name,
                    fault_domain=getattr(item, "fault_domain", None),
                    status=str(item.availability_status),
                    available_count=getattr(item, "available_count", None),
                )
            )

    return results


def capacity_is_available(results: list[CapacityResult]) -> bool:
    return any(
        result.status == "AVAILABLE"
        and (result.available_count is None or result.available_count > 0)
        for result in results
    )


def availability_message(results: list[CapacityResult]) -> str:
    available = [
        result
        for result in results
        if result.status == "AVAILABLE"
        and (result.available_count is None or result.available_count > 0)
    ]
    best = available[0]
    count_text = (
        "al menos una instancia"
        if best.available_count is None
        else f"{best.available_count} instancia(s)"
    )
    return (
        "🚨 ORACLE A1.FLEX DISPONIBLE\n\n"
        f"Región: Spain Central (Madrid) · {REGION}\n"
        f"Shape: {SHAPE}\n"
        f"Configuración buscada: {int(OCPUS)} OCPU / {int(MEMORY_GB)} GB RAM\n"
        f"Availability Domain: {best.availability_domain}\n"
        f"Capacidad reportada: {count_text}\n\n"
        "Entra ahora en Oracle Cloud → Resource Manager → tu pila → Apply.\n"
        "El informe no reserva capacidad, así que conviene intentarlo cuanto antes."
    )


def run_check(send_test: bool = False) -> int:
    previous = load_state()
    previous_state = str(previous.get("state", "UNKNOWN"))

    if send_test:
        telegram_send(
            "✅ Prueba correcta: el monitor de Oracle A1.Flex está conectado a Telegram."
        )

    try:
        results = query_capacity()
    except Exception as exc:
        # Una avería del monitor no debe parecer una falta de capacidad.
        if previous_state != "ERROR":
            try:
                telegram_send(
                    "⚠️ El comprobador de Oracle no ha podido consultar la capacidad. "
                    "Revisa GitHub Actions. No significa que A1.Flex siga sin capacidad."
                )
            except Exception as telegram_exc:
                print(
                    f"No se pudo enviar la alerta de error a Telegram: {telegram_exc}",
                    file=sys.stderr,
                )
        save_state("ERROR", [])
        print(f"ERROR consultando OCI: {exc}", file=sys.stderr)
        return 2

    current_state = "AVAILABLE" if capacity_is_available(results) else "UNAVAILABLE"

    print(
        json.dumps(
            {
                "region": REGION,
                "shape": SHAPE,
                "ocpus": OCPUS,
                "memory_gb": MEMORY_GB,
                "state": current_state,
                "capacity": [asdict(result) for result in results],
            },
            indent=2,
            ensure_ascii=False,
        )
    )

    # Solo avisamos en la transición a AVAILABLE para evitar spam.
    if current_state == "AVAILABLE" and previous_state != "AVAILABLE":
        telegram_send(availability_message(results))

    save_state(current_state, results)
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Comprueba capacidad Oracle A1.Flex y avisa por Telegram."
    )
    parser.add_argument(
        "--send-test",
        action="store_true",
        help="Envía además un mensaje de prueba a Telegram.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    raise SystemExit(run_check(send_test=args.send_test))
