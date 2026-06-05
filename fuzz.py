#!/usr/bin/env python3
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from core.runner import FfufRunner
from modes.directory import DirectoryFuzzer
from modes.extensions import ExtensionFuzzer
from modes.vhost import VHostFuzzer
from modes.params import ParamFuzzer
from ui.display import print_banner, print_status

MODES = ["dir", "ext", "vhost", "params-get", "params-post"]


def build_runner(args: argparse.Namespace) -> FfufRunner:
    return FfufRunner(
        threads=args.threads,
        proxy=args.proxy,
        delay=args.delay,
    )


def run_auto(runner: FfufRunner, args: argparse.Namespace) -> None:
    tasks = {}
    with ThreadPoolExecutor() as executor:
        wl = args.wordlist
        tasks["dir"] = executor.submit(
            DirectoryFuzzer(runner).run, args.target, *([wl] if wl else [])
        )
        if args.domain:
            tasks["vhost"] = executor.submit(
                VHostFuzzer(runner).run, args.target, args.domain, *([wl] if wl else [])
            )

    dir_results = tasks["dir"].result()

    php_pages = [r.url for r in dir_results if r.url.endswith(".php")]
    for page in php_pages:
        print_status(f"Found PHP page {page} — running param fuzz", level="found")
        ParamFuzzer(runner).run_get(page)


def run_single(runner: FfufRunner, args: argparse.Namespace) -> None:
    wordlist = args.wordlist

    if args.mode == "dir":
        DirectoryFuzzer(runner).run(args.target, *([wordlist] if wordlist else []))

    elif args.mode == "ext":
        ExtensionFuzzer(runner).run(args.target, *([wordlist] if wordlist else []))

    elif args.mode == "vhost":
        if not args.domain:
            print_status("--domain is required for vhost mode", level="warn")
            return
        VHostFuzzer(runner).run(args.target, args.domain, *([wordlist] if wordlist else []))

    elif args.mode == "params-get":
        ParamFuzzer(runner).run_get(args.target, *([wordlist] if wordlist else []))

    elif args.mode == "params-post":
        ParamFuzzer(runner).run_post(args.target, *([wordlist] if wordlist else []))


def main() -> None:
    parser = argparse.ArgumentParser(
        description="ffuf automation — point and shoot web fuzzing",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"modes: {', '.join(MODES)}"
    )
    parser.add_argument("target", help="Target URL (e.g. http://10.10.10.5)")
    parser.add_argument("-d", "--domain", help="Domain for vhost fuzzing (e.g. academy.htb)")
    parser.add_argument("-m", "--mode", choices=MODES, help="Run a single mode instead of full auto chain")
    parser.add_argument("-w", "--wordlist", help="Custom wordlist path (overrides default)")
    parser.add_argument("-t", "--threads", type=int, default=40, help="Threads (default: 40)")
    parser.add_argument("-x", "--proxy", help="Proxy URL (e.g. http://127.0.0.1:8080)")
    parser.add_argument("-p", "--delay", type=float, help="Delay between requests (e.g. 0.1)")

    args = parser.parse_args()

    print_banner(args.target)

    runner = build_runner(args)

    if args.mode:
        run_single(runner, args)
    else:
        run_auto(runner, args)


if __name__ == "__main__":
    main()
