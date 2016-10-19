# Simple Let's Encrypt nginx docker image

Slendi is a simple docker image which sets up nginx with ssl using Let's Encrypt.

The default setup is to use nginx for reverse proxying, though it is possible to serve static files.

Slendi will automatically fetch certificates for the specified domains using Let's Encrypt's certbot. Certificates will automatically be renewed when they are about to expire.

# Using as a reverse proxy
Create a Dockerfile like so:

    FROM yalendi
    ADD config.json /etc/yalendi/config.json

And a config.json like this:

    [
        {
            'domains': 'mydomain.org',
            'proxy_ip': '127.0.0.1',
            'proxy_port': 8000
        }
    ]


Build the image

    $ docker build -t my_ssl_enabled_nginx .

and run with

    $ docker run -p 80:80 -p 443:443 -it my_ssl_enabled_nginx

Assuming the proxied service is running then https://mydomain.org should now work.

# Persisting certificates

Strictly not necessary...
