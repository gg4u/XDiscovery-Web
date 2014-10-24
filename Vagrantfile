# -*- mode: ruby -*-
# vi: set ft=ruby :

# Vagrantfile API/syntax version. Don't touch unless you know what you're doing!
VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
  # All Vagrant configuration is done here. The most common configuration
  # options are documented and commented below. For a complete reference,
  # please see the online documentation at vagrantup.com.

  # Every Vagrant virtual environment requires a box to build off of.
  config.vm.box = "file://./package.box"

  # Disable automatic box update checking. If you disable this, then
  # boxes will only be checked for updates when the user runs
  # `vagrant box outdated`. This is not recommended.
  # config.vm.box_check_update = false

  # Create a forwarded port mapping which allows access to a specific port
  # within the machine from a port on the host machine. In the example below,
  # accessing "localhost:8080" will access port 80 on the guest machine.
  config.vm.network "forwarded_port", guest: 8000, host: 8000

  # Create a private network, which allows host-only access to the machine
  # using a specific IP.
  # config.vm.network "private_network", ip: "192.168.33.10"

  # Create a public network, which generally matched to bridged network.
  # Bridged networks make the machine appear as another physical device on
  # your network.
  # config.vm.network "public_network"

  # If true, then any SSH connections made will enable agent forwarding.
  # Default value: false
  # config.ssh.forward_agent = true

  # Share an additional folder to the guest VM. The first argument is
  # the path on the host to the actual folder. The second argument is
  # the path on the guest to mount the folder. And the optional third
  # argument is a set of non-required options.
  # config.vm.synced_folder "../data", "/vagrant_data"

  # Provider-specific configuration so you can fine-tune various
  # backing providers for Vagrant. These expose provider-specific options.
  # Example for VirtualBox:
  #
   config.vm.provider "virtualbox" do |vb|
     # Don't boot with headless mode
     #vb.gui = true

     # Use VBoxManage to customize the VM. For example to change memory:
     vb.customize ["modifyvm", :id, "--memory", "1024"]
     vb.customize ['modifyvm', :id, '--natdnshostresolver1', 'on']
   end
  #
  # View the documentation for the provider you're using for more
  # information on available options.

  # Enable provisioning with CFEngine. CFEngine Community packages are
  # automatically installed. For example, configure the host as a
  # policy server and optionally a policy file to run:
  #
  # config.vm.provision "cfengine" do |cf|
  #   cf.am_policy_hub = true
  #   # cf.run_file = "motd.cf"
  # end
  #
  # You can also configure and bootstrap a client to an existing
  # policy server:
  #
  # config.vm.provision "cfengine" do |cf|
  #   cf.policy_server_address = "10.0.2.15"
  # end

  # Enable provisioning with Puppet stand alone.  Puppet manifests
  # are contained in a directory path relative to this Vagrantfile.
  # You will need to create the manifests directory and a manifest in
  # the file default.pp in the manifests_path directory.
  #
  # config.vm.provision "puppet" do |puppet|
  #   puppet.manifests_path = "manifests"
  #   puppet.manifest_file  = "site.pp"
  # end

  # Enable provisioning with chef solo, specifying a cookbooks path, roles
  # path, and data_bags path (all relative to this Vagrantfile), and adding
  # some recipes and/or roles.
  #
  # config.vm.provision "chef_solo" do |chef|
  #   chef.cookbooks_path = "../my-recipes/cookbooks"
  #   chef.roles_path = "../my-recipes/roles"
  #   chef.data_bags_path = "../my-recipes/data_bags"
  #   chef.add_recipe "mysql"
  #   chef.add_role "web"
  #
  #   # You may also specify custom JSON attributes:
  #   chef.json = { :mysql_password => "foo" }
  # end

  # Enable provisioning with chef server, specifying the chef server URL,
  # and the path to the validation key (relative to this Vagrantfile).
  #
  # The Opscode Platform uses HTTPS. Substitute your organization for
  # ORGNAME in the URL and validation key.
  #
  # If you have your own Chef Server, use the appropriate URL, which may be
  # HTTP instead of HTTPS depending on your configuration. Also change the
  # validation key to validation.pem.
  #
  # config.vm.provision "chef_client" do |chef|
  #   chef.chef_server_url = "https://api.opscode.com/organizations/ORGNAME"
  #   chef.validation_key_path = "ORGNAME-validator.pem"
  # end
  #
  # If you're using the Opscode platform, your validator client is
  # ORGNAME-validator, replacing ORGNAME with your organization name.
  #
  # If you have your own Chef Server, the default validation client name is
  # chef-validator, unless you changed the configuration.
  #
  #   chef.validation_client_name = "ORGNAME-validator"
  config.vm.provision :shell, inline: <<SCRIPT
   sudo locale-gen en_US
   sudo apt-get install git python
   sudo apt-get install python-virtualenv
   virtualenv virtual
   source virtual/bin/activate
   #sudo apt-get install nvm
   curl https://raw.githubusercontent.com/creationix/nvm/v0.10.0/install.sh | bash
   sudo apt-get install postgresql-9.1
   sudo apt-get update
   sudo apt-get install lib
   sudo apt-get install postgresql-server-dev-9.1
   sudo apt-get install libjpeg-dev
   sudo apt-get install python2.7-dev
   sudo apt-get install libevent-dev
   sudo apt-get install libzmq-d
   sudo apt-get install libzmq-dev
   sudo apt-get install g++
   pip install -r /vagrant/requirements/dev.txt
   sudo apt-get install curl
   curl -L get.rvm.io | bash -s stable
   source /home/vagrant/.rvm/scripts/rvm
   rvm install 1.9.3
   rvm gemset create xdiscovery_web
   rvm gemset use xdiscovery_web
   cp /vagrant/scripts/.bash_profile ~
   source ~/.bash_profile
   nvm use 0.10.20
   gem install compass
   cd /vagrant/
   fab build
   sudo locale-gen it
   sudo service postgresql restart
   fab create_db_local:create_role=1
   59  fab restore
   60  fab restore_local
   63  fab restore_local
   64  PGPASSWORD=django pg_restore -n public --cluster 9.1/main -d xdimension_web -O -x -U django -h localhost -p 5432 ./backups/pgdump.db
   65  PGPASSWORD=django pg_restore -n public --cluster 9.1/main -O -x -U django -h localhost -p 5432 ./backups/pgdump.db
   66  python manage.py runserver
   67  nvm install 0.10.20
   68  cd /vagrant/frontend/
   69  npm install -g grunt
   70  npm install -g bower
   71  npm install -g grunt-cli
   72  nvm install
   73  npm install
   74  bower update
   75  sudo dpkg-reconfigure locales
   76  cd /vagrant/
   77  python manage.py runserver
   78  python manage.py runserver 0.0.0.0:8000
   79  python manage.py restore_local
   80  fab  restore_local
   81  python manage.py create_db_local
   82  fab create_db_local
   83  psql -u django
   84  psql -d xdimension_web
   85  psql -u django -d xdimension_web
   86  psql -U django -d xdimension_web
   87  PGPASSWORD=django psql -U django -d xdimension_web
   88  fab create_db_local:create_role=1
   89  PGPASSWORD=django psql -U django -d xdimension_web -h localhost
   90  sudo -u postgres psql
   91  PGPASSWORD=django psql -U django -d xdimension_web -h localhost
   92  fab create_db_local
   93  fab  restore_local
   94  sudo -u postgres psql
   95  fab create_db_local:create_role=1
   96  fab  restore_local
   97  sudo -u postgres psql
   98  fab create_db_local:create_role=1
   99  fab  restore_local
  100  python manage.py runserver 0.0.0.0:8000
  101  fab deploy:staging

end
