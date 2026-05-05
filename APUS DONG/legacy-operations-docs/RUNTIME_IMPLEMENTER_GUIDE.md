# Runtime Implementer Guide

This guide is for AI runtime developers integrating Gov-Agentic AI without runtime-specific assumptions.

## Read Order
1. `runtime-link.json` when starting from an installed shim
2. `runtime-bootstrap.generated.json`
3. `AGENT_README.md`
4. canonical `configs/runtime.generated.json`

## What to Cache
- adapter capabilities
- shim installed skills
- canonical path registry

## What to Keep Dynamic
- central runtime config
- approval requirements
- active clusters and role inventory

## Fail-Closed Conditions
- central home missing
- canonical runtime config missing
- canonical skill manifest missing
- local `Yayak` missing
- runtime bootstrap path registry inconsistent

## Minimal Boot Success
A runtime is attached correctly when it can answer:
- who am I
- where is the central home
- which local bootstrap skills exist
- where do deeper role skills come from
- which governance mode and approval gates apply
