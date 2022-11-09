#! /usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function)
import os, re, collections, getpass, functools, click, six, logging, json, threading, datetime
import base64
import datetime
import io
import contextlib

import pandas as pd

import dash
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State, ALL
from dash import dash_table
import plotly.express as px

from megalodon.web.meg import app
from megalodon import MegIOP

_iop_file=MegIOP.IopFile()

layout = html.Div([
    dcc.Upload(
        id='upload-data',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select Files')
        ]),
        style={
            'width': '100%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px'
        },
        # Allow multiple files to be uploaded
        multiple=True
    ),
    html.Hr(),
    dbc.Button("Run", color="primary", className="me-1", id='chill-get-fetch'),
    html.Hr(),
    html.Div(id='paw-monitor-output-data-upload'),
    html.Hr(),

    html.Div(id='paw-monitor-command-timeline'),
    html.Div(id='paw-monitor-output-chill-get'),
])

def _get_io(filename, decoded):
    _io_file=None
    try:
        if 'csv' in filename:
                # Assume that the user uploaded a CSV file
                # df = pd.read_csv(
                #     io.StringIO(decoded.decode('utf-8')), names=COLUMNS)
                _io_file=io.StringIO(decoded.decode('utf-8'))
        elif 'xls' in filename:
            # Assume that the user uploaded an excel file
            _io_file=io.StringIO()
            df = pd.read_excel(io.BytesIO(decoded))
            df.to_csv(_io_file, index=None, header=True)
    except Exception as e:
        print(e)
        return html.Div(['There was an error processing this file.'])
    finally:
        return _io_file

def make_record(data): 
    if data.kind in ['RateEvent']:
        return dict(time=data.ert, rate=data.rate, name=data.channel)
    if data.kind in ['GenericInfo']:
        return dict(time=data.ert, rate=data.rate, name=data.code)

def parse_contents(contents, filename, date):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    _io_file=_get_io(filename, decoded)

    with contextlib.redirect_stdout(io.StringIO()) as f:
        _sh=session.SessionReportHandler(filename=_io_file)()
    _fig = px.timeline(_sh.command_df, x_start="start", x_end="stop", y="name", color='status', title='FSW Command Timeline')

    _eha_fig=None
    _io_file=_get_io(filename, decoded)

    m = eharate.EHARates()
    with pc_csv.CSVSource(_io_file) as csv_reader:
        for event in csv_reader:
            m.eval(event)
        infos = m.get_all_errors()
        _data=[make_record(_datum.data) for _,_datum in infos]
        df=pd.DataFrame.from_records(_data)
        _eha_fig = px.line(df, x="time", y="rate", color="name")#, line_group="country", hover_name="country",line_shape="spline", render_mode="svg")
        # eharate.log('data:\n\t{}'.format(_data))
        eharate.log(f'{len(infos)} messages recorded.')
        eharate.walk_all_infos(infos)
        eharate.log('ENDING ANALYSIS')
        eharate.statistics_global.show()

    try:
        _autopsy_fig=None
        _io_file=_get_io(filename, decoded)

        eharate.Options.AUTOPSY = True
        m = eharate.AutopsyMonitors()
        with pc_csv.CSVSource(_io_file) as csv_reader:
            for event in csv_reader:
                m.eval(event)
            infos = m.get_all_errors()
            _data=[make_record(_datum.data) for _,_datum in infos]
            df=pd.DataFrame.from_records(_data)
    except Exception as e:
        logging.getLogger(__name__).warning('{}'.format(e))
        pass




    # df['ert']=pd.to_datetime(df['ert'], format='%Y-%jT%H:%M:%S.%f')
    # df['scet']=pd.to_datetime(df['scet'], format='%Y-%jT%H:%M:%S.%f')
    # df.set_index(df['ert'], inplace=True)
    #
    # grouper = df.groupby([pd.Grouper(freq='5T'), 'module'])
    # module_count = grouper['dn'].count().unstack('module').fillna(0)
    # df_r=pd.DataFrame({'EHA Count':df['dn'].resample('5T')})

    # df_module=pd.DataFrame({'Module'})
    # _fig=px.bar(module_count)
    # _fig.update_layout(barmode='group')
    return html.Div([
        html.H5('{}'.format(filename)),
        # html.H6('Start: {}'.format(df.index.min())),
        # html.H6('End: {}'.format(df.index.max())),
        # html.H6('Duration: {}'.format(df.index.max()-df.index.min())),
        # html.H6('Total Count: {}'.format(df['dn'].count())),
        # dcc.Graph(
        #     figure=px.bar(df['dn'].resample('5T').count())
        # ),
        dcc.Graph(
            figure=_fig
        ),
        dcc.Graph(
            figure=_eha_fig
        ),
        # dash_table.DataTable(
        #     data=df.to_dict('records'),
        #     columns=[{'name': i, 'id': i} for i in df.columns]
        # ),

        html.Hr(),  # horizontal line

        # For debugging, display the raw contents provided by the web browser
        # html.Div('Raw Content'),
        # html.Pre(contents[0:200] + '...', style={
        #     'whiteSpace': 'pre-wrap',
        #     'wordBreak': 'break-all'
        # })
    ])

