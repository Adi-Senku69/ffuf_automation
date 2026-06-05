from unittest.mock import MagicMock, patch
from core.filter import AutoFilter
import json


def test_get_filter_flags_with_size():
    af = AutoFilter(runner=MagicMock())
    af.filter_size = 4242

    assert af.get_filter_flags() == ["-fs", "4242"]

    af.filter_size = 123.4
    assert af.get_filter_flags() == ["-fs", "123"]


def test_get_filter_flags_with_no_size():
    af = AutoFilter(runner=MagicMock())
    af.filter_size = None

    assert af.get_filter_flags() == []


def test_probe_sets_dominant_size(tmp_path):
    path = tmp_path / "output.json"

    data = {
        "results": [
            {
                "url": "http://10.10.10.5/a",
                "status": 200,
                "length": 4242,
                "words": 5,
                "lines": 3,
            },
            {
                "url": "http://10.10.10.5/b",
                "status": 200,
                "length": 4242,
                "words": 5,
                "lines": 3,
            },
            {
                "url": "http://10.10.10.5/c",
                "status": 200,
                "length": 987,
                "words": 45,
                "lines": 10,
            },
        ]
    }

    with open(path, mode="w") as f:
        f.write(json.dumps(data))

    runner = MagicMock()
    runner.run.return_value = path

    test_url = "http://test.com"
    test_wordlist = "test_wordlist"

    af = AutoFilter(runner)

    af.probe(test_wordlist, test_url)

    assert af.filter_size == 4242
