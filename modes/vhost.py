from core.runner import FfufRunner
from core.filter import AutoFilter
from core.parser import parse_output, FuzzResult
from core.utils import count_wordlist
from ui.display import print_status, print_results

DEFAULT_WORDLIST = "/usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt"


class VHostFuzzer:
    def __init__(self, runner: FfufRunner):
        self.runner = runner

    def run(
        self,
        url: str,
        domain: str,
        wordlist: str = DEFAULT_WORDLIST,
        host_pattern: str | None = None,
    ) -> list[FuzzResult]:
        host_header = host_pattern if host_pattern else f"FUZZ.{domain}"
        print_status(f"Starting vhost fuzz on {url} — Host: {host_header}", level="info")

        af = AutoFilter(self.runner)
        af.probe(wordlist, url)

        filter_flags = af.get_filter_flags()
        if filter_flags:
            print_status(f"Filtering response size: {af.filter_size}", level="info")

        args = ["-u", url, "-H", f"Host: {host_header}", "-w", wordlist] + filter_flags
        count = count_wordlist(wordlist)
        json_path = self.runner.run(args, description=f"VHost fuzzing — {count} words")

        results = parse_output(json_path)
        print_results(results, mode="vhost")
        return results
