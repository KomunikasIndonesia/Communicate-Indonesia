GAE_ZIP = google_appengine_1.9.24.zip
GAE_URL = https://storage.googleapis.com/appengine-sdks/featured/$(GAE_ZIP)
GAE_SERVER = tmp/google_appengine/dev_appserver.py
GAE_CFG = tmp/google_appengine/appcfg.py

clean:
	rm -rf lib/ venv/

venv:
	virtualenv venv

git-hooks:
	cp git_hooks/* .git/hooks/

install: clean git-hooks venv
	pip install -r requirements.txt -t lib/ --ignore-installed; \
	. venv/bin/activate; \
	pip install requests; pip install requests[security]; \
	pip install flake8; \
	pip install nose; \
	pip install nosegae;\
	pip install mock;

create-tmp:
	rm -rf tmp; mkdir -p tmp

gae-install: create-tmp
	curl $(GAE_URL) -o tmp/$(GAE_ZIP) -z tmp/$(GAE_ZIP); \
	unzip -o tmp/$(GAE_ZIP) -d tmp/

venv-install:
	sudo pip install virtualenv

tool-install: gae-install venv-install

server:
	python $(GAE_SERVER) .

test:
	. venv/bin/activate; \
	nosetests tests --with-gae --gae-lib-root=tmp/google_appengine --logging-level=INFO

flake8:
	. venv/bin/activate; flake8 app tests pcurl.py --max-line-length=100

release-staging:
	mv app.yaml app.yaml.orig; \
	cat app.yaml.orig | sed -e "s/application.*/application : communicate-indonesia-staging/g" > app.yaml; \
	python $(GAE_CFG) update .; \
	mv app.yaml.orig app.yaml;
