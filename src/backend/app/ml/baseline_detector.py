"""Versioned, historical-only, explainable schedule-aware median baseline."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from app.core.config import DetectionPolicy


@dataclass(frozen=True)
class BaselineScore:
    expected_kwh: float | None
    support: int
    cohort: str


class ScheduleAwareBaselineModel:
    """Predict expected use from prior comparable schedule cohorts only.

    Exact cohorts use quarter-hour, weekday/weekend class, and meteorological
    season. A hierarchy relaxes season, then day type, when history is sparse.
    """

    version = "schedule-aware-median-v1"

    def fit(self, readings: pd.DataFrame, policy: DetectionPolicy) -> "ScheduleAwareBaselineModel":
        self.policy = policy
        self.readings = readings.sort_values("timestamp").copy()
        self.readings["quarter"] = self.readings.timestamp.dt.hour * 4 + self.readings.timestamp.dt.minute // 15
        self.readings["day_type"] = self.readings.timestamp.dt.day_of_week.ge(5).map({True: "weekend", False: "weekday"})
        self.readings["season"] = ((self.readings.timestamp.dt.month % 12) // 3 + 1).map({1: "winter", 2: "spring", 3: "summer", 4: "autumn"})
        return self

    @staticmethod
    def _prior_median(frame: pd.DataFrame, groups: list[str]) -> tuple[pd.Series, pd.Series]:
        grouped = frame.groupby(groups, observed=True)["actual_kwh"]
        expected = grouped.transform(lambda values: values.shift().expanding().median())
        support = grouped.cumcount()
        return expected, support

    def score(self, readings: pd.DataFrame | None = None) -> pd.DataFrame:
        frame = (readings.copy() if readings is not None else self.readings.copy()).sort_values("timestamp")
        if "quarter" not in frame:
            self.fit(frame, self.policy)
            frame = self.readings.copy()
        exact, exact_support = self._prior_median(frame, ["quarter", "day_type", "season"])
        day_type, day_type_support = self._prior_median(frame, ["quarter", "day_type"])
        quarter, quarter_support = self._prior_median(frame, ["quarter"])
        frame["expected_kwh"] = exact
        frame["baseline_support"] = exact_support
        frame["baseline_cohort"] = "quarter-hour, day type, season"
        use_day_type = frame.baseline_support < self.policy.minimum_comparable_samples
        frame.loc[use_day_type, ["expected_kwh", "baseline_support", "baseline_cohort"]] = pd.DataFrame({
            "expected_kwh": day_type[use_day_type], "baseline_support": day_type_support[use_day_type],
            "baseline_cohort": "quarter-hour, day type",
        })
        use_quarter = frame.baseline_support < self.policy.minimum_comparable_samples
        frame.loc[use_quarter, ["expected_kwh", "baseline_support", "baseline_cohort"]] = pd.DataFrame({
            "expected_kwh": quarter[use_quarter], "baseline_support": quarter_support[use_quarter],
            "baseline_cohort": "quarter-hour",
        })
        return frame


BASELINE_METHOD = "Historical schedule-aware median from prior comparable intervals"

__all__ = ["BASELINE_METHOD", "BaselineScore", "ScheduleAwareBaselineModel"]
