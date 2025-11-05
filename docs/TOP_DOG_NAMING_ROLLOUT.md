# Top Dog Naming Rollout

This document outlines the plan to roll out the Top Dog naming convention across services, dashboards, and communication channels.

## Scope
- Code (service names, package names where safe)
- Observability (dashboard titles, Prometheus job names/labels)
- Docs and READMEs
- Communication channels and runbooks

## Checklist
- Update service display names and tags in compose/k8s manifests
- Update Prometheus job labels to include `service=topdog-*` where applicable
- Rename dashboards in Grafana to "Top Dog – <component>"
- Update README references and CLI/help outputs
- Announce changes in internal channels; pin summary in #eng and #ops

## Timing
- Perform non-breaking label renames during low-traffic window
- Coordinate Prometheus/Grafana label and dashboard updates in the same release to avoid broken panels

## Backward Compatibility
- Maintain old labels for one release via relabeling rules where possible
- Provide a label mapping cheatsheet for queries

## Validation
- Run smoke queries after relabeling
- Confirm alerts still match on updated labels

## Communication
- Publish a one-pager summarizing changes and impact
- Provide updated links to dashboards and runbooks
