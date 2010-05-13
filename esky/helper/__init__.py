"""

  esky.helper:  stand-alone helper app for processing esky updates.


This module provides the infrastructure for spawning a stand-alone "helper app"
to install updates.  Such a helper app might be necessary because:

    * files need to be overwritten that are currently in use
    * the updates need to be performed with admin privileges

The EskyHelperApp class mirrors the filesystem-modifying methods an Esky, and
transparently proxies them to a running helper app:

    * cleanup()
    * fetch_version(v)
    * install_version(v)
    * uninstall_version(v)

It also has a "close" method that shuts down the proccess.

"""

import sys
from functools import wraps


if sys.platform == "win32":
    from esky.helper.helper_win32 import has_root, SubprocPipe, spawn_helper
else:
    from esky.helper.helper_unix import has_root, SubprocPipe, spawn_helper


def proxied_method(func):
    """Method decorator for proxing calls to the helper app."""
    @wraps(func)
    def proxied_method_wrapper(self,*args,**kwds):
        self.proc.write((func.func_name,args,kwds))
        (success,value) = self.proc.read()
        if not success:
            raise value
        else:
            return value
    return proxied_method_wrapper


class EskyHelperApp(object):
    """Proxy for spawning and interacting with a stand-along helper app."""

    def __init__(self,esky,as_root=True):
        self.proc = spawn_helper(as_root=as_root)
        self.proc.write(esky)
        if self.proc.read() != "READY":
            self.close()
            raise RuntimeError("failed to spawn helper app")

    def close(self):
        self.proc.write(("close",(),{}))
        self.proc.read()
        self.proc.close()

    @proxied_method
    def has_root(self):
        pass

    @proxied_method
    def cleanup(self):
        pass

    @proxied_method
    def fetch_version(self,version):
        pass

    @proxied_method
    def install_version(self,version):
        pass

    @proxied_method
    def uninstall_version(self,version):
        pass



