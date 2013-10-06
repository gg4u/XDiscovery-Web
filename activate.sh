# activate the development environment
source ~/.bash_profile
export PATH=$(pwd)/frontend/node_modules/.bin:$PATH
pyenv local 2.7.5 && pyenv rehash
source virtual/bin/activate
source virtualnode/bin/activate
rvm use 1.9.3
rvm gemset use xdimension_web
