.PHONY: init install lock install-dev

init:
	pip install --upgrade pip setuptools wheel
	pip install pip-tools

install:  # install run-time requirements
	pip install -r requirements.txt

lock:  # generate new hashes for requirement files
	pip-compile --generate-hashes --output-file requirements.txt requirements.in
	pip-compile --generate-hashes --output-file requirements-dev.txt requirements-dev.in

install-dev:  # Install development requirements
	pip install -r requirements-dev.txt
