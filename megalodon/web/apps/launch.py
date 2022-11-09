#! /usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function)

import os, re, collections, getpass, functools, click, six, logging, json, threading

import dash
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State, ALL

import os, collections, getpass, functools

_name_dev_dd={
    'A-UL': '207',
    'B-UL': '202',
    'A-TZ': '220',
    'B-TZ': '221',
    'A-LV': '222',
    'B-LV': '223',
    'A-SA': '224',
    'B-SA': '225'}
_dev_name_dd={vv:kk for kk,vv in _name_dev_dd.items()}

def _get_devices(path='/device/dfe'):
    return [{}]
    # _root=nalct.NalctConfiguration.NalctConfiguration(quiet=True, _context=_context)()._asdict()
    # _devices=next(iter(_root.get('entity', DotMap()).get('container', DotMap()).match(('name','device'))), DotMap())
    # _dev_ent=_devices.get('container', DotMap()).get('entity', [])
    # _dfe=next(iter(list(filter(lambda x: x.get('name') in ['dfe'], _dev_ent))), DotMap())
    # # _dfe=next(iter(_devices.get('container', DotMap()).get('entity', []).match(('name','dfe'))), DotMap())
    # _devs=list(map(lambda x: x.get('name'), _dfe.get('container', DotMap()).get('entity', []) ))
    # return [{'label': _dev_name_dd.get(_dev, _dev), 'value':os.path.join(path, _dev)} for _dev in _devs]

_command_funcs=[]

_devices=_get_devices()
logging.getLogger(__name__).debug('Devices: {}'.format(_devices))
# _commands=sorted(list(set( [_cmd for _device in [_dev.get('value') for _dev in _devices] for _cmds in nalct.NalctCommanding.NalctCommanding(path=_device, _context=_context).commands for _cmd in _cmds ] )))
_commands=[]
# _dev_cmds={_device:list(nalct.NalctCommanding.NalctCommanding(path=_device, _context=_context).commands) for _device in [_dev.get('value') for _dev in _devices] }
_dev_cmds={}
# _commands=[]
# [_commands.extend(_vv) for _vv in _dev_cmds.values()]

_commands=sorted(list(set( _commands )))


_get_click_context = lambda command: click.Context(command).__enter__()
# _commands=collections.OrderedDict([(_cmd.command.name, _cmd) for _cmd in map(_get_click_context, _commands)])
# _cmd_exe_dd = collections.OrderedDict([(_cmd_name, _command_funcs[ii]) for ii,_cmd_name in enumerate(_commands.keys())])
_cmd_exe_dd = {}
_all_services={} #cc.__name__ : cc for cc in nalct.DockerService.DockerService.yield_progeny()}
_all_service_names=sorted(set( filter(lambda x: isinstance(x, six.string_types), [getattr(vv,'component', None) for vv in _all_services.values()]) ))



input_groups = html.Div(
    [
        dbc.Container(
            children=[
                html.Label([
                    "Devices to Command",
                    dcc.Dropdown(
                        id='nalct-device-select-dropdown',
                        options=_devices,
                        multi=True,
                        value=[_dev.get('value') for _dev in _devices])
                ]),
                dbc.InputGroup(
                    [
                        # dbc.InputGroupAddon("Nalct Command", addon_type="prepend"),
                        dbc.InputGroupText("Nalct Command"),
                        dbc.Select(options=[{'label': _command_name, 'value': _command_name} for _command_name in _commands],id='nalct-command-input'),
                    ],),
                dbc.Container(id='nalct-command-parameters')
            ],
            id='nalct-command-builder'
        ),
    ],
)

layout = dbc.Container(
    children=[
        dbc.Alert("PyNAPL -- NetAcquire Commanding", color="success"),
        input_groups,
        dbc.Container(
            children=[dbc.InputGroup([dbc.Button("Execute", id='nalct-launch', outline=True, color="info", className="mr-1", disabled=True),]),],
            id='nalct-command-cfg-exec-container'
        ),
        dbc.Container(
            children=[],
            id='nalct-command-exec-container'
        ),
    ],
    className="p-5",
)

def make_bool_option(_command, _param):
    return dbc.FormGroup([
        dbc.Checklist(
            options=[ {"label": _param.name, "value": _param.name} ],
            value=[],
            id={'type': 'nalct-command-line-flags', 'index': '{}-{}'.format(_command, _param.name)},
            switch=True,
        ),
        dbc.FormText(_param.help, color="secondary",)]
    )

