# T-ASE H6 — Independent Published-Net Embedding Design

Status: `DESIGN / IMPLEMENT ON JOURNAL-HARDENING WORKTREE`
Date: 2026-08-19
Worktree: `D:\worktree\IMS_deadlock-journal-hardening-v1`
Branch: `codex/journal-hardening-v1`
Feeds: G-H6, Proposition 4 field 4, Table I L31 cell
Does not overwrite: `evidence/tase_hardening/h5/`, any G4/G5 hash, H1–H4 cases

This spec is the hashed authorization for H6 science. It does not
authorize shop-floor claims, SBA, CRP candidate generation, or a
general IMS \(\equiv\) S3PR isomorphism.

## 0. Scientific obligation

H5 scored Proposition 4’s four fields on six subjects and refused
field 4 on every row with

```text
field4_reason = no_independent_s4pr_embedding
bridge_agreement = false
```

That refusal is scientifically correct and frozen. H6 does **not**
repair H5 in place. H6 builds a *new* subject whose Petri encoding is
taken from a published S3PR, writes an independently hashed embedding
certificate, and then scores the same four fields. After H6, a missing
embedding is no longer the reason field 4 is undecided.

Two rows are required:

| Row | Intent |
| --- | --- |
| H6-A | Faithful embedding of the published net. Field 4 is `true` iff the certificate verifies. Fields 1–3 are reported honestly (agreement may still be false). |
| H6-B | Same net after a *declared* IMS-only distortion (an AGV token that the source net does not contain). Field 4 is `false` with a typed reason, or fields 1–3 change, or both. |

A reviewer must be able to open H6-A and check

```text
locator → incidence matrix → map ι → four hashes → four fields
```

without trusting a chat summary.

## 1. Source object (H6-A)

**Citation (locator L01 / Ezpeleta 1995).**
J. Ezpeleta, J. M. Colom, and J. Martínez, “A Petri net based deadlock
prevention policy for flexible manufacturing systems,” *IEEE Trans.
Robot. Autom.*, vol. 11, no. 2, pp. 173–184, Apr. 1995.
DOI: `10.1109/70.370500`.

**Object, stated without over-claim.** H6-A is *not* a reconstruction
of Ezpeleta Figure 1 (the three-machine / two-robot FMS). It is the
smallest deadlock-prone S3PR admitted by that paper’s S3PR definition:
two sequential processes sharing two unit-capacity resource places.
Every later S3PR/S4PR paper uses this circular pair as the definitional
core. The incidence matrix below is the source of truth for *this*
embedding; a reviewer checks it against the S3PR definition in [1,
§II], not against an unreproduced figure.

**Notation (source net \(N^\star=(P^\star,T^\star,\mathrm{Pre},\mathrm{Post})\)).**

Places \(P^\star = P_A^\star \cup P_B^\star \cup P_R^\star\):

| Place | Kind | Meaning |
| --- | --- | --- |
| \(p_A^0\) | idle | process \(A\) idle |
| \(p_A^1\) | operation | process \(A\) holds \(r_1\) |
| \(p_A^2\) | operation | process \(A\) holds \(r_2\) |
| \(p_B^0\) | idle | process \(B\) idle |
| \(p_B^1\) | operation | process \(B\) holds \(r_2\) |
| \(p_B^2\) | operation | process \(B\) holds \(r_1\) |
| \(p_{r_1}\) | resource | free units of \(r_1\) |
| \(p_{r_2}\) | resource | free units of \(r_2\) |

Transitions \(T^\star\):

| \(t\) | \(\mathrm{Pre}(t)\) | \(\mathrm{Post}(t)\) |
| --- | --- | --- |
| \(t_A^1\) | \(\{p_A^0, p_{r_1}\}\) | \(\{p_A^1\}\) |
| \(t_A^2\) | \(\{p_A^1, p_{r_2}\}\) | \(\{p_A^2, p_{r_1}\}\) |
| \(t_A^3\) | \(\{p_A^2\}\) | \(\{p_A^0, p_{r_2}\}\) |
| \(t_B^1\) | \(\{p_B^0, p_{r_2}\}\) | \(\{p_B^1\}\) |
| \(t_B^2\) | \(\{p_B^1, p_{r_1}\}\) | \(\{p_B^2, p_{r_2}\}\) |
| \(t_B^3\) | \(\{p_B^2\}\) | \(\{p_B^0, p_{r_1}\}\) |

