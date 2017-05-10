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


class Download:

    def __init__(self, url, cb):
        self.cb = cb
        self.url = url
        self.killed = False
        
        def runThread():
            req = Request(self.url)
            req.add_header('referer', 'https://products.wolframalpha.com/api/explorer/')
            res = urlopen(req).read().decode('ISO-8859-1')
            if self.killed:
                return
            self.cb(res)

        self.t = threading.Thread(target=runThread)
        self.t.start()


    def kill(self):
        self.killed = True

    def join(self):
        self.t.join()



class Wolfram(Download):
    # a função do json precisa de um semaphoro
    semJson = threading.Semaphore(1)
    
    def __init__(self, eq, cb):

        # vamos analisar a entrada
        reVariable = r'[a-zA-z]\w*'

        # se tiver variaveis
        variableList = [
            # nome da variável 0,
            # nome da variável 1,
            # ...
        ];
        if re.search(reVariable, eq):
            allVariables = set(re.findall(reVariable, eq))
            def removeVariable(v):
                if v in ['pi', 'e', 'E']: return True
                return False

            allVariables = [x for x in allVariables if not removeVariable(x)]

            for v in allVariables:
                eq = re.sub(r'\b'+v+r'\b', 'x'+str(len(variableList)), eq)
                variableList.append(v)



        reVirgularVariable = r',\s*('+reVariable+r')$'
        if re.search(reVirgularVariable, eq):
            eq = 'solve '+re.sub(reVirgularVariable, r' for \1', eq)

        # se não tem solve, devo coloca-lo
        elif len(variableList) == 1:
            eq = 'solve '+eq+', x0'


        def stdOutput(o):
            o = re.sub('\s+', ' ', o)
            o = o.replace('==', '=')
            o = re.sub(r'(x\d+)\s+(x\d+)', r'\1*\2', o)
            o = re.sub(r'(\d+)\s+(x\d+)', r'\1*\2', o)

            # troca os nomes das variaveis
            i = 0
            for v in variableList:
                o = re.sub(r'\bx'+str(i)+r'\b', v, o)
                i += 1

            return o

        def downloadCb(res):
            Wolfram.semJson.acquire()
            res = json.loads(res)
            Wolfram.semJson.release()

            res = res['queryresult']
            pods = res['pods']
            for pod in pods:
                if pod['id'] in ['Result', 'Solution', 'SymbolicSolution']:
                    return cb(', '.join(set([stdOutput(x['moutput']) for x in pod['subpods']])))

                elif pod['id'] == 'DecimalApproximation':
                    return cb(pod['subpods'][0]['plaintext'].replace('?', ''))

            # não foi encontrado nada
            return cb(None)

        Download.__init__(self, "https://www.wolframalpha.com/input/apiExplorer.jsp?input="+quote(eq)+"&format=moutput,plaintext&output=JSON&type=full", downloadCb)



class WolframSublime(Wolfram):
    def __init__(self, edit, view, region):
        self.edit = edit
        self.view = view
        self.region = region
        self.content = self.view.substr(region)
        Wolfram.__init__(self, self.content, self.wolframCb)

    def wolframCb(self, res):
        self.result = res


class WolframEval(sublime_plugin.TextCommand):

    def run(self, edit):
        # todos os wolframs sublimes
        ws = []
        for region in self.view.sel():
            if not region.empty():
                ws.append(WolframSublime(edit, self.view, region))

        # faz os joins
        for w in ws:
            w.join()
            if w.result is not None:
                w.view.replace(w.edit, w.region, w.result)