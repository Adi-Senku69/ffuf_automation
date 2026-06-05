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
