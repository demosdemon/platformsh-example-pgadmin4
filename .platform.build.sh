#!/bin/sh

NVM_INSTALL_VERSION=${NVM_INSTALL_VERSION:-v0.33.11}
NODE_INSTALL_VERSION=${NODE_INSTALL_VERSION:-v10.14.2}

# install nvm because javascript dependencies require >=8.0.0, and Platform.sh
# python images ship with node 6.x
unset NPM_CONFIG_PREFIX
curl -s -o- https://raw.githubusercontent.com/creationix/nvm/${NVM_INSTALL_VERSION}/install.sh | sh
export NVM_DIR="$HOME/.nvm"
[ -e "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"
nvm current
nvm install ${NODE_INSTALL_VERSION}
nvm use ${NODE_INSTALL_VERSION}

set -ex

# upgrade pip using `python -m pip` notation due to a bug where sometimes pip
# cannot find itself after replacing its main executable
python -m pip install -U pip setuptools wheel
pip install -U gunicorn

cd pgadmin4 || exit 1
pip install -U Sphinx
pip install -r requirements.txt
make -C docs/en_US -f Makefile.sphinx html

cd web || exit 1
npm install -g yarn
yarn install
yarn bundle
# remove nvm and node dependencies now that static content has been build
rm -r ./node_modules "$NVM_DIR"

# precompile all python code files to speed up access times
python -O -m compileall .

cd "$HOME"
python -O -m compileall config_local.py
