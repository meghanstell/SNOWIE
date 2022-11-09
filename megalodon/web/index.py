#! /usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function)
import os, re, collections
import rich_click as click
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
from dash.dependencies import (Input, Output)

from ..DotMap import (DotMap, SmartDict)
from .meg import app
from .apps import (default, monitor)

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    dbc.NavbarSimple(
        children=[
            dbc.NavItem(dbc.NavLink("🦈 MEG", href="/", target="_blank")),
            dbc.NavItem(dbc.NavLink("Launch", href="/launch", target="_blank", disabled=True)),
            dbc.NavItem(dbc.NavLink("Monitor", href="/monitor", target="_blank")),
            dbc.NavItem(dbc.NavLink("Configure", href="/configure", target="_blank", disabled=True)),
            dbc.DropdownMenu(
                children=[
                    dbc.DropdownMenuItem("More pages", header=True),
                    dbc.DropdownMenuItem("Launch", header=True),
                    dbc.DropdownMenuItem("PAW Launcher", href="/launch", target="_blank", disabled=True),
                    dbc.DropdownMenuItem(divider=True),
                    dbc.DropdownMenuItem("Manage", header=True),
                    dbc.DropdownMenuItem("PAW Monitor", href="/monitor", target="_blank"),
                    dbc.DropdownMenuItem(divider=True),
                    dbc.DropdownMenuItem("Configure", header=True),
                ],
                nav=True,
                in_navbar=True,
                label="More",
            ),
        ],
        brand="🦈 MEG",
        brand_href="#",
        color="primary",
        dark=True,
    ),
    html.Div(children=default.layout, id='page-content')
])

@app.callback(Output('page-content', 'children'), [Input('url', 'pathname')])
def display_page(pathname):
    if pathname in [None, '/', '#']: return monitor.layout
    # if re.match(r'^.*launch$',pathname): return launch.layout
    elif re.match(r'^.*monitor$',pathname): return monitor.layout
    # elif re.match(r'^.*configure$',pathname): return configure.layout
    else: return monitor.layout

server=app.server

@click.command('web')
@click.option('-h','--host', default=None, help="Dash Server host to launch (0.0.0.0, 127.0.0.1, etc.)")
@click.option('-p','--port', default=None, help="Dash Server Port to launch")
@click.pass_context
def main(ctx, *args, **kwargs):
    """
        Launch Performance Assessment Workspace WebUI
    """
    ctx.obj()
    opts = SmartDict({kk:None if vv in [tuple(), None] else vv for kk,vv in kwargs.items() })
    _opts=dict(opts)
    _opts.setdefault('host', ctx.obj.meg_host)
    _opts.setdefault('port', ctx.obj.meg_port)
    app.run_server(**_opts) # host=_context.paw_host, port=_context.paw_port)

if __name__ == '__main__':
    main()


################################################################################
# vim:set sr et ts=4 sw=4 ft=python fenc=utf-8: // See Vim, :help 'modeline'
