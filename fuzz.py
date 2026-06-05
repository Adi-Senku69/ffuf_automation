#!/usr/bin/env python3
import argparse
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor
from core.runner import FfufRunner
from modes.directory import DirectoryFuzzer
from modes.extensions import ExtensionFuzzer
from modes.vhost import VHostFuzzer
from modes.params import ParamFuzzer
from ui.display import print_banner, print_status

MODES = ["dir", "ext", "vhost", "params-get", "params-post"]

EXAMPLES = """
examples:
  # Full auto recon (dir + vhost in parallel, then param fuzz discovered php pages)
  python fuzz.py http://10.10.10.5

  # Auto recon with vhost discovery
  python fuzz.py http://10.10.10.5 -d academy.htb

  # Vhost with custom host pattern (e.g. preprod-FUZZ.trick.htb)
  python fuzz.py http://trick.htb -d trick.htb --host-pattern "preprod-FUZZ.trick.htb" -m vhost

  # Single mode with custom wordlist
  python fuzz.py http://10.10.10.5 -m dir -w /usr/share/seclists/Discovery/Web-Content/raft-medium-files.txt

  # Through Burp proxy
  python fuzz.py http://10.10.10.5 -x http://127.0.0.1:8080

default wordlists (from /usr/share/seclists/):
  dir        Discovery/Web-Content/DirBuster-2007_directory-list-2.3-small.txt
  ext        Discovery/Web-Content/web-extensions.txt
  vhost      Discovery/DNS/subdomains-top1million-5000.txt
  params     Discovery/Web-Content/burp-parameter-names.txt
"""


def build_runner(args: argparse.Namespace) -> FfufRunner:
    return FfufRunner(
        threads=args.threads,
        proxy=args.proxy,
        delay=args.delay,
    )


def run_auto(runner: FfufRunner, args: argparse.Namespace) -> None:
    tasks = {}
    runner.parallel_mode = True
    executor = ThreadPoolExecutor()
    try:
        wl = args.wordlist
        tasks["dir"] = executor.submit(
            DirectoryFuzzer(runner).run, args.target, *([wl] if wl else [])
        )
        if args.domain:
            tasks["vhost"] = executor.submit(
                VHostFuzzer(runner).run, args.target, args.domain,
                *([wl] if wl else []),
                **{"host_pattern": args.host_pattern}
            )
        executor.shutdown(wait=True)
    except KeyboardInterrupt:
        executor.shutdown(wait=False)
        print_status("Scan interrupted", level="warn")
        return
    finally:
        runner.parallel_mode = False

    dir_results = tasks["dir"].result()

    # Dir fuzz any discovered vhosts
    if "vhost" in tasks:
        scheme = urlparse(args.target).scheme
        vhost_results = tasks["vhost"].result()
        for r in vhost_results:
            if r.fuzz_value:
                vhost_url = f"{scheme}://{r.fuzz_value}"
                print_status(f"Discovered vhost {r.fuzz_value} — running dir fuzz", level="found")
                dir_results += DirectoryFuzzer(runner).run(vhost_url, *([wl] if wl else []))

    # Param fuzz discovered php pages
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
        VHostFuzzer(runner).run(
            args.target, args.domain,
            *([wordlist] if wordlist else []),
            host_pattern=args.host_pattern
        )

    elif args.mode == "params-get":
        ParamFuzzer(runner).run_get(args.target, *([wordlist] if wordlist else []))

    elif args.mode == "params-post":
        ParamFuzzer(runner).run_post(args.target, *([wordlist] if wordlist else []))


def main() -> None:
    parser = argparse.ArgumentParser(
        description="ffuf-automation — point and shoot web fuzzing for CPTS",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=EXAMPLES,
    )
    parser.add_argument("target",
        help="Target URL (e.g. http://10.10.10.5)")
    parser.add_argument("-d", "--domain",
        help="Domain for vhost fuzzing (e.g. academy.htb)")
    parser.add_argument("-m", "--mode", choices=MODES,
        help="Single mode instead of full auto chain: " + ", ".join(MODES))
    parser.add_argument("-w", "--wordlist",
        help="Custom wordlist path — overrides the default for the selected mode")
    parser.add_argument("-t", "--threads", type=int, default=40,
        help="Number of threads (default: 40)")
    parser.add_argument("-x", "--proxy",
        help="Proxy URL (e.g. http://127.0.0.1:8080 for Burp)")
    parser.add_argument("-p", "--delay", type=float,
        help="Delay between requests in seconds (e.g. 0.1)")
    parser.add_argument("--host-pattern",
        help="Custom Host header pattern for vhost (e.g. preprod-FUZZ.trick.htb)")

    args = parser.parse_args()

    print_banner(args.target)

    runner = build_runner(args)

    if args.mode:
        run_single(runner, args)
    else:
        run_auto(runner, args)


if __name__ == "__main__":
    main()
