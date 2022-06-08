#!/usr/bin/python
import sys
sys.path.insert(0,'/var/www/htw_beratungsstelle_api')

activate_this = '/var/www/htw_beratungsstelle_api/htw_beratungsstelle_api/bin/activate_this.py'
with open(activate_this) as file_:
    exec(file_.read(), dict(__file__=activate_this))

from app import app as application


