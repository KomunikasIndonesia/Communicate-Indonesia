GAE_ZIP = google_appengine_1.9.24.zip
GAE_URL = https://storage.googleapis.com/appengine-sdks/featured/$(GAE_ZIP)
GAE_SERVER = tmp/google_appengine/dev_appserver.py

clean:
	rm -r lib/ venv/

venv:
	virtualenv venv

git-hooks:
	cp git_hooks/* .git/hooks/

install: git-hooks venv
	pip install -r requirements.txt -t lib/ --ignore-installed; \
	. venv/bin/activate; pip install flake8

create-tmp:
	mkdir -p tmp

gae-install: create-tmp
	curl $(GAE_URL) -o tmp/$(GAE_ZIP) -z tmp/$(GAE_ZIP); \
	unzip -o tmp/$(GAE_ZIP) -d tmp/

venv-install: create-tmp
	sudo pip install virtualenv

tool-install: gae-install venv-install

server:
	python $(GAE_SERVER) .

test:
	nosetests tests --with-gae --gae-lib-root=tmp/google_appengine

flake8:
	. venv/bin/activate; flake8 app tests --max-line-length=100
