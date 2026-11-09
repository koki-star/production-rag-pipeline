# Campus Cloud Architecture

Campus Cloud is our internal platform for class projects and staff tools. It has two main planes. The control plane stores accounts, network plans, and deploy records. The data plane runs customer workloads. Students and staff only place application code in the data plane.

## Regions and environments

We keep three environments: sandbox, staging, and production. Sandbox is for short experiments. Staging is the place to test a full setup before production. Production holds live traffic.

Each environment has its own network boundary. Staging and production do not share a VPC. A job that works in staging can still fail in production if a secret or a hostname is wrong, so we treat them as separate worlds.

## Core services

Compute runs on Kubernetes clusters. Each cluster lives inside a VPC. Worker nodes are the machines that run containers. The control plane nodes stay private.

Storage has two options. Object storage holds logs, images, and export files. Block storage holds databases. Do not put secrets in object storage.

The network layer provides VPC support, subnets, routing tables, and optional peering. Isolated VPCs have no internet gateway. Shared VPCs can reach approved package mirrors through a managed NAT path.

## How a request moves

A user opens an app hostname. The edge load balancer terminates TLS and sends the request to a service in the target environment. The service may read a database or call another internal API. It should not call the public internet unless the security review allows it.

Logs go to the central collector. Metrics go to the same collector under a different stream. Traces are optional but useful when a request crosses more than one service.

## What this assistant should know

This knowledge base covers how we design the platform, how we deploy, how we bill shared resources, and how we build an isolated VPC in staging. It also covers Kubernetes Worker Nodes and the older Terraform modules. It does not cover public cloud outage news or sports scores. Ask the runbook for deploy steps and ask the VPC guide for staging network steps.

## Identity and service names

Every service gets a stable internal name. The pattern is `<service>.<env>.campus-cloud.internal`. Staging names never point at production IPs. If a config file hard codes a production name, the staging review should fail.

Human users sign in through the campus identity provider. Service-to-service calls use short lived tokens issued by the control plane. A token includes the service name, the environment, and an expiry time. A receiver must reject a token with the wrong environment.

## Data stores

Use a managed Postgres instance when the app needs transactions. Use object storage when the app needs files. Do not run a database on a Kubernetes Worker Node unless the lab prompt says to do that for a lesson.

Backups for staging run once a day. Backups for production run every six hours. Restore tests happen on the first Monday of the month in staging only.

## Diagram in words

Think of the platform as three boxes side by side: sandbox, staging, and production. Each box contains a VPC, a Kubernetes cluster, and a small set of shared services. A dotted line between staging and the shared artifact registry is the only extra path an isolated VPC may request. There is no line from staging to production.
