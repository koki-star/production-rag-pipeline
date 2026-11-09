# Security Baseline

This baseline applies to every service on Campus Cloud. It is not a full audit checklist. It is the minimum bar before a staging review can pass.

## Secrets and tokens

Store secrets in the environment vault. Load them as environment variables at runtime. Do not commit a `.env` file. Do not write a token into a Terraform variable that ends up in plan output.

Session tokens for internal apps should expire in 12 hours or less. Refresh tokens need a rotation policy.

## Network rules

Services in an isolated VPC in our staging environment should not open a public load balancer. If a teacher needs to view a demo, use the approved preview proxy.

Outbound traffic from isolated networks is denied by default. Shared staging networks may reach the internal package mirror and the log collector only.

## Access roles

There are three roles: reader, operator, and admin. Readers can view logs and metrics. Operators can deploy to staging. Admins can deploy to production and change network policies.

Do not share an admin login. If a student project needs a one-time production deploy, ask a staff admin to run it.

## Logging

Auth failures, deploy events, and security group changes must be logged. Do not log raw passwords or full bearer tokens. If a log line would include a secret, replace that field with the word redacted.
