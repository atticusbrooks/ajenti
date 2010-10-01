import os
import glob

from ajenti.com import *
from ajenti.app.helpers import ModuleContent
from ajenti import apis


class ApacheBackend:
    config_dir = '/etc/apache2/'
    
    def is_installed(self):
        return os.path.exists(self.config_dir)
        
    def get_hosts(self):
        r = {}
        for h in os.listdir(os.path.join(self.config_dir, 'sites-available')):
            data = open(os.path.join(self.config_dir, 'sites-available', h)).read()
            host = apis.webserver.VirtualHost()
            host.config = data
            host.name = h
            host.enabled = os.path.exists(
                            os.path.join(self.config_dir, 'sites-enabled', h)
                           )
            r[h] = host
        return r
        
    def enable_host(self, id):
        p = os.path.join(self.config_dir, 'sites-enabled', id)
        if not os.path.exists(p):
            ps = os.path.join(self.config_dir, 'sites-available', id)
            os.symlink(ps, p)

    def disable_host(self, id):
        p = os.path.join(self.config_dir, 'sites-enabled', id)
        if os.path.exists(p):
            os.unlink(p)

    def save_host(self, host):
        path = os.path.join(self.config_dir, 'sites-available', host.name)  
        open(path, 'w').write(host.config)
          
    def get_mods(self):
        r = {}
        dir_mods_avail = self.config_dir + '/mods-available/'
        lst = [s.replace(dir_mods_avail, '').replace('.load', '') 
             for s in glob.glob(dir_mods_avail + '*.load')]
        for h in lst:
            mod = apis.webserver.Module()
            mod.name = h
            confpath = os.path.join(self.config_dir, 'mods-available', h+'.conf')
            mod.has_config = os.path.exists(confpath)
            if mod.has_config:
                mod.config = open(os.path.join(self.config_dir, 'mods-available', h+'.conf')).read()
            mod.enabled = os.path.exists(
                            os.path.join(self.config_dir, 'mods-enabled', h+'.load')
                           )
            r[h] = mod
        return r
        
    def enable_mod(self, id):
        p = os.path.join(self.config_dir, 'mods-enabled', id)
        if not os.path.exists(p+'.load'):
            ps = os.path.join(self.config_dir, 'mods-available', id+'.load')
            os.symlink(ps, p+'.load')
        if not os.path.exists(p+'.conf'):
            if os.path.exists(os.path.join(self.config_dir, 'mods-available', id+'.conf')):
                ps = os.path.join(self.config_dir, 'mods-available', id+'.conf')
                os.symlink(ps, p+'.conf')

    def disable_mod(self, id):
        p = os.path.join(self.config_dir, 'mods-enabled', id)
        if os.path.exists(p+'.load'):
            os.unlink(p+'.load')
        if os.path.exists(p+'.conf'):
            os.unlink(p+'.conf')

    def save_mod(self, mod):
        path = os.path.join(self.config_dir, 'sites-available', mod.name+'.conf')  
        open(path, 'w').write(mod.config)
     
                       
class ApachePlugin(apis.webserver.WebserverPlugin):
    text = 'Apache 2'
    icon = '/dl/apache/icon_small.png'
    folder = 'servers'
    ws_service = 'apache2'
    ws_name = 'apache'
    ws_icon = '/dl/apache/icon.png'
    ws_title = 'Apache 2'
    ws_backend = ApacheBackend()
    ws_mods = True

class ApacheContent(ModuleContent):
    module = 'apache'
    path = __file__