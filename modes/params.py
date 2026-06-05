from core.runner import FfufRunner
from core.filter import AutoFilter
from core.parser import parse_output, FuzzResult
from core.utils import count_wordlist
from ui.display import print_status, print_results

DEFAULT_WORDLIST = "/usr/share/seclists/Discovery/Web-Content/burp-parameter-names.txt"


class ParamFuzzer:
    def __init__(self, runner: FfufRunner):
        self.runner = runner

    def run_get(self, url: str, wordlist: str = DEFAULT_WORDLIST) -> list[FuzzResult]:
        print_status(f"Starting GET parameter fuzz on {url}", level="info")

        af = AutoFilter(self.runner)
        af.probe(wordlist, f"{url}?FUZZ=value")

        filter_flags = af.get_filter_flags()
        if filter_flags:
            print_status(f"Filtering response size: {af.filter_size}", level="info")

        args = ["-u", f"{url}?FUZZ=value", "-w", wordlist] + filter_flags
        count = count_wordlist(wordlist)
        json_path = self.runner.run(args, description=f"GET param fuzzing — {count} words")

        results = parse_output(json_path)
        print_results(results, mode="GET params")
        return results

    def run_post(self, url: str, wordlist: str = DEFAULT_WORDLIST) -> list[FuzzResult]:
        print_status(f"Starting POST parameter fuzz on {url}", level="info")

        af = AutoFilter(self.runner)
        af.probe(wordlist, url)

        filter_flags = af.get_filter_flags()
        if filter_flags:
            print_status(f"Filtering response size: {af.filter_size}", level="info")

        args = [
            "-u", url,
            "-X", "POST",
            "-d", "FUZZ=value",
            "-H", "Content-Type: application/x-www-form-urlencoded",
            "-w", wordlist,
        ] + filter_flags
        count = count_wordlist(wordlist)
        json_path = self.runner.run(args, description=f"POST param fuzzing — {count} words")

        results = parse_output(json_path)
        print_results(results, mode="POST params")
        return results
