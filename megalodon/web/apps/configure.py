#! /usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import (division, print_function)
import os, re, collections

from dash import dcc
from dash import html
from dash.dependencies import Input, Output

import padl
from padl.padl import app

layout = html.Div([
    html.H3('AMPCS Configuration Wizard'),
    dcc.Dropdown(id='nalct-configure-dropdown',options=[{'label': 'nalct Configure - {}'.format(i), 'value': i} for i in ['Enclave', 'Service', 'Image']]),
    html.Div(id='nalct-configure-display-value'),
    dcc.Link('Go to Launcher', href='/launch'),
    dcc.Link('Go to Monitor', href='/monitor')
])

@app.callback(Output('nalct-configure-display-value', 'children'),[Input('nalct-configure-dropdown', 'value')])
def display_value(value): return 'You have selected "{}"'.format(value)

################################################################################
# vim:set sr et ts=4 sw=4 ft=python fenc=utf-8: // See Vim, :help 'modeline'