def make_command_option(_command, _param):
    _ctx=_context
    if re.match(r'^.*enclave.*$', _param.name):
        return dbc.FormGroup([
            dbc.Label(_param.name, html_for='nalct-command-line-options-{}-{}'.format(_command, _param.name)),
            dbc.Select(
                options=[{'label': _enclave, 'value': _enclave} for _enclave in sorted(_ctx.active.keys())] if re.match(r'^kill$', _command) else [{'label': _enclave, 'value': _enclave} for _enclave in sorted(_ctx.enclaves.keys())],
                id={'type': 'nalct-command-line-options', 'index': '{}-{}'.format(_command, _param.name)}),
            dbc.FormText(_param.help, color="secondary",)]
        )
    elif re.match(r'^.*service.*$', _param.name):

        return dbc.FormGroup([
            dbc.Label(_param.name, html_for='nalct-command-line-options-{}-{}'.format(_command, _param.name)),
            dbc.Select(
                options=[{'label': _service, 'value': _service} for _service in _all_service_names],
                id={'type': 'nalct-command-line-options', 'index': '{}-{}'.format(_command, _param.name)}),
            dbc.FormText(_param.help, color="secondary",)]
        )
    else:
        return dbc.FormGroup([
            dbc.Label(_param.name, html_for='nalct-command-line-options-{}-{}'.format(_command, _param.name)),
            dbc.Input(placeholder="{} value...".format(_param.name), type="text", id={'type': 'nalct-command-line-options', 'index': '{}-{}'.format(_command, _param.name)}),
            dbc.FormText(_param.help, color="secondary",)]
        )

def build_command_form(command):
    if not(command): return
    _ctx=None #_commands.get(command)
    _params=[] #_ctx.command.params
    _flags=[] #list(filter(lambda x: x.is_flag, _params))
    _options=[] #list(filter(lambda x: not(x.is_flag), _params))

    _content=[]
    if _options:
        options = dbc.FormGroup([
            dbc.FormGroup([make_command_option(command, _param) for _param in _options],
                id='nalct-command-line-options-{}'.format(command))])
        _content.append(options)

    if _flags:
        flags = dbc.FormGroup([
            dbc.Label("Flags", html_for='nalct-command-line-flags-{}'.format(command)),
            dbc.FormGroup([make_bool_option(command, _param) for _param in _flags],
                id='nalct-command-line-flags-{}'.format(command))])
        _content.append(flags)

    if _content:
        _content= [dbc.Label("Nalct {} Options".format(command.capitalize()), 'nalct-command-options-{}'.format(command))] + _content
        return dbc.FormGroup(_content)

@app.callback([Output("nalct-command-parameters", "children"), Output('nalct-launch', 'disabled')], [Input("nalct-command-input", "value")])
def update_command_form(nalct_command):
    logging.getLogger('.'.join([__name__, 'update_command_form'])).info('Command: "{}"'.format(nalct_command))
    if nalct_command:
        return [build_command_form(nalct_command)], False
    return [], True

def _invoke(command, devices):
    pass

@app.callback(
    Output('nalct-command-exec-container', 'children'),
    [Input('nalct-launch', 'n_clicks')],
    [State("nalct-command-input", "value"),
    State("nalct-device-select-dropdown", "value")],
)
def launch_nalct_command(launch_button_clicks, command, devices):
    logging.getLogger('.'.join([__name__, 'launch_nalct_command'])).info('Command: "{}", Devices: {}'.format(command, devices))
    if command and devices:
        _opts=SmartDict(command=command, devices=devices)
        try:
            threading.Thread(target=_invoke, args=(command, devices), name='.'.join([__name__, 'launch_nalct_command','invoke'])).start()

            return [dbc.Toast(
                    [
                        html.P("Launching `nalct.Command({})`".format(', '.join('{}={}'.format(kk,vv) for kk,vv in _opts.items())), className="mb-0"),
                        html.A("Status", href="/apps/app2", className="mb-0"),
                        dbc.Spinner(spinner_style={"width": "3rem", "height": "3rem"})],
                    id="nalct-launch-notifier",
                    header="Launching Nalct Command",
                    icon="primary",
                    duration=5000,
                ),]
        except Exception as e:
            return [dbc.Toast(
                    [html.P("Failed to Launch `nalct.{}({})`: {}".format(command, _opts, e), className="mb-0")],
                    id="nalct-launch-notifier",
                    header="Uh-oh!",
                    icon="danger",
                    duration=5000,
                )]
    return [None]

################################################################################
# vim:set sr et ts=4 sw=4 ft=python fenc=utf-8: // See Vim, :help 'modeline'
