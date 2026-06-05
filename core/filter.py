import tempfile
import os
from core.runner import FfufRunner
from core.parser import parse_output

PROBE_LINES = 150


class AutoFilter:
    def __init__(self, runner: FfufRunner):
        self.runner = runner
        self.filter_size: int | float | None = None

    def _make_probe_wordlist(self, wordlist: str) -> str:
        with open(wordlist) as f:
            lines = [l for l in f.readlines()[:PROBE_LINES] if l.strip() and not l.startswith("#")]
        tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False)
        tmp.writelines(lines)
        tmp.close()
        return tmp.name

    def probe(self, wordlist: str, url: str) -> None:
        probe_wordlist = self._make_probe_wordlist(wordlist)
        cmd = ["-u", url, "-w", probe_wordlist]

        tmp_path = self.runner.run(cmd)
        os.unlink(probe_wordlist)

        json_list = parse_output(tmp_path)

        if not json_list:
            return

        count = {}
        for value in json_list:
            if value.size not in count:
                count[value.size] = 1
            else:
                count[value.size] += 1

        self.filter_size = max(count, key=count.get)

    def get_filter_flags(self) -> list[str]:
        if self.filter_size is not None:
            return ["-fs", str(int(self.filter_size))]
        return []
