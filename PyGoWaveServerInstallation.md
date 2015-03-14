# Introduction #

Although this application is not in a production-quality state at this time, you may want to run a PyGoWave Server on your own testing environment.

PyGoWave Server will be abbreviated PGWS in the following text.

These are the installation steps I have taken to get PGWS running. While all components of PGWS are completely platform-independent, I stick to a Linux installation for now.

# Arch Linux service #

For those of you who are also running this nifty little linux distribution, you can install all of PGWS' required packages from the main or the user repository (AUR).

Packages from the main repository:
```
mysql apache django mysql-python python-lxml pil
```

Packages from the user repository:
```
rabbitmq rabbitmq-stomp carrot orbited django-registration

Optional:
django-rosetta
```

# Step-by-Step #

PGWS is powered by Django, MySQL, Apache, RabbitMQ and Orbited. Additionally some python libraries must be installed for proper operation.

**A warning/information in advance: You will set up a localhost environment that should not be reachable from the web. If you want to do so you are advised to change all database names, usernames and passwords throughout this document for your security.**

## Files and folders ##

My [Linux distribution](http://www.archlinux.org/) keeps Apache's settings in /etc/httpd/conf/httpd.conf this may differ for your distribution. Apache's root folder for serving files is /srv/http and PGWS thus is installed at /srv/http/pygowave\_project. If you see those paths in any settings file, make sure to check them. I consequently avoided using absolute paths in any template or script file so you should be save to just check those configs and settings files.

## MySQL ##

I use [MySQL 5.1.37](http://www.mysql.com/) as database backend. Install it and create a database named "pygowave". Then add a user "pygowave" with password "pygowave" and grant him all rights on the "pygowave" database.

You can do this by running "`mysql -u root -p`" from a shell. After entering your root password, execute the following commands:
```
CREATE DATABASE `pygowave`;
CREATE USER 'pygowave'@'localhost' IDENTIFIED BY 'pygowave';
GRANT ALL PRIVILEGES ON `pygowave`.* TO 'pygowave'@'localhost' WITH GRANT OPTION;
```

## Django ##

[Django 1.1](http://www.djangoproject.com/) is used to serve all dynamically generated websites of PGWS plus the storage and management of PGWS data model. Just install it with a package manager of your choice or by compiling from source.

[django-registration](http://bitbucket.org/ubernostrum/django-registration/wiki/Home) formerly was included in PGWS. It is now a dependency. Check out it's homepage for installation instructions.

## Apache ##

The PyGoWave test server runs on [Apache 2.2.11](http://httpd.apache.org/); you will also need a current release of [mod\_python](http://www.modpython.org/) or mod\_wsgi. This is needed for Django to run on top of Apache.

Snippet from my Apache configuration for PGWS:
```
<Location /pygowave>
  SetHandler python-program
  PythonHandler django.core.handlers.modpython
  SetEnv DJANGO_SETTINGS_MODULE settings
  PythonOption django.root /pygowave
  PythonDebug On
  PythonInterpreter pygowave_django
  PythonPath "['/srv/http/pygowave_project'] + sys.path"
</Location>

Alias /pygowave/media /srv/http/pygowave_project/media
<Location "/pygowave/media">
  SetHandler None
  Options Indexes FollowSymLinks
  Order allow,deny
  Allow from all
</Location>

ProxyRequests Off
ProxyPass /static http://localhost:9000/static
ProxyPass /tcp http://localhost:9000/tcp
```

To enable images and styles in Django's admin interface you might also need the following lines:
```
Alias /admin/media /usr/lib/python2.6/site-packages/django/contrib/admin/media
<Directory /usr/lib/python2.6/site-packages/django/contrib/admin/media>
  Order allow,deny
  Allow from all
</Directory>
<Location "/admin/media">
  SetHandler None
</Location>
```
Change paths as appropriate for your system.

## Orbited ##

[Orbited 0.7.9](http://orbited.org/) is the middleware which is used to connect your Browser continuosly to PGWS' message handler. Just follow the steps given on its homepage.

After that, set up /etc/orbited.cfg like this:
```
[global]
reactor=epoll
pid.location=/var/run/orbited.pid
user=http
group=http
proxy.enabled=1

[listen]
http://localhost:9000

[access]
* -> localhost:61613

[logging]
debug=SCREEN,/var/orbited/debug.log
info=SCREEN,/var/orbited/info.log
access=SCREEN,/var/orbited/info.log
warn=SCREEN,/var/orbited/error.log
error=SCREEN,/var/orbited/error.log

enabled.default=info,access,warn,error

[loggers]
Daemon=info,access,warn,error
TCPConnection=info,access,warn,error
```
Change "user=" and "group=" to your Apache's user and group. This is "apache2" on some systems.

## RabbitMQ ##

[RabbitMQ 1.6.0](http://www.rabbitmq.com/server.html) is a huge scalable message queueing system written in Erlang. All of PGWS asynchronous communication flows through it. Please install it first.

After going through normal installation, you need the rabbitmq-stomp gateway. Its best to get the code via mercurial:
```
hg clone -r rabbitmq_v1_6_0 http://hg.rabbitmq.com/rabbitmq-stomp
```
If you don't want to install mercurial there is also this [link](http://hg.rabbitmq.com/rabbitmq-stomp/archive/6d49eaa2fc25.tar.gz) to get a tarball of that release.

(Note: The compatibility issue with RabbitMQ 1.6.0 is now resolved)

As said in the README you need to compile rabbitmq-stomp like this:
```
cd rabbitmq-stomp
make RABBIT_SERVER_INCLUDE_DIR=/usr/lib/erlang/lib/rabbitmq_server-1.6.0/include
mkdir -p /usr/lib/erlang/lib/rabbitmq-stomp
cp -R * /usr/lib/erlang/lib/rabbitmq-stomp
```
Paths again depending on your installation.

Next, set up your /etc/rabbitmq/rabbitmq.conf
```
NODENAME=rabbit
NODE_IP_ADDRESS=0.0.0.0
NODE_PORT=5672

LOG_BASE=/var/log/rabbitmq
MNESIA_BASE=/var/lib/rabbitmq/mnesia

SERVER_START_ARGS='
  -pa /usr/lib/erlang/lib/rabbitmq-stomp/ebin
  -rabbit
    stomp_listeners [{"0.0.0.0",61613}]
    extra_startup_steps [{"STOMP-listeners",rabbit_stomp,kickstart,[]}]'
```
The last part is important for rabbitmq-stomp to work correctly.

Check if everything went fine by invoking rabbitmq-server (as root). It should print something like that:
```
RabbitMQ 1.6.0 (AMQP 8-0)
Copyright (C) 2007-2009 LShift Ltd., Cohesive Financial Technologies LLC., and Rabbit Technologies Ltd.
Licensed under the MPL.  See http://www.rabbitmq.com/

node        : rabbit@arche
log         : /var/log/rabbitmq/rabbit.log
sasl log    : /var/log/rabbitmq/rabbit-sasl.log
database dir: /var/lib/rabbitmq/mnesia/rabbit

starting database             ...done
starting core processes       ...done
starting recovery             ...done
starting persister            ...done
starting guid generator       ...done
starting builtin applications ...done
starting TCP listeners        ...done
starting STOMP-listeners      ...done

broker running
```

Don't quit it right now, log into another shell instead. You need to create a client and server account on RabbitMQ for PGWS. To do so invoke the following commands. **Important note:** You may change the server password here for security, but do not change the client password.
```
rabbitmqctl change_password guest $RANDOM$RANDOM$RANDOM
rabbitmqctl add_user pygowave_client pygowave_client
rabbitmqctl add_user pygowave_server pygowave_server
rabbitmqctl set_permissions pygowave_client '^[^.]+\.[^.]+\.waveop$|^wavelet.direct$' '^[^.]+\.[^.]+\.(waveop|clientop)$|^wavelet.topic$' '^[^.]+\.[^.]+\.(clientop|waveop)$|^wavelet.direct$'
rabbitmqctl set_permissions pygowave_server '^[^.]+\.[^.]+\.waveop$|^wavelet_rpc_singlethread$|^wavelet\.(topic|direct)$' '^[^.]+\.[^.]+\.waveop$|^wavelet_rpc_singlethread$|^wavelet\.direct$' '^[^.]+\.[^.]+\.waveop$|^wavelet_rpc_singlethread$|^wavelet\.(topic|direct)$'
```

Take a break and relax, you just mastered the hardest part of PGWS' installation :D

## Other Python libraries ##

You need to install the following Python libraries for PGWS to operate:
  * [lxml 2.2.2](http://codespeak.net/lxml/)
  * [mysql-python 1.2.3](http://sourceforge.net/projects/mysql-python/files/)
  * [PIL 1.1.6](http://www.pythonware.com/products/pil/index.htm)
  * [carrot 0.5.1](http://pypi.python.org/pypi/carrot/0.5.1)

## Get PyGoWave Server ##

Now that you have set up all dependencies, checkout PGWS from Google Code:
```
cd /srv/http
svn checkout http://pygowave-server.googlecode.com/svn/tags/alpha_0.3 pygowave_project
```

This installs the **alpha 0.3** release. You can switch to newer releases as they become available.

## Check your settings.py ##

Change to PGWS' directory and open settings.py in a text editor (preferrably vim) and check all those settings. Then type:
```
python manage.py syncdb
```
This creates all the tables used for PGWS' object model. It may also ask you to create a superuser account.

## Set permissions on cache & upload directories ##

PGWS uses some directories for caching and uploaded files. You must set permissions of your Apache to make this work; again the Apache user is "http" or "apache2" depending on your distribution.
```
chown http media/gadgets media/avatars pygowave_client/cache locale pygowave_client/locale
```

## You should be all set now! ##

Start up Orbited, RabbitMQ and Apache.

Finally start up the RPC server by invoking the following command in PGWS' directory:
```
./launch-pygowave-rpc
```

If today was your lucky day, you can access your PyGoWave Server at http://localhost/pygowave. Have fun!