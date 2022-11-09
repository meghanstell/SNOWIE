#! /usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division, print_function)
import os, sys, re, json, yaml, collections, functools, subprocess, time, logging
# import click
import rich_click as click
from . import MegContext
from . import MegIOP
from .web import index
from .DotMap import SmartDict
# from .web import index

# flb_ctx=FlbContext.FlbContext()()

@click.group(chain=True, context_settings=dict(help_option_names=['-h', '--help'], ignore_unknown_options=True))
# @click.group(context_settings=dict(help_option_names=['-h', '--help'], ignore_unknown_options=True))
@click.option('--debug/--no-debug', default=None, help='Debug level output')
@click.pass_context
def _meg(ctx, *args, **kwargs):
    # logging.getLogger(__name__).info('_pycontract')
    _dd=SmartDict(**kwargs)
    ctx.obj=MegContext.MegContext(**_dd)
    ctx.obj(**_dd)
    # logging.getLogger(__name__).info('_pycontract.install_plugins')
    # PcContext.install_pycontract_plugins()
    if ctx.obj.debug:
        ctx.obj.show()
    # if not(os.path.exists(os.path.join(ctx.obj.config_dir, 'node_modules'))):
    #     os.system('pushd {cd} && yarn add taskbook ink enquirer inquirer inquirer-fuzzy-path chalk-cli chalk-animation inquirer-file-tree-selection-prompt --network-timeout 100000'.format(cd=ctx.obj.config_dir))

# _pycontract.add_command(PcContext.main)
# _pycontract.add_command(PcContext._init)
# _pycontract.add_command(PcContext.show)
# _pycontract.add_command(PcDb._main)
# _pycontract.add_command(PcDb._db)
# _pycontract.add_command(PcAuth._auth)
# _pycontract.add_command(index.main)
# _pycontract.add_command(session._session_report)
# _pycontract.add_command(session._immediate_command)
# _pycontract.add_command(FswDict.main)
# _pycontract.add_command(PcChill._chill)
# _pycontract.add_command(PcBlog._blog)
# _pycontract.add_command(PcBlog._rsb_count)
# _pycontract.add_command(PcBlog._dcm)
_meg.add_command(MegIOP._iop)
_meg.add_command(index.main)
# _flb.add_command(FlbDuration._durations)


if __name__ == "__main__":
    _meg()

################################################################################
# vim:set sr et ts=4 sw=4 ft=python fenc=utf-8: // See Vim, :help 'modeline'
