import time
import tempfile
import subprocess
from rich.console import Console

console = Console()


class FfufRunner:
    def __init__(self, threads: int = 40, proxy: str = None, delay: float = None):
        self.threads = threads
        self.proxy = proxy
        self.delay = delay
        self.parallel_mode = False

    def _build_base_args(self) -> list[str]:
        base_command = ["ffuf", "-t", str(self.threads)]
        if self.proxy is not None:
            base_command += ["-x", self.proxy]
        if self.delay is not None:
            base_command += ["-p", str(self.delay)]
        return base_command

    def run(self, args: list[str], description: str = "Fuzzing...") -> str:
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
            cmd = self._build_base_args() + ["-of", "json", "-o", tmp.name] + args
            start = time.time()
            if self.parallel_mode:
                console.log(f"[cyan]▶ {description}[/cyan]")
                subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            else:
                with console.status(f"[cyan]{description}[/cyan]"):
                    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            console.log(f"[green]✓ {description} — done in {time.time() - start:.1f}s[/green]")
            return tmp.name
