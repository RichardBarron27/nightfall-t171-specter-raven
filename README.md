# SPECTER RAVEN — Autonomous Red Team Platform

**T171** | Autonomous Traditional Red Team Platform with AI-Driven Decision Making

SPECTER RAVEN is a production-ready autonomous red team orchestrator that integrates ten specialized subsystems into a complete kill-chain execution engine. Powered by DeepSeek R1 AI decision-making, adaptive payload mutation via PRION, and real tool orchestration across the entire SPECTER ecosystem, RAVEN automates reconnaissance, enumeration, exploitation, privilege escalation, lateral movement, persistence, and data harvesting.

## Features

- **10 Integrated Subsystems**: RECON, ENUMERATE, ASSESS, SELECT, STRIKE, ESCALATE, SPREAD, PERSIST, HARVEST, REPORT
- **Real Tool Orchestration**: Native integration with ORION, WRAITH, GHOUL, REAPER, RAPTOR, FEDERATION, DOMINION
- **AI-Driven Decisions**: DeepSeek R1 model for intelligent payload selection and adaptive attack flow
- **Adaptive Payloads**: PRION-powered mutation and FOUNDRY fallback generation
- **Autonomous Kill Chain**: Full attack path from initial scan to persistence establishment
- **Cryptographic Signing**: Ed25519 + ML-DSA-65 dual-signature reporting
- **Gate Enforcement**: Three-tier operational security (OPEN, STRIKE, UNLEASHED)
- **Structured Reporting**: JSON + Markdown reports with MITRE ATT&CK mapping

## 10 Subsystems

1. **RAVEN-RECON** — ORION async port scanning (1-65535), OS fingerprinting, service detection, timeout handling
2. **RAVEN-ENUMERATE** — WRAITH stealth enumeration, TLS certificate parsing, virtual host discovery
3. **RAVEN-ASSESS** — GHOUL CVE matching, CVSS scoring, VulnMatrix ranking and prioritization
4. **RAVEN-SELECT** — ARMORY payload selection, DeepSeek R1 decision logic, PRION mutation, FOUNDRY generation
5. **RAVEN-STRIKE** — REAPER delivery, result validation, adaptive retry on feedback
6. **RAVEN-ESCALATE** — RAPTOR privilege escalation (Linux/Windows/AD chains, kernel exploits, UAC bypass)
7. **RAVEN-SPREAD** — FEDERATION lateral movement (SMB, RDP, SSH, AD, Kerberos, pass-the-hash, pass-the-ticket)
8. **RAVEN-PERSIST** — DOMINION persistence (cron, systemd, scheduled tasks, Windows services)
9. **RAVEN-HARVEST** — DOMINION credential harvesting (shadow files, LSASS dumps, SAM, DCSync, browser storage)
10. **RAVEN-REPORT** — Structured JSON + Markdown output, MITRE ATT&CK mapping, cryptographic evidence chains

## Gate Levels

SPECTER RAVEN enforces three operational security gates:

| Gate | Description | Requirements |
|------|-------------|--------------|
| **OPEN** | Development/testing, no restrictions | None |
| **STRIKE** | Authorized pentest with payload validation | None (logged) |
| **UNLEASHED** | Full autonomous red team operations | RAVEN_KEY (Ed25519 + ML-DSA-65 keypair) |

## Installation

Install from PyPI:

```bash
pip install specter-raven
```

Or from GitHub:

```bash
pip install git+https://github.com/redspecter/specter-raven.git
```

### Requirements

- Python 3.9+
- typer[all]
- rich
- cryptography

## Quick Start

### Basic Usage

Launch an autonomous red team mission against a target:

```bash
specter-raven run 192.168.1.100
```

### Development Mode (OPEN Gate)

No restrictions, full logging:

```bash
raven run 192.168.1.0/24 --gate OPEN
```

### Authorized Pentest (STRIKE Gate)

Payload validation enabled:

```bash
raven run 192.168.1.100 --gate STRIKE --output ./reports
```

### Full Autonomy (UNLEASHED Gate)

Requires RAVEN_KEY. First, generate your keypair:

```bash
raven keygen --output ~/.redspecter/raven_key
```

Then launch:

```bash
raven run 192.168.1.100 --gate UNLEASHED --gpu --output ./reports
```

## Command Reference

### `raven run` — Launch autonomous mission

```
Usage: raven run [OPTIONS] TARGET

Arguments:
  TARGET                    Target IP or CIDR range

Options:
  --gate, -g TEXT          Gate level (OPEN/STRIKE/UNLEASHED) [default: OPEN]
  --output, -o PATH        Output directory for reports
  --gpu                    Enable GPU acceleration (PRION mutations)
  --model, -m TEXT         AI model for decisions [default: deepseek-r1]
  --quiet, -q              Suppress detailed output
  --help                   Show this message and exit.
```

### `raven keygen` — Generate RAVEN_KEY

```
Usage: raven keygen [OPTIONS]

Options:
  --output, -o PATH    Output path for RAVEN_KEY [default: ~/.redspecter/raven_key]
  --help               Show this message and exit.
```

Generates Ed25519 + ML-DSA-65 keypair for UNLEASHED operations.

