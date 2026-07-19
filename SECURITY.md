# Security Policy

VitaGraph is a research/education reference implementation that operates
exclusively on **synthetic, seeded random data**. It is not a medical
device and processes no real patient data by design. That said, we take
the security of the codebase, its supply chain, and its users seriously,
and we welcome responsible disclosure of any vulnerability.

## Supported Versions

We follow [Semantic Versioning](https://semver.org/). Security fixes are
backported on a best-effort basis to the versions below.

| Version | Supported          | Notes                          |
| ------- | ------------------ | ------------------------------- |
| 0.2.x   | :white_check_mark: | Active development branch       |
| 0.1.x   | :white_check_mark: | Critical fixes only             |
| < 0.1   | :x:                 | Pre-release, no longer supported |

Once VitaGraph reaches `1.0.0`, this table will be updated to track the
current and previous major release lines.

## Reporting a Vulnerability

**Please do not open a public GitHub issue for security vulnerabilities.**

Instead, use one of the following private channels:

1. **GitHub Security Advisories (preferred):** open a report via the
   repository's [Security tab → "Report a vulnerability"](../../security/advisories/new).
   This creates a private discussion thread with maintainers and lets us
   coordinate a fix and a CVE (if warranted) before public disclosure.
2. **Email:** send details to the maintainer contact listed in
   [`pyproject.toml`](pyproject.toml) / the GitHub profile of
   [`@Ciprian-LocalPulse`](https://github.com/Ciprian-LocalPulse). Please
   include `[SECURITY]` in the subject line.

### What to include in a report

- A description of the vulnerability and its potential impact.
- Step-by-step reproduction instructions or a minimal proof-of-concept.
- The affected version(s) / commit hash.
- Any suggested remediation, if you have one.

### What to expect

| Stage                       | Target timeline            |
| ---------------------------- | --------------------------- |
| Acknowledgement of report     | Within 3 business days      |
| Initial triage & severity     | Within 7 business days      |
| Fix or mitigation plan shared | Within 30 days (severity-dependent) |
| Public disclosure / advisory  | Coordinated with reporter, typically after a fix is released |

We ask reporters to give us a reasonable window to ship a fix before any
public disclosure, and we commit to crediting reporters (unless they
prefer to remain anonymous) in the release notes and/or security advisory.

## Scope

In scope:

- The `vitagraph` Python package (`src/vitagraph/`) and its CLI.
- The project's GitHub Actions workflows and CI/CD supply chain.
- The `Dockerfile` / `docker-compose.yml` runtime images.
- Documentation that could mislead users into unsafe usage (e.g.
  suggesting synthetic outputs are clinically valid).

Out of scope:

- Vulnerabilities in third-party dependencies (please report those
  upstream; we will track and update via Dependabot once a fix is
  available). If a dependency vulnerability is actively exploitable
  through VitaGraph's default usage, please still let us know.
- Denial-of-service reports that rely on unbounded local resource
  consumption in a research tool run intentionally by its own operator.

## Automated Security Tooling

This repository additionally uses:

- **CodeQL** static analysis on every push/PR and weekly on a schedule
  (`.github/workflows/codeql.yml`).
- **Dependabot** for automated dependency and GitHub Actions update PRs
  (`.github/dependabot.yml`).
- **Dependency Review** on pull requests to flag newly introduced
  vulnerable or license-incompatible dependencies.

## Disclaimer

VitaGraph produces synthetic biological-age estimates for research and
educational purposes only. See the [README](README.md#-important-disclaimer)
and [`docs/METHODOLOGY.md`](docs/METHODOLOGY.md) for the full scope
statement. Misuse of synthetic outputs as real medical guidance is a
safety concern we take as seriously as code-level vulnerabilities;
please report misleading claims in the docs the same way you would
report a bug.
