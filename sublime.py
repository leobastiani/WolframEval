import sublime
import sublime_plugin

from urllib.request import Request, urlopen
import threading
import time
import json
import re
import sys
from pprint import pprint
from urllib.parse import quote
from .wolfram import *




class WolframSublime(Wolfram):
    def __init__(self, edit, view, region):
        self.edit = edit
        self.view = view
        self.region = region
        self.content = self.view.substr(region)

        # posição de inicio
        Wolfram.__init__(self, self.content, self.wolframCb)

    def wolframCb(self, res):
        self.result = res

    def newRegion(self, d):
        return sublime.Region(self.region.a + d, self.region.b + d)


class WolframEval(sublime_plugin.TextCommand):

    def run(self, edit):
        # todos os wolframs sublimes
        wolframSublimes = []
        for region in self.view.sel():
            if not region.empty():
                wolframSublimes.append(WolframSublime(edit, self.view, region))

        # faz os joins
        for ws in wolframSublimes:
            ws.join()


        # o valor de d é um diferencial que vamos adotar
        # pra cada letra inserida
        d = 0
        for ws in wolframSublimes:
            if ws.result is not None:
                ws.view.replace(ws.edit, ws.newRegion(d), ws.result)
                d += len(ws.result) - (ws.region.b - ws.region.a)