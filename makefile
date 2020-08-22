#
# makefile for Visual Studio Code (VSC) based Python projects
#

# Make targets (can be used when calling make):
#   upgrade_pip_tools     upgrade pip and the pip-tools package
#   upgrade_requirements  upgrade *requirements.txt files without installing
#   upgrade_venv          upgrade pip-tools, *requirements.txt and install packages
#   sync                  synchronize venv with *requirements.txt (default target)
#   info                  show list of installed packages in the venv
#   clean                 remove virtual environment

# names (directories & files)
VENV_DIR := venv
VENV_CLEAN_DIRS := .mypy_cache __pycache__

# binaries / executables
CMD := "C:\Windows\System32\cmd.exe"
PYTHON := "C:\Program Files\Python38\python.exe"
VENV := .\$(VENV_DIR)\Scripts
VENV_ACTIVATE := $(VENV)\activate.bat
VENV_PYTHON := $(VENV)\python.exe
PIP := $(VENV)\pip.exe
PIP_SYNC := $(VENV)\pip-sync.exe
PIP_COMPILE := $(VENV)\pip-compile.exe

all: sync

.NOTPARALLEL:

$(VENV_ACTIVATE):
	$(PYTHON) -m venv $(VENV_DIR)
	$(VENV_PYTHON) -m pip install pip --upgrade
	$(VENV_PYTHON) -m pip install pip-tools
    ifeq (,$(wildcard requirements.txt))
		$(PIP_COMPILE) requirements.in
    endif
    ifeq (,$(wildcard dev-requirements.txt))
		$(PIP_COMPILE) dev-requirements.in
    endif
	$(PIP_SYNC) dev-requirements.txt

requirements.txt: $(VENV_ACTIVATE) requirements.in
	$(PIP_COMPILE) requirements.in

dev-requirements.txt: $(VENV_ACTIVATE) dev-requirements.in requirements.txt
	$(PIP_COMPILE) dev-requirements.in

.PHONY: upgrade_pip_tools
upgrade_pip_tools: $(VENV_ACTIVATE)
	$(VENV_PYTHON) -m pip install pip --upgrade
	$(VENV_PYTHON) -m pip install pip-tools --upgrade

.PHONY: upgrade_requirements
upgrade_requirements: $(VENV_ACTIVATE)
	$(PIP_COMPILE) requirements.in --upgrade
	$(PIP_COMPILE) dev-requirements.in --upgrade

.PHONY: sync
sync: $(VENV_ACTIVATE) dev-requirements.txt
	$(PIP_SYNC) dev-requirements.txt

.PHONY: upgrade_venv
upgrade_venv: upgrade_pip_tools upgrade_requirements sync
    
.PHONY: info
info: $(VENV_ACTIVATE)
	$(PIP) list

.PHONY: clean
clean:
	$(CMD) /c "FOR %%F IN ($(VENV_DIR) $(VENV_CLEAN_DIRS)) DO IF EXIST %%F rmdir /q /s %%F"
