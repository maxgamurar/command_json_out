# -*- coding: utf-8 -*-


"""
    command_json_out
    ===========================

    This extension provides a directive to include the output of commands JSON as
    raw HTML Definition List while building the anaconda-cloud docs.

"""

from __future__ import (print_function, division, unicode_literals,
                        absolute_import)

import sys
import os
import shlex
import markdown
from subprocess import Popen, PIPE, STDOUT, check_output, CalledProcessError
from collections import defaultdict, namedtuple

from docutils import nodes
from docutils.core import publish_string
from docutils.parsers import rst
from docutils.parsers.rst.directives import flag, unchanged, nonnegative_int


__version__ = '0.0.1'


class command_json_output(nodes.Element):
    pass


class CommandJSONOutputDirective(rst.Directive):
    has_content = False
    final_argument_whitespace = True
    required_arguments = 1

    option_spec = dict(level=nonnegative_int)

    def run(self):
        env = self.state.document.settings.env

        node = command_json_output()
        node.line = self.lineno
        node['command'] = self.arguments[0]
        node['level'] = self.options.get('level', 1)

        return [node]


_Command = namedtuple('Command', 'command')


class Command(_Command):
    """
    A command to be executed.
    """

    def __new__(cls, command):
        if isinstance(command, list):
            command = tuple(command)

        return _Command.__new__(cls, command)

    @classmethod
    def from_command_json_output_node(cls, node):
        command = (node['command']).strip()
        return cls(command)

    def execute(self):
        """
        Execute this command.
        """

        command = self.command

        try:
            import json
            output = check_output(command, shell=True, stderr=STDOUT)
            return json.loads(output)
        except CalledProcessError as err:
            output = command + ' : ' + err.output

        return output

    def get_output(self):
        """
        Get the output of this command.
        """
        output = self.execute()
        return output

    def __str__(self):
        if isinstance(self.command, tuple):
            return repr(list(self.command))
        return repr(self.command)


class CommandJSONOutputCache(defaultdict):
    """
    Execute command and cache their output.

    """

    def __missing__(self, command):
        """
        Called, if a command was not found in the cache.
        """
        result = command.get_output()
        self[command] = result
        return result


def run_programs(app, doctree):
    """
    Execute all programs represented by ``command_json_output`` nodes in
    ``doctree``.
    """

    node_class = nodes.raw

    cache = app.env.commandjsonoutput_cache

    for node in doctree.traverse(command_json_output):
        command = Command.from_command_json_output_node(node)
        output = cache[command]
        output_rst = ''

        #Convert JSON into HTML formatted definition list
        for group in output['groups']:
            if 'title' in group and group['title']:
                output_rst += '<div class="cli-group-title">' + str(group['title'])
                if group['description']:
                    output_rst += '<p>' + str(markdown.markdown(group['description'])) + '</p>'
                output_rst += '</div>'
            output_rst += '<dl class="dl-horizontal dl-multiline docutils">'
            for action in group['actions']:
                if(action['option_strings'] or action['help']):
                    output_rst += '<dt>' + ' / '.join(action['option_strings']) + '</dt>'
                    output_rst += '<dd>' + str(action['help']) + '</dd>'

                if  action['action'] == 'parsers':
                  for key in sorted(action['choices']):
                      output_rst += '<dt>' + str(key) + '</dt>'
                      output_rst += '<dd>' + str(action['choices'][key]) + '</dd>'

            output_rst += '</dl>'

        new_node = node_class('', output_rst, format='html')
        new_node['language'] = 'text'
        node.replace_self(new_node)


def init_cache(app):
    """
    Initialize the cache for the output

    The cache is of type :class:`CommandJSONOutputCache`.
    """
    if not hasattr(app.env, 'commandjsonoutput_cache'):
        app.env.commandjsonoutput_cache = CommandJSONOutputCache()


def setup(app):
    app.add_directive('command-json-output', CommandJSONOutputDirective)
    app.connect(str('builder-inited'), init_cache)
    app.connect(str('doctree-read'), run_programs)
