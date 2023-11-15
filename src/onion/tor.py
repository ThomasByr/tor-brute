import logging

import requests
import stem.control as stc
import stem.process as stp

__all__ = ["TorProxy"]


class TorProxy:
    def __init__(self) -> None:
        self.logger = logging.getLogger(".".join(__name__.split(".")[1:]))
        self.__port = 9050
        self.__tor_process = None

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
            self.logger.critical("failed to start Tor service (maybe stop service ?) ❌")
            raise e
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:  # noqa
        # Stop the Tor service
        self.__tor_process.kill()

    @property
    def port(self) -> int:
        """Return the socket port used by the Tor service (not the control port)"""
        return self.__port

    @property
    def ip(self) -> str:
        """Return the current ip used by the Tor service"""
        with requests.Session() as session:
            session.proxies = {
                "http": f"socks5h://localhost:{self.port}",  # Use Tor for HTTP connections
            }
            # http://httpbin.org/ip returns a json like:
            # b'{\n  "origin": "<IP>"\n}\n'
            r = session.get("http://httpbin.org/ip").content.decode("utf-8")
            return r.split("\n")[1].split('"')[3]

    def identity_swap(self) -> None:
        """Change the Tor identity"""
        ip_before = self.ip
        with stc.Controller.from_port(port=9051) as controller:
            controller.authenticate("my_password")  # hehe
            controller.signal(stc.Signal.NEWNYM)
        ip_after = self.ip

        self.logger.debug("Identity swap %s -> %s ♻️", ip_before, ip_after)
        if ip_before == ip_after:
            self.logger.critical("Tor identity swap failed ❌")