Initial marking \(m_0^\star\):

\[
m_0^\star(p_A^0)=1,\;
m_0^\star(p_B^0)=1,\;
m_0^\star(p_{r_1})=1,\;
m_0^\star(p_{r_2})=1,
\]

and \(m_0^\star(p)=0\) on every other place. The net is 1-safe under
\(m_0^\star\). The unique empty-siphon deadlock marking of interest is

\[
m^\dagger(p_A^1)=1,\;
m^\dagger(p_B^1)=1,\;
m^\dagger(p)=0\text{ otherwise}.
\]

At \(m^\dagger\) the siphon \(\{p_{r_1},p_{r_2},p_A^2,p_B^2\}\) is empty
and no transition is enabled. This \(m^\dagger\) is the Proposition 4
*target*. Field 1 is decided by *our* BFS on the IMS LTS, never by
copying a firing sequence from [1].

**Why not L31’s running example.** Su et al. (T-ASE 2026, L31) is the
neighbour paper. Reconstructing their figure from memory would invent
an embedding, which PO-T3-8a and the H5 spec both forbid. H6 therefore
uses the definitional S3PR core, which L31’s S4PR class contains. The
manuscript will say this in one sentence: field 4 is decided on an
audited S3PR that is an S4PR with unit resources; it is not a replay of
L31 Figure \(k\).

## 2. Embedding definition (theory that must be written, not just coded)

### Definition H6.1 (published-net embedding)

An *embedding* of \((N^\star,m_0^\star)\) into an IMS plant is a tuple

\[
\mathcal{E}=
\bigl(N^\star,m_0^\star,\iota,\mathcal{M},x_0,\Sigma,\chi\bigr)
\]

where

- \(\mathcal{M}=(R,J)\) is a finite IMS model (resources, jobs);
- \(x_0\) is a stable initial state of \(\mathcal{M}\);
- \(\Sigma\) is a finite transition registry;
- \(\iota: P^\star\cup T^\star\to\) IMS names is a total map;
- \(\chi\) is the *marking correspondence* defined below.

**Resource clause.** \(\iota\) sends each resource place \(p_r\in P_R^\star\)
to a unique IMS resource \(\iota(p_r)\in R\) of the same capacity
\(C(\iota(p_r))=m_0^\star(p_r)+\sum_{p\in P_{\mathrm{op}}(r)} m_0^\star(p)\).
For the net of §1 this is \(C(r_1)=C(r_2)=1\).

**Operation clause.** \(\iota\) sends each operation place \(p_j^k\) to
a pair \((\mathrm{job}(p),\mathrm{hold}(p))\). Idle places map to
“job idle, no hold.”

**Event clause.** \(\iota\) sends each \(t\in T^\star\) to a unique
registry event \(\iota(t)\in\Sigma\). Distinct source transitions map
to distinct events.

**Marking correspondence \(\chi\).** A 1-safe marking \(m\) of \(N^\star\)
*corresponds* to a stable IMS state \(x\) when, for every resource \(r\),

\[
m(p_r)
=
C(r)-\sum\bigl\{u : (j,r,u)\in x.\mathrm{holds}\bigr\},
\]

and for every operation place \(p_j^k\), \(m(p_j^k)=1\) if and only if
job \(\mathrm{job}(p)\) holds exactly \(\mathrm{hold}(p)\) in the mode
named by \(\iota\). Idle tokens match idle jobs.

### Definition H6.2 (what \(\iota\) preserves)

\(\mathcal{E}\) is *sound* when all six hold:

