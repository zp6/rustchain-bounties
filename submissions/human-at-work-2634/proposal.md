# Bring Your Human to Work Day — Technical Proposal

## Bounty #2634 | 500 RTC Pool

## 1. Human Verification Mechanism

### 1.1 Hardware Attestation (WebAuthn / FIDO2)

Each human operator must register a hardware security key:

```
Registration Flow:
1. User initiates registration on RustChain portal
2. Browser generates WebAuthn challenge
3. Security key signs challenge (YubiKey, TPM, etc.)
4. Attestation certificate stored on-chain (hash only)
5. Credential ID bound to wallet address
```

**Benefits:**
- Cryptographic proof of physical presence
- Resistant to phishing and replay attacks
- No personal data required — only device attestation

**Implementation:**
- Use `webauthn` crate for Rust server-side verification
- Client-side: standard WebAuthn API (supported in all modern browsers)
- Store only `credential_id_hash` + `attestation_hash` on-chain

### 1.2 Social Verification (GitHub Graph)

To prevent fresh accounts from farming bounties:

| Requirement | Threshold |
|-------------|-----------|
| Account age | ≥ 6 months |
| Public contributions | ≥ 10 commits |
| Followers | ≥ 3 (reduces bot clusters) |
| Repositories | ≥ 2 public repos |

**Verification flow:**
1. OAuth via GitHub App (read-only: public profile + contribution data)
2. Server validates thresholds
3. GitHub ID hashed and stored as verification record

### 1.3 Identity Binding

One-time binding ceremony:
```
wallet_address + github_id_hash → commitment_hash
```
This prevents one human from registering multiple identities. The commitment is stored on-chain and checked against new registrations.

---

## 2. Agent Activity Tracking

### 2.1 Contribution Fingerprinting

Each PR/submission is analyzed across multiple dimensions:

```rust
struct ContributionFingerprint {
    diff_complexity: f64,      // Lines changed, files touched, AST depth
    code_originality: f64,     // Similarity vs. known templates/LLM outputs
    review_engagement: f64,    // Responses to reviewer comments
    time_to_complete: f64,     // From issue claim to PR submission
    commit_pattern: f64,       // Natural vs. batch commit patterns
}
```

### 2.2 Frequency Scoring

```
FrequencyScore {
    submissions_per_day: float,
    submissions_per_week: float,
    burst_ratio: float,           // Max 24h submissions / avg 24h submissions
    consistency_score: float,     // Regularity of contribution cadence
}
```

**Burst detection:** If a contributor submits >5 PRs in 24 hours after weeks of inactivity, this triggers a review flag.

### 2.3 Quality Score

Composite metric:
```
quality = 0.3 * merge_rate 
        + 0.2 * review_positive_rate 
        + 0.2 * code_originality 
        + 0.15 * diff_complexity 
        + 0.15 * test_coverage_delta
```

Where:
- `merge_rate` = merged PRs / total PRs
- `review_positive_rate` = positive review comments / total review interactions
- `code_originality` = 1 - similarity_to_templates
- `diff_complexity` = normalized (lines_changed * files_touched * ast_depth)
- `test_coverage_delta` = change in test coverage from PR

---

## 3. Matching Algorithm

### 3.1 Core Concept

Compare **human-verified activity** against **agent submission patterns** to detect:
- One human operating multiple agents
- Template/boilerplate submissions
- Coordinated farming campaigns

### 3.2 Algorithm Steps

```
1. Cluster submissions by similarity (code style, timing, content)
2. For each cluster, check human verification records
3. If multiple agents share one verified human → flag as sybil
4. Compute trust_score for each agent-human pair
5. Weight bounty payouts by trust_score
```

### 3.3 Trust Score Formula

```
trust_score = w1 * human_verification_score
            + w2 * contribution_quality_score
            + w3 * frequency_normalcy_score
            + w4 * social_graph_strength

Default weights: w1=0.35, w2=0.30, w3=0.20, w4=0.15
```

### 3.4 Anomaly Detection

| Signal | Threshold | Action |
|--------|-----------|--------|
| Submissions from same IP/region | >3 agents | Flag for review |
| Similar code structure (cosine sim) | >0.85 | Auto-merge check |
| Identical commit timestamps | Within 60s | Sybil alert |
| Shared wallet funding | Common source | Investigation |

---

## 4. Implementation Roadmap

### Phase 1: Foundation (Weeks 1-2)
- [ ] WebAuthn registration flow
- [ ] GitHub OAuth integration
- [ ] Identity binding smart contract
- [ ] Database schema for verification records

### Phase 2: Tracking (Weeks 3-4)
- [ ] PR analysis pipeline (diff parsing, AST analysis)
- [ ] Frequency scoring service
- [ ] Quality score calculator
- [ ] Contribution fingerprint storage

### Phase 3: Matching (Weeks 5-6)
- [ ] Similarity clustering (DBSCAN on code embeddings)
- [ ] Trust score computation
- [ ] Anomaly detection rules engine
- [ ] Dashboard for maintainers

### Phase 4: Integration (Weeks 7-8)
- [ ] Bounty payout weighting by trust score
- [ ] Alert system for sybil patterns
- [ ] Public audit API
- [ ] Documentation and open-sourcing

---

## 5. Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Sybil detection rate | >80% | Known sybil accounts correctly flagged |
| False positive rate | <5% | Legitimate contributors incorrectly flagged |
| Verification completion | >70% | Bounty claimants who complete verification |
| Agent quality improvement | +30% | Average quality score post-launch vs pre-launch |
| Time to verify | <5 min | End-to-end human verification flow |

---

## 6. Security Considerations

- **No personal data stored** — only cryptographic hashes and commitments
- **Hardware keys are non-transferable** — prevents account selling
- **Social graph checks are one-time** — no ongoing data access
- **All scoring is deterministic and auditable** — no hidden weights
- **Appeal process** — flagged contributors can request manual review

## 7. Open Source Commitment

All code will be MIT-licensed and contributed back to the RustChain ecosystem. The matching algorithm reference implementation is included in this submission.
