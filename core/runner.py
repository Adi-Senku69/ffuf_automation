import tempfile
import subprocess


class FfufRunner:
    def __init__(self, threads: int = 40, proxy: str = None, delay: float = None):
        self.threads = threads
        self.proxy = proxy
        self.delay = delay

    def _build_base_args(self) -> list[str]:
        base_command = ["ffuf", "-t", str(self.threads)]
        if self.proxy is not None:
            base_command += ["-x", self.proxy]
        if self.delay is not None:
            base_command += ["-p", str(self.delay)]

        return base_command

    def run(self, args: list[str]) -> str:
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
            cmd = self._build_base_args(
            ) + ["-of", "json", "-o", tmp.name] + args

            with subprocess.Popen(cmd, stdout=subprocess.PIPE, text=True) as proc:
                for line in proc.stdout:
                    print(line, end="")

            return tmp.name
