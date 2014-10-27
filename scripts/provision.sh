# To be run by the developer's own user
export PYTHONUNBUFFERED="Y"

# python
virtualenv virtual
source virtual/bin/activate
pip install -r /vagrant/requirements/dev.txt

# ruby
curl -L get.rvm.io | bash -s stable
source /home/vagrant/.rvm/scripts/rvm
rvm install 1.9.3
rvm use 1.9.3
rvm gemset create xdiscovery_web
rvm gemset use xdiscovery_web
gem install compass

# node
curl https://raw.githubusercontent.com/creationix/nvm/v0.10.0/install.sh | bash
source /home/vagrant/.nvm/nvm.sh
nvm install 0.10.20
nvm use 0.10.20
cd /vagrant
cat > .bowerrc <<EOF
{
    "analytics": false
}
EOF
pushd /vagrant/frontend
rm -rf node_modules  # Just in case someone created it outside the VM
npm install -g grunt-cli bower
npm install  # Installing into current folder is the only way to please grunt...
bower update --config.interactive=false
popd

# Init db and rcfiles
fab create_db_local:create_role=1 &&
cat >> /home/vagrant/.bash_profile <<EOF
cd /vagrant
EOF
