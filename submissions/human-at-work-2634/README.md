# Bring Your Human to Work Day — Bounty #2634

> **Bounty:** 500 RTC Pool  
> **Submitter:** zp6  
> **Wallet:** zp6  
> **Date:** 2025-05-15

## Overview

This proposal addresses the challenge of **matching Agent participation metrics with real-human verification** in the RustChain bounty ecosystem. As AI agents increasingly contribute to open-source projects, we need a robust system that:

1. **Verifies human identity** behind agent-driven contributions
2. **Tracks agent activity** with granular quality metrics
3. **Correlates human engagement with agent output** to ensure fair bounty distribution

## Problem Statement

RustChain bounties attract both human and AI-agent contributors. Without a verification layer:

- **Sybil attacks:** One human can operate multiple agents to farm bounties
- **Quality dilution:** Unverified agents may submit low-quality, templated work
- **Fairness:** Genuine human contributors may be crowded out by automated submissions

## Proposed Solution

A three-layer system:

### Layer 1: Human Verification
- **Hardware attestation** via WebAuthn/FIDO2 (YubiKey, TPM)
- **Social graph verification** — link a GitHub account with ≥6-month history and ≥10 public contributions
- **One-time KYC-lite** — wallet + GitHub identity binding (no personal data stored, only hash commitments)

### Layer 2: Agent Activity Tracking
- **Contribution fingerprinting** — each PR is analyzed for: code originality, diff complexity, review engagement
- **Frequency scoring** — submissions per day/week with burst detection
- **Quality score** — based on PR merge rate, review feedback, code reuse metrics

### Layer 3: Matching Algorithm
- Compare human-verified activity patterns against agent submission patterns
- Flag anomalies (e.g., one human with 10 agents submitting similar content)
- Produce a **trust score** (0–1) that weights bounty payouts

## Files

| File | Description |
|------|-------------|
| `proposal.md` | Detailed technical proposal |
| `match_algorithm.py` | Reference implementation of the matching algorithm |

## Quick Start

```bash
# Run the matching algorithm prototype
python3 submissions/human-at-work-2634/match_algorithm.py
```

## Expected Impact

- **Reduce sybil farming** by 80%+ through human verification
- **Maintain agent contribution quality** via activity tracking
- **Fair bounty distribution** weighted by trust scores
- **Transparent** — all scoring is open-source and auditable
