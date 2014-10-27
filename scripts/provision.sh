# To be run by the developer's own user
FRONTEND_DIR=/vagrant/frontend
BASE_DIR=/vagrant

cd $HOME

# python
export PYTHONUNBUFFERED="Y"
virtualenv $HOME/virtual
source $HOME/virtual/bin/activate
pip install -r $BASE_DIR/requirements/dev.txt

# ruby
curl -L get.rvm.io | bash -s stable
source $HOME/.rvm/scripts/rvm
rvm install 1.9.3
rvm use 1.9.3
rvm gemset create xdiscovery_web
rvm gemset use xdiscovery_web
gem install compass --version=0.12.7

# node
curl https://raw.githubusercontent.com/creationix/nvm/v0.10.0/install.sh | bash
source $HOME/.nvm/nvm.sh
nvm install 0.10.20
nvm use 0.10.20
# Dance to install node modules out of the shared directory
cp $FRONTEND_DIR/package.json $HOME
npm install -g grunt-cli bower
npm install
[ -d $FRONTEND_DIR/node_modules ] && mv $FRONTEND_DIR/node_modules $FRONTEND_DIR/node_modules_bak  # Just in case someone created it outside the VM
ln -s $HOME/node_modules $FRONTEND_DIR/node_modules

cd $BASE_DIR

# Init db and rcfiles
cat >> $HOME/.bash_profile <<EOF
cd /vagrant
EOF

# First build (includes a bower update run)
fab create_db_local:create_role=1 &&
fab dep
fab build
