# FROM ubuntu:22.04
FROM httpd:2.4.63

# Enable required Apache modules
RUN apt-get update && apt-get install -y apache2-utils apache2 

# Disable mpm_event and enable mpm_prefork by editing the httpd.conf directly
RUN sed -i '/mpm_event_module/d' /usr/local/apache2/conf/httpd.conf \
    && echo "LoadModule mpm_prefork_module modules/mod_mpm_prefork.so" >> /usr/local/apache2/conf/httpd.conf \
    && echo "IncludeOptional conf/extra/httpd-mpm.conf" >> /usr/local/apache2/conf/httpd.conf \
    && echo "LoadModule proxy_module modules/mod_proxy.so" >> /usr/local/apache2/conf/httpd.conf \
    && echo "LoadModule proxy_http_module modules/mod_proxy_http.so" >> /usr/local/apache2/conf/httpd.conf \
    && echo "Include conf/extra/apache-config.conf" >> /usr/local/apache2/conf/httpd.conf

# Copy custom config into the container
# COPY apache.conf /usr/local/apache2/conf/httpd.conf
COPY apache.conf /usr/local/apache2/conf/extra/apache-config.conf

# RUN a2enmod status

# /etc/apache2/mods-enabled/status.conf
# set ExtendedStatus to On
# <Location /server-status>, append  IP address to the line with the Allow directive. Example: 'Allow from 127.0.0.1 ::1 66.77.88.99'
# service apache2 restart

# or

# try: 'tail -f /var/log/apache2/access.log'

# Expose the port Apache will run on
EXPOSE 80
