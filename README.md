# <img src="assets/favicon.png" alt="icon" width="4%"/> tor-brute - Forms brute-forcer via Tor

[![GitHub license](https://img.shields.io/github/license/ThomasByr/tor-brute)](https://github.com/ThomasByr/tor-brute/blob/master/LICENSE)
[![GitHub commits](https://badgen.net/github/commits/ThomasByr/tor-brute)](https://GitHub.com/ThomasByr/tor-brute/commit/)
[![GitHub latest commit](https://badgen.net/github/last-commit/ThomasByr/tor-brute)](https://gitHub.com/ThomasByr/tor-brute/commit/)
[![Maintenance](https://img.shields.io/badge/maintained%3F-yes-green.svg)](https://GitHub.com/ThomasByr/tor-brute/graphs/commit-activity)

[![Python Package](https://github.com/ThomasByr/tor-brute/actions/workflows/python-package.yml/badge.svg)](https://github.com/ThomasByr/tor-brute/actions/workflows/python-package.yml)
[![GitHub release](https://img.shields.io/github/release/ThomasByr/tor-brute)](https://github.com/ThomasByr/tor-brute/releases/)
[![Author](https://img.shields.io/badge/author-@ThomasByr-blue)](https://github.com/ThomasByr)
[![Author](https://img.shields.io/badge/author-@ThomasD-blue)](https://github.com/LosKeeper)

1. [✏️ Setup](#️-setup)
2. [🔧 Usage](#-usage)
3. [🧑‍🏫 Contributing](#-contributing)
4. [⚖️ License](#️-license)
5. [🔄 Changelog](#-changelog)
6. [🐛 Bugs and TODO](#-bugs-and-todo)
7. [🎨 Logo and Icons](#-logo-and-icons)

> <picture>
>   <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/Mqxx/GitHub-Markdown/main/blockquotes/badge/light-theme/warning.svg">
>   <img alt="Warning" src="https://raw.githubusercontent.com/Mqxx/GitHub-Markdown/main/blockquotes/badge/dark-theme/warning.svg">
> </picture><br>
>
> Disclaimer : This is an educational project, please do not use it for illegal purposes. We are not responsible for any damage caused by the use of this project.

## ✏️ Setup

> <picture>
>   <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/Mqxx/GitHub-Markdown/main/blockquotes/badge/light-theme/info.svg">
>   <img alt="Info" src="https://raw.githubusercontent.com/Mqxx/GitHub-Markdown/main/blockquotes/badge/dark-theme/info.svg">
> </picture><br>
>
> Please note we do not officially support Windows or MacOS, but we do provide some instructions for those who want to use it on these platforms.

You do not explicitly need a conda environment for the bot to run. But it is always recommended nontheless, especially because the next LTS of Ubuntu won't let users pip-install anything without a virtual environment. At the time of writing, this app requires `python >= 3.8` to run.

First, install the dependencies :

```bash
sudo apt-get update
sudo apt-get install tor
sudo service tor stop  # the app will start its own tor instance
# or
# sudo systemctl disable tor
```

Then clone the repository and cd into it :

```bash
# Clones the repository
git clone git@github.com:ThomasByr/tor-brute.git
cd tor-brute
```

You can create and activate a conda environment with the following commands :

```bash
# Creates environment and install dependencies
conda env create -f environment.yml -y
conda activate tor
```

Finally, run the app in the background with `nohup` :

```bash
# Runs the app in the background
nohup python tor_brute.py &
```

or in the foreground :

```bash
# Runs the app (lets you Ctrl+C to stop it)
python tor_brute.py
```

## 🔧 Usage

Simply create a `.cfg` file from [.cfg.example](.cfg.example) and fill it, then provide text files for both usernames and passwords. The app will try every combination of usernames and passwords, and will issue a log record for each successful login. If you have a user file that looks like this :

```txt
foo
bar
baz
```

The app will try these usernames (for combinations of size 2) (note that if you use `--all`, the app will create permutations instead of combinations) :

```txt
foo
bar
baz
foobar
foobaz
barbaz
```

and for each one, try every password combination in the password file following the same logic.

Once you are all set, you can run the app with :

<!-- markdownlint-disable MD051 -->

| argument                  | hint                                       | default             |
| ------------------------- | ------------------------------------------ | ------------------- |
| `-h`, `--help`            | show help message and exit                 |                     |
| `-v`, `--version`         | show program's version                     |                     |
| `-d`, `--debug`           | debug mode                                 | `False`             |
| `-c`, `--config`          | path to the config file                    | `.cfg`              |
| `-u`, `--user`            | path to the usernames file                 | `assets/user.txt`   |
| `-p`, `--passwd`          | path to the passwords file                 | `assets/passwd.txt` |
| `-i`, `--iter` [\*][1]    | number of combination for user/passwd      | `3, 2`              |
| `-e`, `--each`            | change Tor ID each X requests (0 or >=100) | `1000`              |
| `-t`, `--timeout`         | timeout for http requests                  | `10`                |
| `-m`, `--max-tries`       | how much to _retry_ stuff                  | `3`                 |
| `-w`, `--threads` [\*][2] | number of threads                          | `50`                |
| `-s`, `--sleep`           | additional sleep time between each ID swap | `0`                 |
| `-a`, `--all`             | use permutations (unordered combination)   | `False`             |

[1]: ## "a file with a, b, c with iter=2 would produce a, b, c, ab, ac, ba, bc, ca, cb"
[2]: ## "too many threads might result in a server timeout"

<!-- markdownlint-enable MD051 -->

## 🧑‍🏫 Contributing

If you ever want to contribute, either request the contributor status, or, more manually, fork the repo and make a pull request !

We are using [black](https://github.com/psf/black) to format the code, so make sure you have it installed and run :

```ps1
black src
```

> The standard procedure is :
>
> ```txt
> fork -> git branch -> push -> pull request
> ```
>
> Note that we won't accept any PR :
>
> - that does not follow our Contributing Guidelines
> - that is not sufficiently commented or isn't well formated
> - without any proper test suite
> - with a failing or incomplete test suite

Happy coding ! 🙂

## ⚖️ License

> <picture>
>   <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/Mqxx/GitHub-Markdown/main/blockquotes/badge/light-theme/warning.svg">
>   <img alt="Warning" src="https://raw.githubusercontent.com/Mqxx/GitHub-Markdown/main/blockquotes/badge/dark-theme/warning.svg">
> </picture><br>
>
> This repository is an app and might be exported as a standalone binary. Working source code is licensed under AGPL, the text assets are unlicensed, images and logos have their own section. The following license only applies to the template itself and is not legal advice. <FONT COLOR="#ff0000"><u>The license of this repo does not apply to the resources used in it.</u></FONT> Please check the license of each resource before using them.

This project is licensed under the AGPL-3.0 new or revised license. Please read the [LICENSE](LICENSE.md) file. Additionally :

- Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.

- Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.

- Neither the name of the tor-brute authors nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.

```LICENSE
tor-brute - Forms brute-forcer via Tor
Copyright (C) 2023 ThomasByr AND LosKeeper

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
```

## 🔄 Changelog

Please read the [changelog](changelog.md) file for the full history !

<details>
  <summary>  first release (click here to expand) </summary>

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

</details>

## 🐛 Bugs and TODO

**TODO** (first implementation version)

- [x] add a simple cli (0.1.1)
- [ ] option to not use tor (?)
- [x] option to change Tor ID each X requests (would need to implement a catch-up mechanism because thread jobs are unordered) (v1.0.0-dev)
- [ ] option to use a running tor instance/service
- [ ] choose protocol (http, https, ssh, etc.)
- [x] dynamic change between `combinations` and `permutations` (v1.0.0-beta.1)

**Known Bugs** (latest fix)

- [ ] lagging threads are not catching up, especially when `ReadTimeout` is reached (interferes with Tor ID swap)
- [ ] sometimes, successfull logins are not reported, or are reported twice (might be fixed with separate sessions for each thread)

## 🎨 Logo and Icons

Icon by Dewi Sari from [flaticon.com](https://www.flaticon.com/fr/auteurs/dewi-sari)

Unless otherwise stated, all icons and logos are made by the author.
Copyright (C) 2023 Thomas BOUYER, all rights reserved.

Tools used :

- [Microsoft Designer](https://designer.microsoft.com/)
- [Clip Studio Paint](https://www.clipstudio.net/en)
- [Canva](https://www.canva.com/)
