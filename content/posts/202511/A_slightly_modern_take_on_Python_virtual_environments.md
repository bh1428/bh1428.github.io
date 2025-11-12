+++
date = '2025-11-12T18:31:50+01:00'
draft = false
title = 'A slightly modern take on Python virtual environments'
+++
As developers we often work on multiple projects at the same time: while working on a new feature in a Django 5.2 project you quickly have to fix a bug in an older Django 4.2 application. [Python virtual environments](https://docs.python.org/3/tutorial/venv.html) enable us to separate these two tasks and seamlessly switch  between them. This article explores ways of handling virtual environments both in a classical and in a somewhat more modern way.

Examples in this article assume a [Debian](https://www.debian.org/) based Linux environment (like [Ubuntu](https://ubuntu.com/) running in Windows [WSL(2)](https://learn.microsoft.com/en-us/windows/wsl/)).

## Why use a virtual environment?

Before diving in, lets take a moment and find out what the advantages of virtual environments are. Why should we (always) use them?

When you _just_ install a package in Python (using [`pip`](https://docs.python.org/3/installing/index.html)) it is placed in the global `site-packages`: a location shared between all Python applications on a system. When Django 5.2 is installed, we are unable to work on our bug in Django 4.2 as we can only have one version in the global environment. Obviously, you can uninstall 5.2 (along with its dependencies!), install 4.2, fix the bug, uninstall 4.2, reinstall 5.2, etc... but this is simply too much trouble.

[Python virtual environments](https://docs.python.org/3/tutorial/venv.html) solve this problem by semi-isolating projects and their dependencies. Virtual environments use the same base interpreter but each one has its own `site-packages`. These local `site-packages` are (among other things) part of a projects `.venv` directory.

Some benefits with regard to virtual environments:

- **Dependency management**: prevent version conflicts by isolating versions of packages between projects.
- **Replicability**: a virtual environment can easily be recreated.
- **Python version**: the Python version can be switched by creating a new virtual environment with another base interpreter.
- **Simplified Cleanup**: the base Python installation stays clean; remove a project environment by _just_ deleting the virtual environment.

A virtual environment should not be part of your (Git) repository. Normally, a list of packages and their required version is added to version management but the virtual environment (directory) itself is excluded (e.g. add `.venv` to your `.gitignore`).

## Classical approach

### Installation

There are multiple ways of creating a virtual environment. Since Python 3.3 the [`venv`](https://docs.python.org/3/library/venv.html) module is part of the standard. Lets call the `venv` module the _classical approach_.

`venv` is part of the standard, you therefore need an active Python installation to use it. How to install Python is beyond the scope of this article; for more information see this excellent [RealPython Tutorial](https://realpython.com/installing-python/). For now, let's assume we have a working Python installation.

As a first step, create a folder for the project and secondly create the virtual environment in that folder:

```bash
mkdir ~/dj_42
cd ~/dj_42
python3 -m venv .venv
```

It may fail with an error like this:

```text
The virtual environment was not created successfully because ensurepip is not
available.  On Debian/Ubuntu systems, you need to install the python3-venv
package using the following command.

    apt install python3.12-venv

You may need to use sudo with that command.  After installing the python3-venv
package, recreate your virtual environment.

Failing command: /home/user/dj_42/.venv/bin/python3
```

In this case install the `python*-venv` package and try again (make sure to use the correct version of `python*-venv`):

```bash
sudo apt install python3.12-venv -y
python3 -m venv .venv
```

The `.venv` argument after `-m venv` is the folder where the virtual environment is created. You are free to choose whatever you want but `.venv` (or `venv`) is commonly used.

To use the virtual environment it has to be activated. On Linux activation works like this (for Windows, see [How venvs work](https://docs.python.org/3/library/venv.html#how-venvs-work)):

```bash
source .venv/bin/activate
```

The prompt changes: the name of the virtual environment folder is added. We can now install packages, lets install the latest Django 4.2:

```bash
pip install 'django~=4.2'
pip list
```

Example of the output:

```text
user@hostname:~/dj_42$ source .venv/bin/activate

(.venv) user@hostname:~/dj_42$ pip install 'django~=4.2'
Collecting django~=4.2
  Downloading django-4.2.26-py3-none-any.whl.metadata (4.2 kB)
Collecting asgiref<4,>=3.6.0 (from django~=4.2)
  Downloading asgiref-3.10.0-py3-none-any.whl.metadata (9.3 kB)
Collecting sqlparse>=0.3.1 (from django~=4.2)
  Downloading sqlparse-0.5.3-py3-none-any.whl.metadata (3.9 kB)
Downloading django-4.2.26-py3-none-any.whl (8.0 MB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 8.0/8.0 MB 47.4 MB/s eta 0:00:00
Downloading asgiref-3.10.0-py3-none-any.whl (24 kB)
Downloading sqlparse-0.5.3-py3-none-any.whl (44 kB)
   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 44.4/44.4 kB 4.2 MB/s eta 0:00:00
Installing collected packages: sqlparse, asgiref, django
Successfully installed asgiref-3.10.0 django-4.2.26 sqlparse-0.5.3

(.venv) user@hostname:~/dj_42$ pip list
Package  Version
-------- -------
asgiref  3.10.0
Django   4.2.26
pip      24.0
sqlparse 0.5.3
```

As a final step, we want to recreate the virtual environment easily. For this, we use the [`pip freeze`](https://pip.pypa.io/en/stable/cli/pip_freeze/) command to list all installed packages with their **exact** version. Common practice is to store the output of `pip freeze` in a file named `requirements.txt`:

```bash
pip freeze > requirements.txt
```

The `requirements.txt` should be included in the repository while the `.venv` folder is **not** included. Only `requirements.txt` is needed to recreate the virtual environment.

## Usage

A classic virtual environment has to be activated before it can be used. You have already seen the `activate` command during the installation. Lets get the version of Django:

```bash
cd ~/dj_42/
source .venv/bin/activate
python -m django version
```

Output:

```text
user@hostname:~$ cd ~/dj_42/
user@hostname:~/dj_42$ source .venv/bin/activate

(.venv) user@hostname:~/dj_42$ python -m django version
4.2.26
```

When done: close the terminal or use the `deactivate` command to deactivate the virtual environment.

## Recreation

As mentioned: one of the advantages of virtual environments is easy recreation. Lets try. First deactivate and remove:

```bash
deactivate
rm -rf ~/dj_42/.venv/
```

Then re-create a new (empty) virtual environment and install the packages again (using the [`pip install -r`](https://pip.pypa.io/en/stable/cli/pip_install/#cmdoption-r) command):

```bash
cd ~/dj_42/
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip list
```

For example:

```text
user@hostname:~$ cd ~/dj_42/
user@hostname:~/dj_42$ python3 -m venv .venv
user@hostname:~/dj_42$ source .venv/bin/activate

(.venv) user@hostname:~/dj_42$ pip install -r requirements.txt
Collecting asgiref==3.10.0 (from -r requirements.txt (line 1))
  Using cached asgiref-3.10.0-py3-none-any.whl.metadata (9.3 kB)
Collecting Django==4.2.26 (from -r requirements.txt (line 2))
  Using cached django-4.2.26-py3-none-any.whl.metadata (4.2 kB)
Collecting sqlparse==0.5.3 (from -r requirements.txt (line 3))
  Using cached sqlparse-0.5.3-py3-none-any.whl.metadata (3.9 kB)
Using cached asgiref-3.10.0-py3-none-any.whl (24 kB)
Using cached django-4.2.26-py3-none-any.whl (8.0 MB)
Using cached sqlparse-0.5.3-py3-none-any.whl (44 kB)
Installing collected packages: sqlparse, asgiref, Django
Successfully installed Django-4.2.26 asgiref-3.10.0 sqlparse-0.5.3

(.venv) user@hostname:~/dj_42$ pip list
Package  Version
-------- -------
asgiref  3.10.0
Django   4.2.26
pip      24.0
sqlparse 0.5.3
```

## Modern approach

In the paragraphs above we explored a classical approach using the `venv` module. This works, however a more contemporary approach would be to use [Astral's uv](https://docs.astral.sh/uv/).

`uv` is a single tool to replace `pip`, `pip-tools`, `pipx`, `poetry`, `pyenv`, `twine`, `virtualenv` and more. These are all other tools to manage virtual environments, each with their own (dis)advantages. Personally, I like [`pip-tools`](https://pip-tools.readthedocs.io/en/stable/), but thats a subject for another article. `uv` is also able to [installs and manage](https://docs.astral.sh/uv/#python-versions) Python versions: you do not need pre-installed Python interpreters anymore. As an added bonus, `uv` is much (10-100x) faster than `pip`: have your cake and eat it to!

Note: the approach as described here does not use `uv` options like [initialize a project](https://docs.astral.sh/uv/guides/projects/) and use a [`uv.lock`](https://docs.astral.sh/uv/guides/projects/#uvlock) file. The procedure as described here takes advantage of `uv` without going all-in into the [astral.sh](https://astral.sh/) ecosystem: you can still recreate an environment from a `requirements.txt` file using `pip`. We are just touching the surface of what `uv` really can do. Consult the excellent [documentation](https://docs.astral.sh/uv/) for the entire picture.

### Installation

You may not need pre-installed Python versions, but you do need to install `uv`. The standard [installation](https://docs.astral.sh/uv/#installation) expects you to `curl` a script and pipe it to `sh`. As always: check the script before _just_ piping it through `sh`!

Assuming `uv` is installed, lets create a Python 3.14 environment with Django 5.2 (supports 3.14 since 5.2.8):

```bash
mkdir ~/dj_52
cd ~/dj_52
uv venv --python 3.14
```

If Python 3.14 is not already available it will be downloaded. For an overview of available Python versions you can use [`uv python list`](https://docs.astral.sh/uv/concepts/python-versions/#viewing-available-python-versions).

We now have a normal virtual environment managed by `uv`. Lets install Django (using [`uv pip install`](https://docs.astral.sh/uv/pip/)):

```bash
uv pip install 'django>=5.2.8'
uv pip list
```

Output of the entire process:

```text
user@hostname:~$ mkdir ~/dj_52
user@hostname:~$ cd ~/dj_52

user@hostname:~/dj_52$ uv venv --python 3.14
Using CPython 3.14.0
Creating virtual environment at: .venv
Activate with: source .venv/bin/activate

user@hostname:~/dj_52$ uv pip install 'django>=5.2.8'
Resolved 3 packages in 11ms
Installed 3 packages in 519ms
 + asgiref==3.10.0
 + django==5.2.8
 + sqlparse==0.5.3

user@hostname:~/dj_52$ uv pip list
Package  Version
-------- -------
asgiref  3.10.0
django   5.2.8
sqlparse 0.5.3
```

Notice: although it is possible, we did not **need** to activate the virtual environment. `uv` will normally [automatically find and use the virtual environment](https://docs.astral.sh/uv/pip/environments/#using-a-virtual-environment).

Again, to recreate the virtual environment we need a `requirements.txt`. We now use [`uv pip freeze`](https://docs.astral.sh/uv/pip/inspection/#inspecting-environments) instead of [`pip freeze`](https://pip.pypa.io/en/stable/cli/pip_freeze/) (do you recognize the pattern for the `uv pip` interface?):

```bash
uv pip freeze > requirements.txt
```

As for the classical approach: `requirements.txt` should be included in the repository while the `.venv` folder is **not** included. Again, only `requirements.txt` is required to recreate the virtual environment. `uv` will create a `.venv/.gitignore` to assist you.

## Usage

When using a `uv` managed virtual environment you can use `uv run` instead of `python`:

```bash
cd ~/dj_52/
uv run -m django version
```

For example:

```text
user@hostname:~$ cd ~/dj_52/

user@hostname:~/dj_52$ uv run -m django version
5.2.8
```

## Recreation

Recreation of a virtual environment with `uv` is comparable to using the `venv` module. The main difference is that we use th `uv` tool for everything:

```bash
cd ~/dj_52/
rm -rf ~/dj_52/.venv/
uv venv --python 3.14
uv pip install -r requirements.txt
uv pip list
```

Output example:

```text
user@hostname:~/dj_52$ cd ~/dj_52/
user@hostname:~/dj_52$ rm -rf ~/dj_52/.venv/
user@hostname:~/dj_52$ uv venv --python 3.14
Using CPython 3.14.0
Creating virtual environment at: .venv
Activate with: source .venv/bin/activate
user@hostname:~/dj_52$ uv pip install -r requirements.txt
Resolved 3 packages in 41ms
Installed 3 packages in 547ms
 + asgiref==3.10.0
 + django==5.2.8
 + sqlparse==0.5.3
user@hostname:~/dj_52$ uv pip list
Package  Version
-------- -------
asgiref  3.10.0
django   5.2.8
sqlparse 0.5.3
```
