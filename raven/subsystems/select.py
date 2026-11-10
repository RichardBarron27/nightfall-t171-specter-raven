"""RAVEN-SELECT: Payload selection via DeepSeek R1 (AI decision), PRION (mutation), FOUNDRY (fallback)."""
import json
import logging
import shutil
import subprocess
import time
import httpx
from datetime import datetime

from ..models import (
    TargetMission,
    OrderedPayloadList,
    Payload,
    RavenPhase,
)
from ..gate import validate_gate_level, GateViolation

_OLLAMA_URL = "http://localhost:11434/api/generate"
_R1_MODEL = "deepseek-r1:32b"
_R1_TIMEOUT = 120.0


class SelectSubsystem:
    """RAVEN-SELECT subsystem — AI-driven payload selection engine."""

    def __init__(self, mission: TargetMission):
        self.mission = mission

    def execute(self) -> OrderedPayloadList:
        """Execute payload selection for STRIKE phase.

        Uses DeepSeek R1 for strategic decision making on payload prioritization,
        applies PRION GPU mutation for WAF evasion, falls back to FOUNDRY for novel exploits.

        Returns OrderedPayloadList with ranked payloads ready for STRIKE.

        Raises:
            GateViolation: If gate requirements not met
            Exception: If selection fails
        """
        try:
            validate_gate_level(self.mission.gate_level, "SELECT")
        except GateViolation as e:
            self.mission.halt(f"SELECT gate violation: {str(e)}")
            raise

        start_ms = int(time.time() * 1000)

        try:
            if not self.mission.vuln_matrix:
                self.mission.halt("No vulnerability matrix from ASSESS")
                raise Exception("Missing vulnerability matrix")

            payloads = self._call_deepseek_r1()

            if not payloads:
                self.mission.halt("No payloads selected")
                raise Exception("SELECT failed to generate payload list")

            # Apply PRION mutation for WAF evasion
            payloads = self._apply_prion_mutation(payloads)

            ordered = OrderedPayloadList(
                target_ip=self.mission.target_ip,
                phase=RavenPhase.SELECT,
                payloads=payloads,
                selected_at=datetime.now(),
            )

            self.mission.ordered_payloads = ordered
            self.mission.mark_phase_complete(RavenPhase.SELECT, int(time.time() * 1000) - start_ms)

            return ordered

        except Exception as e:
            self.mission.halt(f"SELECT failed: {str(e)}")
            raise

    def _call_deepseek_r1(self) -> list[Payload]:
        """Call DeepSeek R1 for strategic payload selection.

        DeepSeek R1 analyzes:
        - Available vulnerabilities ranked by CVSS
        - Service-specific exploitation vectors
        - Authentication requirements
        - Payload success probability
        - Lateral movement potential post-exploitation

        Returns list of Payload objects in priority order.
        Falls back to CVSS sort if Ollama unavailable.
        """
        if not self.mission.vuln_matrix:
            return []

        vulns = self.mission.vuln_matrix.sorted_by_cvss()

        # Build structured prompt for R1
        vuln_list = []
        for vuln in vulns[:10]:
            vuln_list.append(
                f"- {vuln.cve_id} | Service: {vuln.service} | CVSS: {vuln.cvss_score} | "
                f"Exploitable: {vuln.exploitable} | Requires Auth: {vuln.requires_auth}"
            )

        prompt = f"""You are a red team AI. Given the following vulnerabilities on target {self.mission.target_ip}, rank them by exploitation priority.

Vulnerabilities:
{chr(10).join(vuln_list)}

Return ONLY a JSON array of CVE IDs in priority order, highest priority first. Example:
["CVE-2024-37032", "CVE-2024-5483", "CVE-2024-5480"]

No explanation. No markdown. JSON array only."""

        try:
            client = httpx.Client(timeout=_R1_TIMEOUT)
            response = client.post(
                _OLLAMA_URL,
                json={"model": _R1_MODEL, "prompt": prompt, "stream": False},
            )
            response.raise_for_status()

            result = response.json()
            response_text = result.get("response", "").strip()

            # Parse R1's JSON array response
            try:
                cve_order = json.loads(response_text)
                if not isinstance(cve_order, list):
                    raise ValueError("R1 response not a JSON array")
            except (json.JSONDecodeError, ValueError) as e:
                logging.warning("R1 output not valid JSON, falling back to CVSS sort: %s", e)
                return self._fallback_cvss_sort(vulns)

            # Map R1's ranked CVE list back to Payload objects
            payloads = []
            for i, cve_id in enumerate(cve_order):
                vuln = next((v for v in vulns if v.cve_id == cve_id), None)
                if vuln is None:
                    logging.warning("R1 returned unknown CVE %s, skipping", cve_id)
                    continue

                payload = Payload(
                    payload_id=f"PAYLOAD-{i+1}",
                    name=f"Exploit {vuln.cve_id}",
                    description=f"Exploitation vector for {vuln.cve_id} (CVSS {vuln.cvss_score})",
                    type="exploit",
                    target_service=vuln.service,
                    target_cve=[vuln.cve_id],
                    delivery_method="http" if "http" in vuln.service.lower() else "ssh",
                    command=f"/opt/exploits/{vuln.cve_id}/exploit.sh",
                    args={
                        "target": self.mission.target_ip,
                        "port": self._get_service_port(vuln.service),
                        "cve": vuln.cve_id,
                    },
                )
                payloads.append(payload)

            # Store R1's reasoning in the ordered list
            self.mission.ordered_payloads = OrderedPayloadList(
                target_ip=self.mission.target_ip,
                phase=RavenPhase.SELECT,
                payloads=payloads,
                selected_at=datetime.now(),
                selection_logic=response_text,
            )

            return payloads if payloads else self._fallback_cvss_sort(vulns)

        except (httpx.ConnectError, httpx.TimeoutException) as e:
            logging.warning("R1 unavailable: %s — falling back to CVSS sort", e)
            return self._fallback_cvss_sort(vulns)
        except Exception as e:
            logging.warning("R1 call failed: %s — falling back to CVSS sort", e)
            return self._fallback_cvss_sort(vulns)

    def _fallback_cvss_sort(self, vulns: list) -> list[Payload]:
        """Fallback: sort by CVSS when R1 unavailable."""
        payloads = []
        for i, vuln in enumerate(vulns[:5]):
            payload = Payload(
                payload_id=f"PAYLOAD-{i+1}",
                name=f"Exploit {vuln.cve_id}",
                description=f"Exploitation vector for {vuln.cve_id} (CVSS {vuln.cvss_score})",
                type="exploit",
                target_service=vuln.service,
                target_cve=[vuln.cve_id],
                delivery_method="http" if "http" in vuln.service.lower() else "ssh",
                command=f"/opt/exploits/{vuln.cve_id}/exploit.sh",
                args={
                    "target": self.mission.target_ip,
                    "port": self._get_service_port(vuln.service),
                    "cve": vuln.cve_id,
                },
            )
            payloads.append(payload)

        # Mark fallback in mission state
        if hasattr(self.mission, 'ordered_payloads') and self.mission.ordered_payloads:
            self.mission.ordered_payloads.selection_logic = "FALLBACK: R1 unavailable — CVSS sort used"

        return payloads

    def _apply_prion_mutation(self, payloads: list[Payload]) -> list[Payload]:
        """Apply PRION GPU mutation to payloads for WAF evasion.

        Attempts to call specter-prion CLI for:
        - Encoding obfuscation (base64, hex, gzip)
        - Signature polymorphism
        - Request fragmentation
        - Timing randomization
        - Protocol-specific evasion (HTTP/SQL/etc)

        If PRION unavailable, returns payloads with mutated=False.
        Never simulates mutation.
        """
        if not shutil.which("specter-prion"):
            logging.warning("PRION not available — payloads returned unmodified")
            for payload in payloads:
                payload.mutated = False
                payload.mutation_method = ""
            return payloads

        for payload in payloads:
            if not payload.command:
                continue

            try:
                result = subprocess.run(
                    ["specter-prion", "mutate", "--payload", payload.command],
                    capture_output=True,
                    text=True,
                    timeout=30,
                )
                if result.returncode == 0 and result.stdout.strip():
                    payload.command = result.stdout.strip()
                    payload.mutated = True
                    payload.mutation_method = "PRION-GPU"
                else:
                    logging.warning(
                        "PRION mutation failed for %s: %s",
                        payload.payload_id,
                        result.stderr.strip(),
                    )
                    payload.mutated = False
                    payload.mutation_method = ""
            except subprocess.TimeoutExpired:
                logging.warning("PRION mutation timed out for %s", payload.payload_id)
                payload.mutated = False
                payload.mutation_method = ""
            except Exception as exc:
                logging.warning("PRION mutation error for %s: %s", payload.payload_id, exc)
                payload.mutated = False
                payload.mutation_method = ""

        return payloads

    def _get_service_port(self, service: str) -> int:
        """Get default port for service."""
        port_map = {
            "ssh": 22,
            "http": 80,
            "https": 443,
            "mysql": 3306,
            "postgresql": 5432,
        }
        return port_map.get(service.lower(), 80)