@app.callback(Output('paw-monitor-output-data-upload', 'children'),
              Input('upload-data', 'contents'),
              State('upload-data', 'filename'),
              State('upload-data', 'last_modified'))
def update_output(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        children = [
            parse_contents(c, n, d) for c, n, d in
            zip(list_of_contents, list_of_names, list_of_dates)]
        return children

@app.callback(Output('paw-monitor-output-chill-get', 'children'),
              Input('chill-get-fetch',  'n_clicks'))
def update_output(n):
    _data=_iop_file()
    __df=_data.df
    _raw_series={_cn: __df[_cn] for _cn in list(__df.columns) if _cn not in ['time']}
    return html.Div([
        html.Hr(),
        dcc.Graph(
                figure={
                    'data': [ {'x':__df['time'], 'y':ss, 'name':kk} for kk,ss in _raw_series.items() ],
                    'layout': {
                        'title': 'Ice Water Content'
                    }
                }
            ),
        # dash_table.DataTable(
        #     data=_chill.df.to_dict('records'),
        #     columns=[{'name': i, 'id': i} for i in _chill.df.columns],
        #     filter_action="native",
        #     sort_action="native",
        #     sort_mode="multi",
        #     column_selectable="multi",
        #     # row_selectable="multi",
        #     selected_columns=[],
        #     selected_rows=[],
        #     page_action="native",
        #     hidden_columns=['eventId','dssId','vcid','metadataKeywordList','metadataValuesList', 'recordType', 'sessionId', 'sessionHost'],
        #     style_cell={'textAlign': 'left'},
        #     style_header={
        #         'backgroundColor': 'rgb(30, 30, 30)',
        #         'color': 'white'
        #     },
        #     style_data={
        #         'backgroundColor': 'rgb(50, 50, 50)',
        #         'color': 'white'
        #     },
        #     style_data_conditional=[
        #         {
        #             'if': {
        #                 'filter_query': '{level} = FATAL',
        #                 'column_id': 'level'
        #             },
        #             'backgroundColor': 'tomato',
        #             'color': 'white'
        #         },
        #         {
        #             'if': {
        #                 'filter_query': '{level} = WARNING_LO',
        #                 'column_id': 'level'
        #             },
        #             'backgroundColor': 'gold',
        #             'color': 'black'
        #         },
        #         {
        #             'if': {
        #                 'filter_query': '{level} = WARNING_HI',
        #                 'column_id': 'level'
        #             },
        #             'backgroundColor': 'orange',
        #             'color': 'black'
        #         },
        #         {
        #             'if': {
        #                 'filter_query': '{level} = COMMAND',
        #                 'column_id': 'level'
        #             },
        #             'backgroundColor': '#66CCFF',
        #             'color': 'white'
        #         },
        #         {
        #             'if': {
        #                 'filter_query': '{level} = ACTIVITY_LO',
        #                 'column_id': 'level'
        #             },
        #             'backgroundColor': '#ccc',
        #             'color': 'black'
        #         },
        #         {
        #             'if': {
        #                 'filter_query': '{level} = ACTIVITY_HI',
        #                 'column_id': 'level'
        #             },
        #             'backgroundColor': '#6B6B6B',
        #             'color': 'white'
        #         },
        #         {
        #             'if': {
        #                 'filter_query': '{level} = DIAGNOSTIC',
        #                 'column_id': 'level'
        #             },
        #             'backgroundColor': '#00FF00',
        #             'color': 'black'
        #         },
        #     ],
        # ),
        html.Hr(),
    ])

_dd={
        'FATAL':"background-color: tomato; color:white;",
        'WARNING_LO':"background-color: gold; color: black;",
        'WARNING_HI':"background-color: orange; color: black;",
        'COMMAND':"background-color: #66CCFF; color: white;",
        'ACTIVITY_LO':"background-color: #ccc; color: black;",
        'ACTIVITY_HI':"background-color: #6B6B6B; color: white;",
        'DIAGNOSTIC':"background-color: #00FF00; color: black;"}
if __name__ == '__main__':
    app.run_server(debug=True)

################################################################################
# vim:set sr et ts=4 sw=4 ft=python fenc=utf-8: // See Vim, :help 'modeline'
