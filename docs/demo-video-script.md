# GhostWatt Hackathon Demo Script

**Target runtime:** 2 minutes 35 seconds  
**Format:** Screen recording with voiceover; no background music required.

> Before recording, open GhostWatt at the hero page and confirm the dashboard has imported data. Do not show terminal secrets, personal paths, browser bookmarks, or third-party logos. Do not use copyrighted music.

## 0:00–0:15 — Problem and product
**On screen:** GhostWatt hero page; show the headline and feature cards.

**Say:**
> Commercial buildings already collect energy data, but facility teams often lack the time and analytics tools to identify avoidable consumption. GhostWatt turns that existing data into clear, actionable energy-auditing insights.

## 0:15–0:32 — Product value
**On screen:** Hero page feature cards.

**Say:**
> GhostWatt is built for property managers, facility teams, universities, and energy auditors. It combines electricity use with schedules, occupancy evidence, Wi-Fi device proxies, and weather context to identify potential off-hours energy waste.

## 0:32–0:45 — Enter the working app
**On screen:** Click **Explore the dashboard** and pause on the KPI cards.

**Say:**
> This is the live GhostWatt dashboard. These cards summarize total analyzed energy, anomalous excess energy, estimated cost opportunity, estimated carbon impact, and the events that need review.

## 0:45–1:05 — Demonstrate import capability
**On screen:** Click **Import** in the dashboard header. Show the modal and folder-path field, then close it. Do not clear data during the recording.

**Say:**
> Building data is imported from a local folder into SQLite. GhostWatt normalizes electricity, camera occupancy, Wi-Fi device-proxy, and weather files before running detection. The same workflow can clear saved data before a fresh import when needed.

## 1:05–1:30 — Show the anomaly queue
**On screen:** Show the anomaly queue and select a high- or critical-severity event.

**Say:**
> Instead of asking operators to inspect thousands of meter readings, GhostWatt ranks schedule-aware anomaly events. Each event represents a period where electricity was materially higher than the historical expected level during an overnight, weekend, or configured holiday schedule.

## 1:30–2:00 — Explain the baseline and evidence
**On screen:** In the event drawer, highlight Actual, Expected, and Excess values; then show the interval chart.

**Say:**
> The expected baseline is explainable. For every 15-minute interval, GhostWatt compares actual use with the median of earlier comparable intervals—matching the same time slot, weekday or weekend pattern, and season. It flags an event only when both the extra kilowatt-hours and percentage deviation exceed configured thresholds.

> The interval chart makes that evidence visible: actual energy is compared directly against the expected baseline.

## 2:00–2:20 — Context and actionability
**On screen:** Highlight schedule and occupancy labels, impact estimate, recommendation, and status controls.

**Say:**
> The event records schedule context, available occupancy evidence, estimated cost and carbon impact, data-quality context, and a recommended next action—such as reviewing HVAC, lighting, or plug-load schedules.

> A manager can mark the event as investigating, resolved, or dismissed, and that workflow status is persisted in SQLite.

## 2:20–2:35 — Close
**On screen:** Close the event drawer and show the queue or return to the hero page.

**Say:**
> GhostWatt makes energy auditing accessible for organizations that have building data but do not have expensive building-management analytics. It helps teams find potential waste, prioritize investigation, and act on the highest-impact opportunities. Thank you.

## Submission checklist

- [ ] Runtime is below **3:00**; aim for 2:35.
- [ ] The recording visibly shows the working app on the browser/device.
- [ ] The dashboard uses imported data, not Demo view.
- [ ] The Import modal, dashboard, event detail, and status controls are shown.
- [ ] No personal folders, secrets, terminal output, browser bookmarks, or unrelated apps are visible.
- [ ] No copyrighted music, unlicensed graphics, or third-party trademarks are included.
- [ ] Upload the final video as **publicly visible** on an allowed platform and submit its public link on the hackathon website.
