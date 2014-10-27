# To be run by the developer's own user
export PYTHONUNBUFFERED="Y"
virtualenv virtual
source virtual/bin/activate
pip install -r /vagrant/requirements/dev.txt
curl -L get.rvm.io | bash -s stable
source /home/vagrant/.rvm/scripts/rvm
rvm install 1.9.3
rvm use 1.9.3
rvm gemset create xdiscovery_web
rvm gemset use xdiscovery_web
gem install compass
curl https://raw.githubusercontent.com/creationix/nvm/v0.10.0/install.sh | bash
source /home/vagrant/.nvm/nvm.sh
nvm install 0.10.20
nvm use 0.10.20
wget -qO- https://toolbelt.heroku.com/install-ubuntu.sh | sh
cd /vagrant
cat > .bowerrc <<EOF
{
    "analytics": false
}
EOF
npm install -g grunt-cli bower
pushd /vagrant/frontend/
npm install
bower update --config.interactive=false
fab create_db_local:create_role=1
