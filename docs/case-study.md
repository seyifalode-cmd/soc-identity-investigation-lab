# Analyst case study

## Assessment

The synthetic Alex sequence warrants investigation, but does not confirm compromise. Three failures precede a success from the same user/IP/application; subsequent application records show an order view, a denied export, and a logout. The denied export only establishes the outcome of that recorded attempt.

## Timeline

All scenario times are 23 September 2026, UTC, not screenshot capture times.

| Time | Recorded event | Interpretation |
|---|---|---|
| 09:00, 09:01, 09:02 | Alex authentication failed | Repeated unsuccessful attempts; actor unknown |
| 09:03 | Alex authentication succeeded | Successful access, without proof of actor or MFA |
| 09:04 | Order-1042 view succeeded | Recorded application action; session attribution uncertain |
| 09:05 | CustomerDirectory export denied | This export attempt was blocked |
| 09:06 | Logout succeeded | Does not establish revocation of every session |

The six-row login fixture also includes Maya's successful login at 09:04 and Ben's failed login at 09:05. They are context, not evidence of an expanded incident.

## Competing explanations

| Hypothesis | Why it remains possible | Evidence that would help discriminate |
|---|---|---|
| Legitimate password mistakes | The same pattern can be produced by an authorised user | Approved identity-verification route, device and session-linked application activity |
| Password guessing | Repeated failures precede access | Broader attempt history, source distribution, device and authentication details |
| Reused or phished password | Successful authentication can follow credential theft | Relevant identity, endpoint, and email evidence; verified user account of events |

No supplied evidence establishes the acquisition method. The optional MFA exception and LAB-SESSION-001 in the walkthrough are tabletop facts, not independently collected identity-provider logs.

## Investigation priorities

1. Preserve the original event exports, query text, selected time range, and source context.
2. Obtain authentication event IDs, result details, device IDs, MFA details, and applicable policy decisions.
3. Seek a shared session/correlation identifier before attributing application actions to the sign-in.
4. Expand review across relevant accounts, devices, applications, and time periods with coverage explicitly recorded.
5. Assess export and other access paths; a denied export is not a complete exposure assessment.
6. Record disposition, evidence gaps, owner, and next action. Do not infer that closing a training exercise closes an enterprise incident.

## Detection reasoning

The five-minute inclusive lower boundary captures a failure exactly five minutes before success. Strict upper exclusion avoids inferring sequence from equal timestamps. Grouping by user/IP/application avoids combining unrelated contexts, but misses attacks that change source addresses. IP sharing also means an address does not identify a person.

Event-ID deduplication stops repeated copies from inflating the failure count. The simplified last-record-wins behaviour for conflicting IDs is a known limitation. Replay deduplication stops a repeated success from emitting another alert in one process; it is not durable exactly-once delivery.

## Response interpretation

The local application establishes a working baseline before controls change. Session clearing rejects an old token; disabling the account rejects fresh login. Recovery verifies both that old access stays blocked and that new intended access works. This demonstrates the verification method within the app, not effectiveness in Azure, Okta, or another identity system.

## Next iteration

Add session IDs to both fixture schemas; introduce conflicting-ID rejection and validation; persist alert state; define retention and late-arrival behaviour; add distinct-user/application tests; evaluate labelled benign and malicious scenarios before making any precision/recall claim. These are proposed improvements, not completed features.
