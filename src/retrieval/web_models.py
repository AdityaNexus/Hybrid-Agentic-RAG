from dataclasses import dataclass


@dataclass(slots=True)
class WebResult:
    title: str
    url: str
    snippet: str