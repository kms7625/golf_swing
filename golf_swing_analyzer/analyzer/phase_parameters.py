"""Immutable phase rules. Defaults reproduce 3bdf45d exactly."""
from dataclasses import dataclass
import math


@dataclass(frozen=True)
class PhaseParameters:
    plateau_ratio: float = .05
    top_offset_sec: float = 0.0
    onset_fraction: float = .10
    address_window_sec: float = 3.0
    address_offset_sec: float = 0.0
    address_min_valid_sec: float = 0.0
    impact_window_sec: float = 1.25
    finish_window_sec: float = 2.0
    finish_mode: str = 'minimum'
    finish_speed_ratio: float = .20
    finish_hold_sec: float = .20
    smooth_sec: float = .10

    def __post_init__(self):
        numeric = [v for v in self.__dict__.values() if isinstance(v, (int, float))]
        if not all(math.isfinite(v) for v in numeric):
            raise ValueError('Phase parameters must be finite')
        if not 0 <= self.plateau_ratio <= .25 or not 0 < self.onset_fraction < 1:
            raise ValueError('Invalid amplitude ratio')
        if any(getattr(self, name) <= 0 for name in
               ('address_window_sec', 'impact_window_sec', 'finish_window_sec',
                'finish_speed_ratio', 'finish_hold_sec', 'smooth_sec')):
            raise ValueError('Time windows and speed threshold must be positive')
        if self.finish_mode not in ('minimum', 'settled_start', 'settled_end'):
            raise ValueError('Unknown finish rule')
        if self.address_min_valid_sec < 0:
            raise ValueError('Minimum address support must be nonnegative')


BASELINE_PARAMETERS = PhaseParameters()
# A regression fix selected on split 1–3 and seven application videos.
# The prior A experiment exposed split 4 once; the fix's second exposure is final.
CALIBRATED_PARAMETERS = PhaseParameters(
    plateau_ratio=.05,
    onset_fraction=.02,
    address_window_sec=2.0,
    address_offset_sec=-.20,
    address_min_valid_sec=.30,
    impact_window_sec=1.25,
    finish_mode='settled_start',
    finish_speed_ratio=.40,
    finish_hold_sec=.10,
    smooth_sec=1/6,
)
