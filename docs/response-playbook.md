# Suspicious sign-in response playbook

This is an analyst training aid. The repository automates only a synthetic replay and local application checks.

| Stage | Analyst action | Evidence / decision gate |
|---|---|---|
| Validate | Confirm source, timestamps, distinct IDs, and rule conditions | Preserve matching records and query; identify missing context |
| Scope | Pivot by account, IP, device, application and time | Record coverage and correlation limits; avoid assuming a shared session |
| Assess | Compare suspicious and legitimate explanations | Use corroborating authentication/device/application records; document confidence |
| Decide | Determine whether containment is justified | Account for impact and the organisation's response authority; a threshold alone is insufficient |
| Contain | Apply appropriate approved controls | Record each action, actor, timestamp, target and outcome |
| Verify | Retry old access and fresh authentication | Check both existing-session and new-login paths; preserve actual responses |
| Recover | Address relevant cause, verify identity and restore intended access | Old credentials/tokens remain invalid; new authorised access succeeds |
| Close | Review residual risk, monitoring and follow-up ownership | Separate lab completion from an enterprise incident disposition |

## Copyable case-note template

```text
Scope / review period:
Owner / case reference:
Observed facts and evidence IDs:
Working hypotheses and alternatives:
Unknowns / telemetry gaps:
Decision and rationale:
Actions actually performed:
Verification requests and actual results:
Residual risk / next action / owner:
Disposition and supporting evidence:
```

## Lab acceptance criteria

- Ten detector checks pass.
- Replay emits one alert despite duplicate delivery.
- Baseline login and protected access return 200.
- Containment rejects old-token access with 401 and fresh login with 403.
- Recovery rejects old password/token with 401 and accepts new login/access with 200.
- Alert/audit files are saved and the server is stopped.

If a check fails, preserve the actual error and keep the affected step incomplete. The original selected screenshots do not establish final main-case closure in Jira.
