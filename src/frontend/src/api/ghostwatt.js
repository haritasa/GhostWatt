const API_BASE = "/api";

async function request(path, options) {
  const response = await fetch(`${API_BASE}${path}`, options);
  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || "GhostWatt API is unavailable");
  }
  return response.json();
}

export const getDashboard = () => request("/dashboard?building_id=building-59");
export const getAnomalies = (status = "") =>
  request(`/anomalies?building_id=building-59&limit=20${status ? `&status=${status}` : ""}`);
export const getAnomaly = (id) => request(`/anomalies/${id}`);
export const updateAnomalyStatus = (id, status) =>
  request(`/anomalies/${id}/status`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ status }),
  });
export const clearBuilding59 = () =>
  request("/ingestion/building-59", { method: "DELETE" });

export const ingestBuilding59 = (sourceDir) =>
  request("/ingestion/building-59", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(sourceDir ? { source_dir: sourceDir } : {}),
  });

export const demoEvent = {
  id: "event-2021-07-14-overnight",
  title: "Overnight excess energy use",
  status: "new",
  severity: "high",
  start_at: "2021-07-14T00:00",
  end_at: "2021-07-14T05:00",
  duration_minutes: 300,
  occupancy_context: { label: "Low occupancy", value: 4, unit: "people" },
  energy: { actual_kwh: 460, expected_kwh: 225, excess_kwh: 235, deviation_percent: 104.4 },
  impact: { estimated_cost_usd: 47, estimated_co2_kg: 88.1 },
  confidence: "high",
  recommended_action: "Review HVAC, lighting, and equipment schedules.",
};

export const demoDashboard = {
  building: { id: "building-59", name: "Berkeley Building 59" },
  period: { start: "2021-07-01T00:00", end: "2021-07-31T23:59", time_basis: "Demo data" },
  summary: {
    total_energy_kwh: 12840.2,
    anomalous_excess_kwh: 482.6,
    estimated_cost_impact_usd: 96.52,
    estimated_co2_kg: 181,
    anomaly_event_count: 8,
  },
  top_events: [demoEvent],
};

export const demoDetail = {
  ...demoEvent,
  explanation: {
    headline: "Electricity use was 104% above the expected level during low occupancy.",
    actual_kwh: 460,
    expected_kwh: 225,
    excess_kwh: 235,
    baseline_method: "Median usage from comparable historical intervals",
    comparison_context: ["Same building", "Overnight period", "Weekday", "Low occupancy"],
  },
  impact: {
    ...demoEvent.impact,
    assumptions: ["Estimated using the configured electricity cost rate.", "Potential impact is not verified savings."],
  },
  recommended_actions: [
    { title: "Review HVAC scheduling", reason: "Sustained overnight load may indicate HVAC operation outside occupied hours." },
    { title: "Inspect lighting and plug-load controls", reason: "Low occupancy should normally correspond to reduced non-essential electrical load." },
  ],
  intervals: [
    [92, 45, 4], [88, 45, 4], [95, 45, 3], [91, 45, 5], [94, 45, 4], [90, 45, 4],
  ].map(([actual_kwh, expected_kwh, occupancy_value], index) => ({
    timestamp: `2021-07-14T0${index}:00`, actual_kwh, expected_kwh, occupancy_value, occupancy_unit: "people", is_anomalous: true,
  })),
};
