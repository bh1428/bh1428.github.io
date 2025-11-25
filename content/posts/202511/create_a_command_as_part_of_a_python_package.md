+++
date = '2025-11-24T18:49:39+01:00'
draft = false
title = 'Create a command as part of a Python package'
tags = ['python', 'packaging', 'windows', 'console']
+++
The [Python Packaging User Guide][python_packaging_user_guide] describes how to create an [executable script][python_packaging_executable_script] as part of a Python package. The best know option is to declare a command in the `[project.scripts]` section of [`pyproject.toml`][python_packaging_pyproject.toml] for a script that runs in a console window. Lesser known is the `[project.gui-scripts]` table which allows you to create a GUI application without a console window (on Microsoft Windows). This article describes an entire walkthrough for both options.

<!--more-->
This article is mainly focussed on Microsoft Windows, as prerequisites:

- Have a [currently supported][python_version_support] version of Python installed.
- You should know how to use the _Windows Explorer_ and [open a Powershell window][open_powershell_window] in a certain folder.
- You should have basic knowledge how to create a Python package and use a [`pyproject.toml`][python_packaging_pyproject.toml] file (see [RealPython - Setting Up a Python Project With pyproject.toml][realpython_pyproject.toml]).

## Table of Contents <!-- omit in toc -->

- [Example project](#example-project)
- [Creating executable scripts](#creating-executable-scripts)

## Example project

First, lets build an example project. Create a project folder somewhere and start with a minimal `pyproject.toml`:

```toml
[project]
name = "package"
version = "0.1.0"
```

Create a `package` subfolder and mark it as a package by creating an empty `package\__init__py`.

Now, add a basic _Hello World_ using [`tkinter`][python_docu_tkinter] ([`package\hello_world.py`][hello_world.py]):
{{< code file="/posts/202511/create_a_command_as_part_of_a_python_package/hello_world.py" language="python" >}}

Finally, create a virtual environment and install the package in [editable mode][pip_editable_mode] (e.g. on Windows):

```powershell
python.exe -m venv .venv
.\.venv\Scripts\pip.exe install -e .
```

We can now start our `hello_world.py` from a (Powershell) commandline:

```powershell
.\.venv\Scripts\python.exe package\hello_world.py
```

Not very sophisticated, but it qualifies (barely) as a GUI application:

![Hello World Gui][hello_world_gui]

## Creating executable scripts

As described in [Creating executable scripts][python_packaging_executable_script], let's create commands as part of the package. Replace the `pyproject.toml` with this ([`pyproject.toml`][pyproject.toml]):
{{< code file="/posts/202511/create_a_command_as_part_of_a_python_package/pyproject.toml" language="toml" >}}

Update the _editable installation_:

```powershell
.\.venv\Scripts\pip.exe install -e .
```

The update will create two executables (e.g. on Windows):

1. `.venv\Scripts\gui-console.exe`: execution **with** a console window
2. `.venv\Scripts\gui-no-console.exe`: execution **without** a console window

Try double clicking the executables in _Windows Explorer_, the first will open a console window and the GUI, the second only the GUI without a console window. Note: you don't need to activate a virtual environment manually; you can just double click.

[hello_world_gui]: /posts/202511/create_a_command_as_part_of_a_python_package/hello_world_gui.png
[hello_world.py]: /posts/202511/create_a_command_as_part_of_a_python_package/hello_world.py
[open_powershell_window]: https://stackoverflow.com/a/6599296
[pip_editable_mode]: https://pip.pypa.io/en/stable/cli/pip_install/#cmdoption-e
[pyproject.toml]: /posts/202511/create_a_command_as_part_of_a_python_package/pyproject.toml
[python_docu_tkinter]: https://docs.python.org/3/library/tkinter.html
[python_packaging_executable_script]: https://packaging.python.org/en/latest/guides/writing-pyproject-toml/#creating-executable-scripts
[python_packaging_pyproject.toml]: https://packaging.python.org/en/latest/guides/writing-pyproject-toml/
[python_packaging_user_guide]: https://packaging.python.org/en/latest/
[python_version_support]: https://devguide.python.org/versions/
[realpython_pyproject.toml]: https://realpython.com/python-pyproject-toml/
