#! /usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function)

import os, re, collections, getpass, functools, logging, json, inspect

import dash
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
from dash.dependencies import (Input, Output, State, MATCH, ALL)

from ..meg import app

_enclaves = collections.OrderedDict()

def make_service_card(service):
    pass

def make_item(index, name):
    # we use this function to make the example items to avoid code duplication
    return dbc.Card(
        [
            dbc.CardHeader(
                html.H2(
                    dbc.Button(
                        name,
                        color="link",
                        id=dict(type="enclave-group-toggle", index=index),
                    )
                )
            ),
            dbc.Collapse(
                dbc.ListGroup(
                    [dbc.ListGroupItem(make_service_card(_service)) for _service in _enclaves.get(name).get('services') ],
                    flush=True,
                ),
                # dbc.CardBody(f"This is the content of group {index}..."),
                id=dict(type="enclave-group-collapse", index=index),
            ),
        ]
    )


accordion = html.Div(
    [make_item(ii, name) for ii, name in enumerate(_enclaves.keys())], className="accordion"
)

jumbotron = html.Div(
    dbc.Container(
        [
            html.H1("🐾 PAW", className="display-3"),
            html.P(
                "PAW (Performance Assessment Workspace) is a scoped user-facing interface for Performance Assessment tasks.",
                className="lead",
            )
        ],
        fluid=True,
        className="py-3",
    ),
    className="p-3 bg-light rounded-3",
)

layout = dbc.Container(
    children=[
        # dbc.Alert("What's Nalct?!", color="success"),
        jumbotron,
        html.Hr(),
        # dropdowns,
        # html.Hr(),
        # dbc.Button("Configure", id='nalct-configure', outline=True, color="light", className="mr-1"),
        # dbc.Button("Launch", id='nalct-launch', outline=True, color="info", className="mr-1"),
        # html.Hr(),
        accordion,
        ],
    className="p-5",
)


list_to_bitmask=lambda ll: int(''.join(map(lambda x: str(int(x)), ll)), 2)
@app.callback(Output({'type': 'enclave-group-collapse', 'index': ALL}, "is_open"),
    [Input({'type': 'enclave-group-toggle', 'index': ALL}, 'n_clicks')],
    [State({'type': 'enclave-group-collapse', 'index': ALL}, "is_open")],
)
def toggle_accordion(values, states):
    ctx = dash.callback_context
    _default=[False]*len(states)
    if not(ctx.triggered):
        return _default
    else:
        _default[json.loads(ctx.triggered[0]["prop_id"].split(".")[0]).get('index')]=True
        _current=list_to_bitmask(states)
        _mask=list_to_bitmask(_default)
        return tuple(map(lambda x: bool(int(x)), '{{:0{}b}}'.format(len(states)).format( (_mask|_current)^_current)))

################################################################################
# vim:set sr et ts=4 sw=4 ft=python fenc=utf-8: // See Vim, :help 'modeline'
