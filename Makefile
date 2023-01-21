.PHONY: clean
clean:
	rm -rf env

.PHONY: prepare
prepare: clean
	virtualenv -p python3 env
	env/bin/pip install -r requirements.txt

.PHONY: run
run:
	env/bin/python run.py