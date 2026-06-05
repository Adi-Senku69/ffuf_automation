from core.runner import FfufRunner
from core.parser import parse_output, FuzzResult
from ui.display import print_status, print_results

DEFAULT_WORDLIST = "/usr/share/seclists/Discovery/Web-Content/web-extensions.txt"


class ExtensionFuzzer:
    def __init__(self, runner: FfufRunner):
        self.runner = runner

    def run(self, url: str, wordlist: str = DEFAULT_WORDLIST) -> list[FuzzResult]:
        print_status(f"Starting extension fuzz on {url}", level="info")

        args = ["-u", f"{url}/indexFUZZ", "-w", wordlist]
        json_path = self.runner.run(args)

        results = parse_output(json_path)
        print_results(results, mode="extensions")
        return results
