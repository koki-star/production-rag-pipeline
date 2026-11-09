# Terraform Modules

We manage Campus Cloud networks and clusters with Terraform. Teams should use the current module set unless a change ticket says the older set is required for a rollback test.

## Current module set

The current modules live under `terraform/modules/v3`.

- `vpc` creates a VPC, subnets, and routing. Set `isolated = true` when you want the same layout described in the staging VPC guide.
- `k8s-cluster` creates the control plane records and the bootstrap files for Kubernetes Worker Nodes.
- `node-pool` adds a group of worker nodes and applies the system requirement checks.
- `app-service` creates a namespace, a deploy skeleton, and a public or private hostname.

Pin a module version in your root module. Do not track the main branch of the module repo.

## Older terraform modules

Last month some teams still used the v2 modules. The older terraform modules used different variable names. `enable_public_nat` in v2 is now `isolated` with the opposite meaning. If you copy an old file, a staging VPC can accidentally get a NAT gateway.

The older terraform modules also created a single subnet. The current vpc module creates two subnets so a zone failure does not take down every pod.

If a teammate asks "Can I do that with the older terraform modules we used last month?", the safe answer is: only for a documented rollback test. For a new isolated VPC in staging, use the current `vpc` module with `isolated = true`.

## Apply flow

1. Run `terraform fmt` and `terraform validate`.
2. Run `terraform plan` and save the plan file in the change ticket.
3. Ask a reviewer to read the plan.
4. Apply the saved plan. Do not apply a fresh plan that nobody reviewed.

State files stay in the shared state bucket. Do not keep state on a laptop.
