FROM debian:jessie

MAINTAINER Knut Saua Mathiesen "knut@saua.no"

ENV NGINX_VERSION 1.11.5-1~jessie

RUN apt-key adv --keyserver hkp://pgp.mit.edu:80 --recv-keys 573BFD6B3D8FBC641079A6ABABF5BD827BD9BF62 \
	&& echo "deb http://nginx.org/packages/mainline/debian/ jessie nginx" >> /etc/apt/sources.list \
	&& apt-get update \
	&& apt-get install --no-install-recommends --no-install-suggests -y \
						ca-certificates \
						nginx=${NGINX_VERSION} \
						nginx-module-xslt \
						nginx-module-geoip \
						nginx-module-image-filter \
						nginx-module-perl \
						nginx-module-njs \
						gettext-base \
                        python3 \
	&& rm -rf /var/lib/apt/lists/*


# forward request and error logs to docker log collector
RUN ln -sf /dev/stdout /var/log/nginx/access.log \
	&& ln -sf /dev/stderr /var/log/nginx/error.log

# Install certbot
RUN echo "deb http://httpredir.debian.org/debian jessie-backports main" >> /etc/apt/sources.list \
    && apt-get update \
    && apt-get install -t "jessie-backports" --no-install-suggests -y certbot

# Use slendi's nginx.config
ADD nginx.conf /etc/nginx/nginx.conf

# Copy over slendi's required files
ADD nginx_site_template.conf /var/slendi/nginx_site_template.conf
ADD slendi.py /usr/bin/slendi
RUN chmod 550 /usr/bin/slendi

EXPOSE 80 443

# CMD ["nginx", "-g", "daemon off;"]
CMD ["/usr/bin/slendi"]
