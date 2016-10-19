#!/usr/bin/python3
import sys, subprocess, os, threading
from functools import reduce

NGINX_LETS_ENCRYPT_WEBROOT="/var/slendi/webroot"
DEFAULT_NGINX_SITE_TEMPLATE="/var/slendi/nginx_site_template.conf"
SLENDI_CONFIG="/etc/slendi/config.json"

class StreamLinePrefixer:
    """Takes a given stream and prefixes each line with the given prefix before outputting to stdout/stderr"""
    def __init__(self, stream, prefix, stderr=False):
        self.stream = stream
        self.prefix = prefix
        if stderr:
            self.outputstream = sys.stderr
        else:
            self.outputstream = sys.stdout
        self.thread = threading.Thread(target = self.run)
        self.thread.start()

    def run(self):
        for line in self.stream:
            print("%s %s" % (self.prefix, line.decode("UTF-8").strip()), file=self.outputstream)

def popen_prefix_ouptput(prefix, cmd):
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    StreamLinePrefixer(process.stdout, prefix + ":")
    StreamLinePrefixer(process.stderr, prefix + ":")
    return process

class NginxWrapper:
    def __init__(self):
        self.process = None
        self.lock = threading.RLock() # Rentrant lock

    def start(self):
        with self.lock:
            self.process = popen_prefix_ouptput("Nginx", ["nginx", "-g", "daemon off;"])

    def stop(self):
        with self.lock:
            self.process.terminate()
            self.process.wait()

    def restart(self):
        with self.lock:
            self.stop()
            self.start()

def create_certificate(main_domain, domains, email, callback):
    def inner():
        print("Slendi: Creating certificates for %s" % main_domain)
        domain_arguments = reduce(lambda x,y: x+y, map(lambda x: ["-d", x], domains))

        process = popen_prefix_ouptput("Certbot [%s]" % main_domain,
            ["certbot",
             "certonly",
             "--test-cert",
             "-a", "webroot",
             "--webroot-path=" + NGINX_LETS_ENCRYPT_WEBROOT,
             "--email", email,
             "--agree-tos",
             "--text"] + domain_arguments)

        process.wait()

        callback(
            "/etc/letsencrypt/live/%s/fullchain.pem" % main_domain,
            "/etc/letsencrypt/live/%s/privkey.pem" % main_domain)

    thread = threading.Thread(target = inner)
    thread.start()

def certificate_created(nginx_config_path, main_domain, domains, proxy_ip, proxy_port, fullchain_path, privkey_path):
    with open(DEFAULT_NGINX_SITE_TEMPLATE, 'r') as f:
        site_template = f.read()
        site_template = site_template.replace("%MAIN_DOMAIN%", main_domain)
        site_template = site_template.replace("%DOMAINS%", " ".join(domains))
        site_template = site_template.replace("%PROXY_IP%", proxy_ip)
        site_template = site_template.replace("%PROXY_PORT%", proxy_port)
        site_template = site_template.replace("%FULLCHAIN_PATH%", fullchain_path)
        site_template = site_template.replace("%PRIVKEY_PATH%", privkey_path)

    with open(nginx_config_path, 'w') as f:
        f.write(site_template)

    nginxWrapper.restart()


print("")
print("Slendi: Started!")
os.makedirs(NGINX_LETS_ENCRYPT_WEBROOT)
print("Slendi: Created webroot directory needed by certbot")
print("Slendi: Starting initial nginx for bootstrapping.")
nginxWrapper = NginxWrapper()
nginxWrapper.start()

create_certificate("saua.no", ["saua.no"], "knut@saua.no", lambda fullchain_path, privkey_path: certificate_created("/etc/nginx/conf.d/saua.no.conf", "saua.no", ["saua.no"], "127.0.0.1", "8000", fullchain_path, privkey_path))

while True:
    pass
