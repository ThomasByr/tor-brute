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

You do not explicitly need a conda environment for the bot to run. But it is always recommended nontheless, especially because the next LTS of Ubuntu won't let users pip-install anything without a virtual environment. At the time of writing, this app `python >= 3.8` to run.

First, install the dependencies :

```bash
sudo apt-get update
sudo apt-get install tor
sudo service tor stop
```

Then clone the repository and cd into it :

```bash
# Clones the repository
git clone git@github.com:ThomasByr/tor-brute.git
cd tor-brute
```

You can create and activate a conda environment with the following commands (make sure to give it a name in [environment.yml](environment.yml)) :

```bash
# Creates environment and install dependencies
conda env create -f environment.yml -y
conda activate tor
```

Finally, run the app in the background with `nohup` and `tee` :

```bash
# Runs the app in the background
nohup python tor-brute.py 2>&1 | tee -a .log &
```

or in the foreground :

```bash
# Runs the app (lets you Ctrl+C to stop it)
python tor-brute.py
```

## 🔧 Usage

Simply create a `.cfg` file from [.cfg.example](.cfg.example) and fill it, then provide text files for both usernames and passwords.

```txt
username_or_password_part_1
username_or_password_part_2
username_or_password_part_3
...
```

<!-- markdownlint-disable MD051 -->

| argument            | hint                                  | default             |
| ------------------- | ------------------------------------- | ------------------- |
| `--help`            | show help message and exit            |                     |
| `--version`         | show program's version                |                     |
| `--debug`           | debug mode                            | `False`             |
| `--config`          | path to the config file               | `.cfg`              |
| `--users`           | path to the usernames file            | `assets/users.txt`  |
| `--passwd`          | path to the passwords file            | `assets/passwd.txt` |
| `--it-comb` [\*][1] | number of combination for user/passwd | `3, 2`              |

[1]: ## "a file with a, b, c with it-comb=2 would produce a, b, c, ab, ac, ba, bc, ca, cb"

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
  <summary>  alpha (click here to expand) </summary>

**v0.1** first public release

- use threads
- create a cli

</details>

## 🐛 Bugs and TODO

**TODO** (first implementation version)

- [x] add a simple cli

**Known Bugs** (latest fix)

- [ ] ...

## 🎨 Logo and Icons

Icon by Dewi Sari from [flaticon.com](https://www.flaticon.com/fr/auteurs/dewi-sari)

Unless otherwise stated, all icons and logos are made by the author.
Copyright (C) 2023 Thomas BOUYER, all rights reserved.

Tools used :

- [Microsoft Designer](https://designer.microsoft.com/)
- [Clip Studio Paint](https://www.clipstudio.net/en)
- [Canva](https://www.canva.com/)