| Id | Obligation |
| --- | --- |
| E1 | Capacities match: \(C(\iota(p_r))=1\) for both resource places. |
| E2 | Holds match: \(\chi(m_0^\star)=x_0\). |
| E3 | Enabled-event bijection at \(x_0\): \(t\) is enabled at \(m_0^\star\) iff \(\iota(t)\) is enabled at \(x_0\). |
| E4 | Local commutation: if \(t\) is enabled at \(m\) and \(\chi(m)=x\), then \(\chi(m[t\rangle)=x[\iota(t)\rangle\) (one-step). |
| E5 | No extra IMS resources: \(R=\{\iota(p):p\in P_R^\star\}\). |
| E6 | No extra jobs: \(J\) is exactly the process set of \(N^\star\). |

### Definition H6.3 (what \(\iota\) does *not* preserve)

A sound embedding does **not** claim any of:

- BAS blocked-unload modes (those are IMS-only);
- AGV occupancy unless the source net has a corresponding place;
- OR / AND acquisition;
- timing, rates, or a CTMC;
- a plant-level S3PR \(\equiv\) IMS bisimulation on a larger class;
- Su et al. CRP, SBA, or an iff.

### Lemma H6.1 (field 1 is prefix-independent)

Let \(x^\dagger=\chi(m^\dagger)\) be the image of the source deadlock
marking. Field 1 of Proposition 4 on the H6-A subject is the Boolean

\[
\Phi_1
=
\bigl[
x^\dagger\text{ occurs in the BFS of }
(\mathcal{M},x_0,\Sigma)
\text{ and the LTS is not truncated}
\bigr].
\]

The BFS witness is computed by `enumerate_stable_lts`. No firing
sequence printed in [1], and no prefix supplied by the case JSON, is
an input to \(\Phi_1\).

*Proof.* By construction of `evaluate_h6_subject`, the target is
resolved as the unique stable LTS record whose hold/request signature
equals \(\chi(m^\dagger)\), or as the shortest deadlock on that LTS if
the signature is absent. Reachability is `record is not None and not
lts.truncated`. The function does not read a `claimed_prefix` field.
Hence \(\Phi_1\) is independent of any source-paper prefix. \(\square\)

### Lemma H6.2 (sound embedding decides field 4)

Field 4 is `true` if and only if a certificate \(\mathcal{E}\) is
present *and* E1–E6 all evaluate to true on independently hashed
bytes. In particular:

- a missing certificate yields `field4_reason = no_independent_s4pr_embedding` (H5 behaviour, retained on H5);
- a present certificate that fails E1–E6 yields a typed reason naming the first failed clause;
- a present certificate that passes E1–E6 yields `s4pr_overlap = true`.

H6-A is required to pass E1–E6. H6-B is required to fail at least E5
(extra AGV resource) and therefore field 4 is false.

*Proof of the “only if” direction.* Proposition 4, field 4, as frozen
in the H5 spec, is the conjunction “declared S4PR/S3PR overlap **and**
independent embedding hash.” The hash is the SHA-256 of the
canonical JSON of \(\mathcal{E}\) (locator, incidence, \(\iota\),
model+state+registry, LTS reachability). If any of E1–E6 fails, the
verifier returns `verified=false` and the scorer must not set
`s4pr_overlap=true`. \(\square\)

### Proposition H6.3 (H6-A four-field prediction)

On the sound embedding of §1–§2, with declared resource set
\(R^\star=\{r_1,r_2\}\) and target \(x^\dagger=\chi(m^\dagger)\):

1. \(\Phi_1=\mathrm{true}\) (the circular wait is reachable by BFS:
   fire \(t_A^1\) then \(t_B^1\), or the symmetric order);
2. the local certificate family at \(x^\dagger\) is nonempty
   (kernel \(\{A,B\}\) on \(\{r_1,r_2\}\));
3. \(\lvert\{K:R_K=R^\star\}\rvert=1\);
4. `s4pr_overlap = true`.

Therefore `bridge_agreement = true` on H6-A. This is **not** a CRP
theorem and **not** an SBA run. It is the four-field *rule* of
Proposition 4 applied to an audited embedding.

### Proposition H6.4 (H6-B typed refusal)

H6-B is H6-A plus one IMS resource \(\mathrm{V}\) (kind `agv`,
capacity 1) that process \(A\) must acquire on the second step
(\(t_A^2\) becomes “acquire \(\{r_2,\mathrm{V}\}\)”). Then:

- E5 fails because \(R\setminus\iota(P_R^\star)=\{\mathrm{V}\}\);
- field 4 is `false` with
  `field4_reason = declared_distortion_agv_token`;
- fields 1–3 are still scored honestly (the circular wait may remain
  reachable; the local family may remain nonempty).

Agreement is false because field 4 is false. This is the designed
negative control: the scorer can say “yes” on a faithful net and
“no” on a declared distortion of the same net.

## 3. Four frozen hashes

The embedding certificate JSON (canonical, sorted keys, UTF-8, trailing
newline) contains exactly these four digests, each SHA-256 hex of the
named bytes:

| Hash | Bytes |
| --- | --- |
| `source_locator_sha256` | locator record: citation, DOI, object paragraph of §1, incidence matrix as a sorted list of `{t, pre, post}` |
| `iota_map_sha256` | \(\iota\) as a sorted list of `{source, image, clause}` |
| `ims_identity_sha256` | canonical JSON of \((\mathcal{M}.\mathrm{id}, x_0.\mathrm{id},\) sorted resource ids, sorted job ids, sorted transition names and acquire/release) |
| `lts_reachability_sha256` | canonical JSON of `{state_count, truncated, target_signature, bfs_witness}` computed by `enumerate_stable_lts` |

`embedding_certificate_sha256` is the SHA-256 of the whole
certificate JSON *including* those four hashes. Field 4 uses
`embedding_certificate_sha256` as the “independent embedding hash.”

**Forbidden identities.** The certificate must not equal
`ARTICLE_CORE_SCOPE_LOCK_SHA256`, must not reuse any G4/G5 case hash,
and must not reuse H5 subject identities. `reject_forbidden_identity`
is called on `ims_identity_sha256` and on
`embedding_certificate_sha256`.

## 4. Plants (executable)

Reuse the existing `IMSModel` / `IMSState` / `TransitionSpec` types.
New model ids, never `h2v2-*` or `h5-*`.

### H6-A (`H6_A_ezpeleta_unit_s3pr`)

Resources: `r1` (machine, 1), `r2` (machine, 1).
Jobs: `A`, `B`.
Initial: both idle, no holds, no requests, `stable=True`.

Registry (names are the \(\iota\)-images):

| Name | Kind | Job | Source \(\to\) target | Acquire | Release | Next request |
| --- | --- | --- | --- | --- | --- | --- |
| `A-start-r1` | START | A | idle \(\to\) hold_r1 | r1 | — | r2 |
| `A-to-r2` | DISPATCH | A | hold_r1 \(\to\) hold_r2 | r2 | r1 | — (clears) |
| `A-complete` | RELEASE | A | hold_r2 \(\to\) completed | — | r2 | — ; `mark_complete` |
| `B-start-r2` | START | B | idle \(\to\) hold_r2 | r2 | — | r1 |
| `B-to-r1` | DISPATCH | B | hold_r2 \(\to\) hold_r1 | r1 | r2 | — (clears) |
| `B-complete` | RELEASE | B | hold_r1 \(\to\) completed | — | r1 | — ; `mark_complete` |

All six are non-zero-time. START/DISPATCH controllable; RELEASE
uncontrollable. No BAS mode, no AGV, no OR/AND.

Target signature for field 1:

```text
holds = {(A, r1, 1), (B, r2, 1)}
requests = {A: {r2}, B: {r1}}
```

### H6-B (`H6_B_agv_distortion`)

Same as H6-A plus resource `V` (agv, 1). Transition `A-to-r2` acquires
`(r2, V)` and does not release `V` (the distortion is an extra hold).
Add `A-release-v` if needed so Barrier A cannot fire
`completed_job_holds_resource`. The embedding attempt still maps only
\(\{r_1,r_2\}\); `V` is the declared extra resource that fails E5.

## 5. Scoring

`evaluate_h6_subject(subject)` extends `evaluate_h5_subject`:

1. Build the plant.
2. Enumerate the stable LTS (`max_states=4096`).
3. Field 1: target signature present and LTS not truncated. **Do not**
   accept a supplied prefix as a reachability proof.
4. Field 2: `enumerate_local_blocking_certificates` at the target,
   with the BFS witness as `reachable_prefix`.
5. Field 3: \(\lvert\{K:R_K=R^\star\}\rvert\) with
   \(R^\star=\{r_1,r_2\}\).
6. Field 4: run `verify_embedding_certificate`. Set
   `s4pr_overlap` only if `verified` is true.
7. `sba_ran = false`, `crp_equations_ran = false`,
   `g4_g5_identity_reused = false`.

H5’s six rows stay frozen. H6 does not call `build_h5_subject`.

## 6. Roots, CLI, tests

- Cases: `cases/discovery/tase_hardening_v1/h6/`
  (`H6_A_ezpeleta_unit_s3pr.json`, `H6_B_agv_distortion.json`,
  `embeddings/H6_A_certificate.json`, `embeddings/H6_B_certificate.json`)
- Evidence: `evidence/tase_hardening/h6_embed/tase_hardening_h6_report.json`
- Module: `src/ims_deadlock/tase_height.py` (do not grow
  `tase_hardening.py` past its H1–H5 panel)
- Tests: `tests/test_tase_height.py`
- CLI: `tase_hardening_run.py --h6`

Required unit tests (must fail before the builder exists):

1. H6-A certificate verifies; E1–E6 all true.
2. H6-A field 4 is true; fields 1–3 match Proposition H6.3.
3. H6-A `bridge_agreement` is true.
4. H6-B certificate is present and `verified` is false with
   `declared_distortion_agv_token`.
5. H6-B field 4 is false; agreement is false.
6. Field 1 does not read a `claimed_prefix` key (even if one is
   injected into the subject dict).
7. No G4/G5/H5 identity is reused; `sba_ran` is false.
8. H5 scorer is unchanged: six H5 rows still refuse field 4.

## 7. Iteration protocol (case \(\leftrightarrow\) theory)

If H6-A field 1 is false, the builder is wrong — fix the builder, do
not weaken Lemma H6.1. If E1–E6 fail on H6-A, fix \(\iota\) or the
plant so they match §1; do not drop a clause. If H6-A agreement is
false because field 2 or 3 fails, record the row, then either

- correct the target signature so it is the circular wait, or
- correct the theory prediction in Proposition H6.3 and say why

and keep the failed clothing under
`cases/discovery/tase_hardening_v1/h6/failed/`. Never replace a failed
clothing in place.

If the definitional S3PR cannot be embedded without violating E5
(unexpected extra IMS resource), stop and redesign as H6-C; do not
invent L31 Figure \(k\).

## 8. Forbidden sentences

- “We have a CRP theorem.”
- “We replayed Su et al. Figure \(k\).”
- “We proved IMS \(\equiv\) S3PR.”
- “SBA agrees with our kernel.”
- Any reuse of G4/G5/H5 hashes as H6 identities.
- Overwriting `evidence/tase_hardening/h5/`.

## 9. Manuscript delta (after G-H6)

One subsection: “Proposition 4 on a published S3PR.” Update Table I
L31 cell: field 4 is decided on an audited S3PR core; CRP iff and SBA
remain unclaimed. Do not add a Theorem 13.

## 10. Gate G-H6

Pass iff all hold:

1. H6-A embedding certificate verifies (E1–E6).
2. H6-A field 4 is true.
3. H6-B field 4 is false with a typed distortion reason.
4. Fields 1–3 on both rows are produced by the scorer, not by hand.
5. Evidence root `evidence/tase_hardening/h6_embed/` is write-once
   and does not touch frozen roots.

Fail action: stay at the current tier; do not invent field 4.
