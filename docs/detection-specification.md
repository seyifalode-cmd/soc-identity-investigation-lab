# Detection specification: failures followed by success

## Purpose and contract

Identify successful authentications preceded by at least three distinct failures for the same user, IP, and application. This is a review signal, not a compromise verdict. Implementation: [cell-01.py](../code/cell-01.py); replay: [cell-03.py](../code/cell-03.py).

| Input field | Expected type | Use |
|---|---|---|
| `id` | Unique string | Deduplication and evidence reference |
| `time` | Timezone-aware Python datetime | Chronological order and five-minute window |
| `user` | String | Account grouping |
| `ip` | String | Source grouping |
| `app` | String | Application grouping |
| `result` | `Failed` or `Success` | Failure evidence and success anchor |

These are fixture assumptions, not enforced validation rules. Malformed records may raise errors or be ignored depending on which field is invalid. CSV fields have different names and no IDs; the notebook constructs its own Python fixture rather than parsing the CSVs.

## Algorithm

1. Build a dictionary keyed by event ID. Identical repeated deliveries collapse. Conflicting values for one ID retain the last supplied record.
2. Sort the remaining events by time and ID.
3. For each success, select same-user/IP/application failures with `success_time - 5 minutes <= failure_time < success_time`.
4. Emit a candidate when at least three failures qualify. Include the failure IDs and successful-event ID.
5. In the replay worker, suppress candidate alert IDs already emitted in the current process.

The lower boundary is inclusive, the upper boundary is exclusive. Input list order does not determine event order. Different success IDs can each emit an alert using overlapping failures; failures are not consumed or reset by an intervening success. The rule does not require consecutive failures.

## Alert fields

| Output | Meaning |
|---|---|
| `alert_id` | `rule1:` plus success ID; assumes globally trustworthy IDs |
| `user`, `ip`, `application` | Matching context |
| `failures` | Number of qualifying deduplicated failures |
| `success_time` | ISO-formatted event time |
| `evidence_ids` | Failures followed by the success anchor |
| `disposition` | Initial analyst review status |

## KQL comparison

The provided KQL candidate query counts failures and successes inside one fixed interval. It does not enforce sequence, deduplicate by event ID, or use a success-relative window. Its original schema lacks event IDs. Treat the Python detector as an additional exercise, not a byte-for-byte translation of the KQL.

## False positives and coverage gaps

Repeated legitimate mistakes can satisfy the rule. Shared IPs do not identify one person. Source changes split a user's activity into different groups, so rotating-source attempts may not match. Password theft with a successful first attempt will not match. Success without recorded failures will not match, whether legitimate or malicious. Missing telemetry directly affects these conclusions.

Tuning should start with reviewed alert context and telemetry quality. Raising the threshold may reduce volume but also excludes matching attack patterns; the small fixture cannot quantify that trade-off.

## Runtime characteristics

The detector scans all records for each success: worst-case quadratic work per batch. The replay repeatedly evaluates growing history, making it inappropriate for an unbounded production stream. State is in memory. It has no durable checkpoint, schema validation, retry/dead-letter handling, retention, or clock-skew allowance.

Late failures can make a previously unmatched success match when history is re-evaluated. Once an alert ID has been emitted, later additional evidence does not update that emitted alert. A real pipeline would need an explicit policy for late data and alert revisions.

## Validation scope

The original ten checks cover the source walkthrough. The added regression cases check out-of-order input, separate users/applications, the just-outside boundary, repeated success delivery, evidence IDs, and multiple successes. The suite also records the existing conflicting-ID behaviour so the limitation remains visible. These are functional tests, not threat-detection effectiveness measurements.
