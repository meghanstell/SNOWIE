#! /usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function)
import flask
import dash
_auth=None
try:
    import dash_auth
    _auth=True
except ImportError:
    pass
import dash_bootstrap_components as dbc

app = dash.Dash(__name__, suppress_callback_exceptions=True, external_stylesheets=[dbc.themes.DARKLY])
if _auth:
    auth = dash_auth.BasicAuth(app, dict(meg='meg'))
# app = dash.Dash(name='WebDog', server=flask.Flask(__name__), suppress_callback_exceptions=True, external_stylesheets=[dbc.themes.DARKLY])
# app.scripts.config.serve_locally=True
server = app.server

# app.run_server(debug=True)


# app = dash.Dash(external_stylesheets=[dbc.themes.DARKLY])

# if __name__ == "__main__":
#     app.run_server()

################################################################################
# vim:set sr et ts=4 sw=4 ft=python fenc=utf-8: // See Vim, :help 'modeline'
