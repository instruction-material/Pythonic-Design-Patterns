"""Version, timezone and unit conversion stay at the external boundary."""
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import UTC, datetime
import math

class AdapterError(ValueError):
    pass

def number(value: object) -> float:
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise TypeError('temperature must be numeric')
    result = float(value)
    if not math.isfinite(result):
        raise ValueError('temperature must be finite')
    return result

@dataclass(frozen=True)
class Measurement:
    instant: datetime
    celsius: float

    def __post_init__(self) -> None:
        if not isinstance(self.instant, datetime) or self.instant.utcoffset() is None:
            raise ValueError('measurement requires an aware datetime')
        value = number(self.celsius)
        if value < -273.15:
            raise ValueError('temperature is below absolute zero')
        object.__setattr__(self, 'instant', self.instant.astimezone(UTC))
        object.__setattr__(self, 'celsius', value)

def mapping(value: object) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise TypeError('record must be a mapping')
    return value

def parse_measurement(payload: Mapping[str, object]) -> Measurement:
    raise NotImplementedError('Complete parse_measurement')

def measurement_payload(value: Measurement) -> dict[str, object]:
    raise NotImplementedError('Complete measurement_payload')

def main() -> None:
    value = parse_measurement({'timestamp': '2026-01-01T02:00:00+02:00', 'temperature': {'value': 68, 'unit': 'F'}})
    print('normalized:', value.instant.isoformat(), f'{value.celsius:.1f} C')
    round_trip = parse_measurement(measurement_payload(value))
    print('round trip:', value.instant == round_trip.instant and math.isclose(value.celsius, round_trip.celsius, abs_tol=1e-10))
if __name__ == '__main__':
    try:
        main()
    except NotImplementedError as error:
        print('starter unfinished:', error)
