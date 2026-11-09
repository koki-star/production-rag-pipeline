# Billing Policies

Campus Cloud shares real compute with class projects, so we track cost by team and environment. This page explains how charges appear and how to avoid a surprise bill.

## Who pays for what

Staging and sandbox have a monthly classroom credit. Production has no classroom credit. If a project goes beyond the staging credit, the extra amount is billed to the department code on the namespace.

Storage and egress are billed separately from CPU. Isolated VPCs do not add an extra hourly fee, but they still pay for the nodes inside them.

## Required tags

Every billable resource needs `env`, `team`, and `project` tags. Missing tags cause the cost to fall into the shared unmatched bucket. The unmatched bucket is reviewed each Friday.

Kubernetes Worker Nodes inherit tags from the node pool. If you create a node by hand and skip tags, the nightly job will stop the node after a warning.

## Staging limits

A staging namespace may run up to 40 vCPU and 160 GB RAM unless a teacher raises the cap. If you hit the cap, the deploy API returns an error instead of starting extra pods.

Long running staging databases should be sized down after a demo. A forgotten database is a common source of extra charges.

## How to read a bill

The invoice page groups items by environment, then by service. Look at staging first. If a line item named `node-hours` is high, count the Kubernetes Worker Nodes that stayed up overnight.

Refunds for mistakes are possible when you file a note within seven days and show that the resource was unused. There is no refund for production traffic you meant to send.

## Classroom credit example

A team with a 40 dollar staging credit that runs three Kubernetes Worker Nodes for ten hours during a demo week may still stay inside the credit. The same three nodes left running for a full month will go over the credit. The invoice will show extra node-hours under staging. Stop unused nodes after the demo to avoid that line item.
