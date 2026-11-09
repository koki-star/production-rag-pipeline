# Deployment Runbook

This runbook explains how to ship a service on Campus Cloud. Follow the order below. Skipping a check is the usual reason a staging test looks fine and production then fails.

## Before you deploy

Confirm the service name, the environment, and the image tag. The image tag must point to a digest that passed the pipeline. Do not deploy an image tagged only as latest.

Check the change ticket. Staging deploys need one reviewer. Production deploys need two reviewers and a written rollback plan.

Make sure the Kubernetes namespace exists. If the service needs a new secret, store it in the environment vault first. Do not paste a secret into a manifest file.

## Staging deploy steps

1. Open the deploy console and select staging.
2. Choose the service and the approved image digest.
3. Review the health endpoint. The default path is `/healthz`.
4. Apply the change. Wait until the new pods report ready.
5. Call the health endpoint from inside the cluster.
6. Run the smoke checks listed on the service page.

If a pod stays pending, look at node resources next. A common cause is a request for more memory than a Kubernetes Worker Node can give.

## Production deploy steps

Repeat the staging steps in production only after the staging smoke checks pass. Use a rolling update. Keep the previous replica set until the new pods stay healthy for ten minutes.

If error rates rise above the service budget, roll back with the previous digest. Do not try to patch a live image by hand.

## After you deploy

Write the digest, the time, and the ticket number in the change log. Watch logs for at least fifteen minutes. If you changed a network policy, verify that the service can still reach its database and cannot reach blocked hosts.

## Rollback

The rollback command is the same deploy flow with the last known good digest. After rollback, file a short note that says what failed and what you changed. This note helps the next person avoid the same mistake.

## Smoke checks we expect

A basic smoke check should prove four things: the process starts, the health endpoint returns 200, the service can read its database or fallback data, and the service cannot reach a blocked host. Write the commands you used in the change ticket so another person can repeat them.

For a web app, open the staging hostname and sign in with a test account. For an API, call one read route and one write route. If the write route changes data, use a row that is safe to delete.

## Frozen deploys

Teachers may freeze production during exam week. A freeze means no production deploys except a documented emergency. Staging stays open. If you missed a production window, wait for the freeze to end rather than asking for a special exception.
