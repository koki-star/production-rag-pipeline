# On-Call Notes and Platform Limits

This page records the operational limits that people ask about during lab hours. It is not an outage timeline for public cloud vendors.

## Platform limits

- One namespace per student team in staging.
- 40 vCPU and 160 GB RAM per staging namespace.
- 10 GB object storage per namespace without an extra request.
- 50 GB block storage per namespace without an extra request.
- Five public hostnames per team, and only in shared staging or production.

If you need more room for a demo week, file a limit request two days ahead.

## Common failures

A pod is pending: the node pool may be full, or the pod asks for more memory than a Kubernetes Worker Node can reserve.

A service cannot reach the database: check that both sides sit in the same VPC or that an approved peer exists.

A deploy hangs on image pull: isolated VPCs cannot reach a public registry. Mirror the image first.

A TLS error on an internal name: check the clock on the node. NTP drift is a known cause.

## What this page does not cover

This page does not explain public vendor outages, sports results, or news events. Those topics are outside the internal knowledge base. The assistant should treat them as out of scope for internal documents.
