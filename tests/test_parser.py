import json
from core.parser import FuzzResult, parse_output


def test_output_parser(tmp_path):
    path = tmp_path / "output.json"
    data = {
        "results": [
            {
                "url": "http://10.10.10.5/admin",
                "status": 301,
                "length": 4242,
                "words": 12,
                "lines": 8,
            },
            {
                "url": "http://10.10.10.5/login",
                "status": 301,
                "length": 69420,
                "words": 12,
                "lines": 8,
            },
        ]
    }
    with open(path, mode="w") as f:
        f.write(json.dumps(data))

    result = parse_output(path)
    assert result[0].url == "http://10.10.10.5/admin"
    assert result[0].status == 301
    assert result[0].size == 4242
    assert result[0].words == 12
    assert result[0].lines == 8
    assert result[1].url == "http://10.10.10.5/login"
    assert result[1].status == 301
    assert result[1].size == 69420
    assert result[1].words == 12
    assert result[1].lines == 8


def test_parse_output_empty(tmp_path):
    path = tmp_path / "output.json"
    with open(path, mode="w") as f:
        f.write(json.dumps({"results": []}))

    result = parse_output(path)
    assert result == []
