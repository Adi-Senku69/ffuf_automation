from core.runner import FfufRunner
from core.parser import parse_output


class AutoFilter:
    def __init__(self, runner: FfufRunner):
        self.runner = runner
        self.filter_size: int | float | None = None

    def probe(self, wordlist: str, url: str) -> None:
        cmd = ["-u", url, "-w", wordlist]

        tmp_path = self.runner.run(cmd)

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
