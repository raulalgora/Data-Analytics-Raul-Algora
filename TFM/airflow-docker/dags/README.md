Algunas cosas importantes a tener en cuenta:

Importante utilizar version de python 3.11 porque si no Airflow da error

hay que instalar previamente openssl.

Como ejecutar por tanto:


$ brew install openssl
$ export LDFLAGS="-L$(brew --prefix openssl@1.1)/lib"
$ export CPPFLAGS="-I$(brew --prefix openssl@1.1)/include"

