# Test Run Template

Use this template for every requested model test run. Automated results are
preliminary; the final result is the manual audit.

## Run details

- Pipeline/model:
- Thinking mode:
- Evaluation set and case count:
- Run label:
- Report files:

## Automated result

- Passed/total:
- Pass rate:
- Automated failures:

## Runtime

| Test | Runtime (seconds) |
|---|---:|
| `<case name>` | |

- Overall generation runtime (seconds):
- Mean runtime per test (seconds):
- Slowest test:

## Manual audit

Audit every generated answer independently. For each requested journey, verify
the requested origin and destination, the ordered line pair, and every required
Central Station transfer. Treat contradictory route narration as incorrect even
when a response later corrects itself.

- Manual passed/total:
- Manual pass rate:
- Automated false positives:
- Automated false negatives:

| Test | Automated result | Manual result | Finding |
|---|---|---|---|
| `<case name>` | | | |

## Conclusion

- Final result: the manually audited score.
- Comparison with relevant prior runs:
