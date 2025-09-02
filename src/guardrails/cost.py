from dataclasses import dataclass

@dataclass
class CostPolicy:
    max_rows: int
    timeout_seconds: int

default_policy = CostPolicy(max_rows=10000, timeout_seconds=20)
