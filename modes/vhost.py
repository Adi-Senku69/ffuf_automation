from core.runner import FfufRunner
from core.filter import AutoFilter
from core.parser import parse_output, FuzzResult
from ui.display import print_status, print_results

DEFAULT_WORDLIST = "/usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt"


class VHostFuzzer:
    def __init__(self, runner: FfufRunner):
        self.runner = runner

    def run(
        self, url: str, domain: str, wordlist: str = DEFAULT_WORDLIST
    ) -> list[FuzzResult]:
        print_status(f"Starting vhost fuzz on {url} for domain {domain}", level="info")

        af = AutoFilter(self.runner)
        af.probe(wordlist, url)

        filter_flags = af.get_filter_flags()
        if filter_flags:
            print_status(f"Filtering response size: {af.filter_size}", level="info")

        args = ["-u", url, "-H", f"Host: FUZZ.{domain}", "-w", wordlist] + filter_flags
        json_path = self.runner.run(args)

        results = parse_output(json_path)
        print_results(results, mode="vhost")
        return results
