import logging
import signal
import sys
import time

import requests
import stem.control as stc
import stem.process as stp
from requests.exceptions import ConnectionError, Timeout

__all__ = ["TorProxy"]


class TorProxy:
    MAX_TRIES = 3

    def __init__(self) -> None:
        self.logger = logging.getLogger(".".join(__name__.split(".")[1:]))
        self.__consecutive_fails = 0
        self.__consecutive_exit_node_change_failures = 0
        self.__port = 9050
        self.__tor_process = None

        signal.signal(signal.SIGINT, self.__on_end)
        signal.signal(signal.SIGTERM, self.__on_end)

    def __enter__(self) -> "TorProxy":
        # Start the Tor service
        try:
            self.__tor_process = stp.launch_tor_with_config(
                config={
                    "SocksPort": str(self.port),
                    "ControlPort": "9051",
                    # beautiful password
                    "HashedControlPassword": "16:E600ADC1B52C80BB6022A0E999A7734571A451EB6AE50FED489B72E3DF",
                },
            )
        except OSError as e:
            self.logger.critical(
                "failed to start Tor service (maybe stop service ?) ❌\n%s", e
            )
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:  # noqa
        self.__tor_process.kill()

    def __on_end(self, signum, frame):  # noqa
        if self.__tor_process:
            self.__tor_process.kill()
        self.logger.warning(
            "Received signal %s, exiting ...", signal.Signals(signum).name
        )
        sys.exit(0)

    @property
    def port(self) -> int:
        """Return the socket port used by the Tor service (not the control port)"""
        return self.__port

    @property
    def ip(self) -> str:
        """Return the current ip used by the Tor service"""
        response: requests.Response = None
        try_no = 0

        with requests.Session() as session:
            session.proxies = {
                "http": f"socks5h://localhost:{self.port}",  # use Tor for HTTP connections
            }

            # 3 tries to connect to the target
            # connected if some response and status code is 200
            while try_no < self.MAX_TRIES and (
                not response or response.status_code != 200
            ):
                # http://httpbin.org/ip returns a json like:
                # b'{\n  "origin": "<IP>"\n}\n'
                try:
                    response = session.get("http://httpbin.org/ip", timeout=10)
                    if response and response.status_code == 200:
                        self.__consecutive_fails = 0
                except (ConnectionError, Timeout) as e:
                    self.logger.debug(
                        "exception [%s] : retrying ... (%d/%d)",
                        e.__class__.__name__,
                        try_no + 1,
                        self.MAX_TRIES,
                    )
                    time.sleep(1)  # wait to ~avoid~ spamming
                finally:
                    try_no += 1
            else:
                if not response or response.status_code != 200:
                    self.logger.error(
                        "failed multiple reconnect to httpbin.org (%d/%d) ❌",
                        self.__consecutive_fails,
                        self.MAX_TRIES,
                    )
                    if self.__consecutive_fails >= self.MAX_TRIES:
                        self.logger.critical(
                            "too many consecutive fails, exiting ... ❌"
                        )
                    return None
        return response.text.split("\n")[1].split('"')[3]

    def identity_swap(self) -> None:
        """Change the Tor identity"""
        ip_before = self.ip
        with stc.Controller.from_port(port=9051) as controller:
            controller.authenticate("my_password")  # hehe
            controller.signal(stc.Signal.NEWNYM)
        ip_after = self.ip if ip_before else None

        if ip_before and ip_after:
            self.logger.debug("exit node %s -> %s ♻️", ip_before, ip_after)
            if ip_before == ip_after:
                self.__consecutive_exit_node_change_failures += 1
                self.logger.warning(
                    "Tor exit node did not change while id swap (%d/%d) 🥷",
                    self.__consecutive_exit_node_change_failures,
                    self.MAX_TRIES,
                )
                if self.__consecutive_exit_node_change_failures >= self.MAX_TRIES:
                    self.logger.critical(
                        "too many consecutive exit node change failures, exiting ... ❌"
                    )
            else:
                self.__consecutive_exit_node_change_failures = 0
