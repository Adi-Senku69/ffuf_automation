import json
from dataclasses import dataclass


@dataclass
class FuzzResult:
    url: str
    status: int
    words: int
    size: int
    lines: int
    fuzz_value: str = ""

    @classmethod
    def from_dict(cls, d: dict) -> "FuzzResult":
        return cls(
            url=d["url"],
            status=d["status"],
            words=d["words"],
            size=d["length"],
            lines=d["lines"],
            fuzz_value=d.get("input", {}).get("FUZZ", ""),
        )


def parse_output(json_path: str) -> list[FuzzResult]:
    with open(json_path) as f:
        json_object = json.load(f)
        return [FuzzResult.from_dict(r) for r in json_object["results"]]
