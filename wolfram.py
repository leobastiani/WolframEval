from urllib.request import Request, urlopen
import threading
import time
import json
import re
import sys
from pprint import pprint
from urllib.parse import quote


DEBUG = sys.flags.debug or False
def debug(*args):
    '''funciona como print, mas só é executada se sys.flags.debug == 1'''
    if not sys.flags.debug:
        return ;
    print(*args)



class Download:

    def __init__(self, url, cb, headers={}):
        self.cb = cb
        self.url = url
        self.killed = False
        
        def runThread():
            req = Request(self.url)

            for h in headers:
                req.add_header(h, headers[h])

            res = urlopen(req).read()
            if DEBUG:
                with open('debug.js', 'wb') as file:
                    file.write(res)
            res = res.decode('UTF-8')
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
        reVariable = r'\b[a-zA-Z]\w*\b'

        # se tiver variaveis
        variableList = [
            # nome da variável 0,
            # nome da variável 1,
            # ...
        ]


        if re.search(reVariable, eq):
            allVariables = set(re.findall(reVariable, eq))
            def removeVariable(v):
                if v in ['pi', 'e', 'E', 'mod']: return True
                return False

            allVariables = [x for x in allVariables if not removeVariable(x)]

            for v in allVariables:
                eq = re.sub(r'\b'+v+r'\b', 'x'+str(len(variableList)), eq)
                variableList.append(v)


        # vamos retirar os \n e por ,
        eq = eq.replace(' ', '')
        eq = re.sub(r'[\n\r\t]+', ', ', eq)


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

            o = o.replace('', '=')

            return o

        def downloadCb(res):
            Wolfram.semJson.acquire()
            res = json.loads(res)
            Wolfram.semJson.release()

            res = res['queryresult']
            pods = res['pods']
            ids = [x['id'] for x in pods]
            for id in ['Result', 'DecimalApproximation', 'Solution', 'SymbolicSolution']:
                for pod in pods:
                    if pod['id'] != id:
                        continue
                    #  estou no id
                    for result in ['moutput', 'plaintext']:
                        if result not in pod['subpods'][0]:
                            continue
                        resWolfram = ', '.join(set([stdOutput(x[result]) for x in pod['subpods']]))
                        if '(irreducible)' in resWolfram:
                            # não quero resultados com irreducible
                            continue
                        return cb(resWolfram)

            # não foi encontrado nada
            return cb(None)

        # atualiza o eq
        self.eqEfetiva = eq
        quoted = quote(eq)
        Download.__init__(self, 'http://www.wolframalpha.com/input/json.jsp?async=true&format=plaintext,moutput&input='+quoted+'&output=JSON&proxycode=1c5688ba025555b8ba89fdef96ff665a&scantimeout=0.5', downloadCb, {
            'referer': 'http://www.wolframalpha.com/input/?i='+quoted,
            # 'Accept-Language': 'pt-BR,pt;q=0.8',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
        })

