from core.runner import FfufRunner
from core.filter import AutoFilter
from core.parser import parse_output, FuzzResult
from core.utils import count_wordlist
from ui.display import print_status, print_results

DEFAULT_WORDLIST = "/usr/share/seclists/Discovery/Web-Content/DirBuster-2007_directory-list-2.3-small.txt"


class DirectoryFuzzer:
    def __init__(self, runner: FfufRunner):
        self.runner = runner

    def run(self, url: str, wordlist: str = DEFAULT_WORDLIST) -> list[FuzzResult]:
        print_status(f"Starting directory fuzz on {url}", level="info")

        af = AutoFilter(self.runner)
        af.probe(wordlist, f"{url}/FUZZ")

        filter_flags = af.get_filter_flags()
        if filter_flags:
            print_status(
                f"Filtering response size: {af.filter_size}", level="info")

        args = ["-u", f"{url}/FUZZ", "-w", wordlist] + filter_flags
        count = count_wordlist(wordlist)
        json_path = self.runner.run(args, description=f"Directory fuzzing — {count} words")

        results = parse_output(json_path)
        print_results(results, mode="dir")
        return results
