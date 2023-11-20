# Changelog

<summary>The full history, or so was I told...</summary>

## alpha

**v0.1** first public release

- use threads
- create a cli
- unique progression bar for all users (so this is not spammy)
- removed color and emotes from streams that don't support it

**v0.2** misc refactors

- use `argparse` instead of `sys.argv`
- better formula to count combinations
- beautify code and error messages/handling
- account for `ReadTimeout` in `requests` (and other errors)
- account for ip check failure, successive failures, and exit node unchanged
- `logging.critical` sends SIGTERM to all threads and shows cursor back

## first release

**v1.0** beta candidate (1.0.0-dev)

- add option to change Tor ID each X requests
- new `TupleGenerator` that yields products of combinations
- renew http session each Tor ID swap
- `ThreadPool` is not closed/joined/terminated/deleted and then recreated anymore ! we use POSIX condition variables !
- somehow improved performance by 6.9% (not sure how)
- RAM usage does not seem to increase anymore (to be confirmed)
- consistent naming for variables and files
- next up: beta, release candidate, and release (drastic changes should only happen between beta and release candidate)

**v1.0** beta (1.0.0-beta.1 and 1.0.1-beta.1)

- `-t` for timeout, the maximum number of seconds to wait for one request
- `-m` for max retries, the maximum number of retries for one request, as well as the maximum number of consecutive failures before shutting down
- `-w` for workers of threads, pretty self-explanatory
- `-s` for sleep, the amount of seconds to wait between each Tor ID swap
- `-a` for use_all or all, to use permutations instead of combinations in generators
- each worker has its own session (no more shared session) and is renewed each Tor ID swap

**v1.0** candidate (1.0.1-rc1)

- no breaking changes here
- few bug fixes and minor refactors
- opened Tor proxy to http and https (this should not slow down the process)
- faster thread identification (no more `threading.current_thread().name.split('-')[1].split(' ')[0]`)

**v1.0** release (1.0.1)

- config file checkers
