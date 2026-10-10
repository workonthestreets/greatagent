# Case 001: Recipient cannot attend the booked delivery window

## Case details

- **Source role:** Vessa Lorne, recipient
- **Status:** Completed — test fixture
- **Created:** 2026-01-05 09:00:00 UTC
- **Escalated:** 2026-01-05 09:10:00 UTC
- **Primary shipment:** TX-001
- **Coordinator:** Test Coordinator, Example Desk
- **Data:** Invented test fixture written for this repository

## Context

A parcel is at the destination depot. Dispatch, not the desk, controls booking changes.

## Initial request

I can't be in for the morning delivery. Can you move it?

## Overview

Events 001–002 are the escalation snapshot.

## Next action at escalation

Ask the recipient to choose from dispatcher-confirmed alternative slots.

## Outcome

Dispatch confirms the selected slot.

## Boundaries and remaining work

Do not promise an exact arrival minute.

## History

[Read the complete dated history](history.md).