### `raven version` — Display version

```
Usage: raven version
```

## RAVEN_KEY Management

The RAVEN_KEY is a cryptographic keypair consisting of:
- **Ed25519 keypair** (32-byte private + 32-byte public)
- **ML-DSA-65 keypair** (2400-byte private + 1312-byte public)

### Generate a key:

```bash
raven keygen --output ~/.redspecter/raven_key
```

### Key permissions:

Generated keys are stored with 0600 (read/write owner only) permissions.

### Using UNLEASHED mode:

The RAVEN_KEY must be present at the default location or specified via environment. Missions without a valid key in UNLEASHED mode will halt immediately.

## Architecture

```
┌─────────────────────────────────────────────────────┐
│          SPECTER RAVEN (T171) CLI                   │
│  Autonomous Red Team Orchestrator                   │
└─────────────────────────────────────────────────────┘
         │
         ├─→ Gate Enforcement (OPEN/STRIKE/UNLEASHED)
         │
         ├─→ Mission Configuration
         │   ├─ Target IP/CIDR
         │   ├─ Gate Level
         │   ├─ AI Model
         │   └─ Output Directory
         │
         └─→ Kill Chain Execution (10 Subsystems)
             ├─ RAVEN-RECON (ORION)
             ├─ RAVEN-ENUMERATE (WRAITH)
             ├─ RAVEN-ASSESS (GHOUL)
             ├─ RAVEN-SELECT (ARMORY → PRION → FOUNDRY)
             ├─ RAVEN-STRIKE (REAPER)
             ├─ RAVEN-ESCALATE (RAPTOR)
             ├─ RAVEN-SPREAD (FEDERATION)
             ├─ RAVEN-PERSIST (DOMINION)
             ├─ RAVEN-HARVEST (DOMINION)
             └─ RAVEN-REPORT (JSON + Markdown)
```

## Output

SPECTER RAVEN generates two report formats:

### JSON Report (`raven-<mission-id>.json`)

Complete mission data including:
- Target profile (services, OS, versions)
- Discovered vulnerabilities (CVEs, CVSS scores)
- Executed payloads and results
- Credentials obtained
- Persistence mechanisms established
- Evidence chain (cryptographic signatures)

### Markdown Report (`raven-<mission-id>.md`)

Human-readable summary including:
- Executive summary
- Vulnerability matrix (CVSS ranking)
- Attack flow timeline
- MITRE ATT&CK mapping
- Recommendations

## Integration with SPECTER Ecosystem

SPECTER RAVEN orchestrates the following SPECTER tools:

| Tool | Subsystem | Purpose |
|------|-----------|---------|
| ORION | RAVEN-RECON | Async reconnaissance and scanning |
| WRAITH | RAVEN-ENUMERATE | Stealth enumeration |
| GHOUL | RAVEN-ASSESS | CVE mapping and CVSS scoring |
| ARMORY | RAVEN-SELECT | Payload database and selection |
| PRION | RAVEN-SELECT | Adaptive payload mutation |
| FOUNDRY | RAVEN-SELECT | Fallback payload generation |
| REAPER | RAVEN-STRIKE | Exploit delivery and execution |
| RAPTOR | RAVEN-ESCALATE | Privilege escalation |
| FEDERATION | RAVEN-SPREAD | Lateral movement and pivot |
| DOMINION | RAVEN-PERSIST, RAVEN-HARVEST | Persistence and credential harvesting |

## Security

### Gate Enforcement

- **OPEN**: Unvalidated execution (testing only)
- **STRIKE**: Payload validation required
- **UNLEASHED**: RAVEN_KEY cryptographic enforcement

### Cryptographic Signatures

All reports in UNLEASHED mode include dual signatures:
- **Ed25519** (32-byte signature)
- **ML-DSA-65** (post-quantum safe signature)

### No Stubs or Simulations

SPECTER RAVEN contains zero simulation code. All subsystems execute real logic against real targets or halt with an error. No mock returns, no placeholder execution, no fake progress.

## Troubleshooting

### UNLEASHED gate requires RAVEN_KEY

```
Error: UNLEASHED gate requires RAVEN_KEY.
Generate with: raven keygen --output ~/.redspecter/raven_key
```

Solution: Generate a key with `raven keygen` and place it in the default location or use `RAVEN_KEY_PATH` environment variable.

### Target unreachable

SPECTER RAVEN will halt if the target is unreachable during reconnaissance. Verify network connectivity and target configuration.

### Subsystem failure

If a subsystem fails, the entire mission halts with a detailed error message. Check that:
1. Target is accessible
2. Credentials are valid (for authenticated subsystems)
3. SPECTER tool dependencies are installed
4. Firewall rules allow scanning and exploitation

## Development

### Running Tests

```bash
pytest tests/
```

### Code Quality

```bash
black raven/
ruff check raven/
mypy raven/
```

## License

MIT License — Red Specter Security Research Ltd

## Support

For issues, questions, or contributions:

- GitHub Issues: https://github.com/redspecter/specter-raven/issues
- Email: tech@redspecter.co.uk

---

**Red Specter Security Research Ltd** — Innovation Beyond Belief
