# Provision an Isolated VPC in Our Staging Environment

This page is the internal guide for staging networks. Use it when someone asks how to provision an isolated VPC in our staging environment.

An isolated VPC in staging is a private network with no public internet gateway. Workloads inside it can talk to each other and to approved internal endpoints. They cannot open outbound connections to the public web.

## When to use an isolated VPC

Use an isolated VPC in our staging environment when you are testing a service that handles student data, grade exports, or any token that should not leak. Also use it when you want to prove that a job can run without a public package download.

Do not use an isolated VPC when the service must call a public API during the test. In that case use a shared staging VPC with an allow list.

## How do I provision an isolated VPC in our staging environment?

Follow these steps to provision an isolated VPC in our staging environment:

1. Sign in to the Campus Cloud console and switch the context to staging.
2. Open Network, then VPC, then Create.
3. Set the name to `staging-isolated-<team>`. The name must start with `staging-isolated-`.
4. Set the CIDR block to `10.40.0.0/16` unless your team already has a reserved range. Do not overlap `10.40.0.0/16` with another staging VPC.
5. Choose Isolated mode. Isolated mode leaves out the internet gateway on purpose.
6. Create two private subnets. Place subnet A in staging zone A with `10.40.1.0/24`. Place subnet B in staging zone B with `10.40.2.0/24`.
7. Attach the default staging routing table that points only to internal targets.
8. Enable DNS hostnames so internal services can use names instead of raw IPs.
9. Tag the VPC with `env=staging`, `isolation=private`, and your team name.
10. Save the VPC id in the team inventory page.

After you provision an isolated VPC in our staging environment, create a security group that allows inbound traffic only from the staging shared services range `10.30.0.0/16` on the ports your app needs. Deny all other inbound traffic.

## Peering and exceptions

If the service needs the staging artifact registry, add a peering request to `staging-shared-services`. A reviewer must approve the peer. The peer should allow registry ports only.

Do not add a NAT gateway to an isolated VPC to make a quick download work. That change would break the isolation promise.

## Checks after creation

- Confirm there is no internet gateway attached.
- Confirm both subnets are private.
- Launch a tiny test pod and try to reach `https://example.com`. The call should fail.
- Reach the internal health service at `health.staging.campus-cloud.internal`. That call should work.

If those checks pass, the isolated VPC in our staging environment is ready for application deploy tests.

## Worked example

A team named harbor wants to provision an isolated VPC in our staging environment for a grading assistant. They create `staging-isolated-harbor` with CIDR `10.40.0.0/16`. They add subnets `10.40.1.0/24` and `10.40.2.0/24`. They peer only to `staging-shared-services` so they can pull the approved app image. They deploy the API into that VPC and confirm that a curl to a public news site times out. That is the expected result.

If the same team later needs a public demo, they should not open the isolated VPC. They should deploy a separate copy into the shared staging VPC and use fake data.
