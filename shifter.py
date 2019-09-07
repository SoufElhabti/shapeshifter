import click, os, requests, json, glob, sys, re
from datetime import datetime
import urllib.parse
from sgqlc.endpoint.http import HTTPEndpoint
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import json, string
import random
import errno
from datetime import datetime
from dateutil.relativedelta import relativedelta

@click.group()
@click.version_option('1.0')
@click.pass_context
def cli(ctx):
    ctx.obj = {}

@cli.command()
@click.pass_context
@click.option(
    '--url', '-u',
    prompt='Please Enter a URL:PORT to Test...',
    help='URL:PORT to scan',
)

@click.option(
    '--proxies', '-p',
    help='URL:PORT to proxy requests upstream',
)

def scan(ctx, url, proxies):
    """Scan a GraphQL endpoint"""
    ctx.obj = {
        'url' : url,
        'proxies': proxies,
    }

    requests.packages.urllib3.disable_warnings()

    consoleDict = [
        "",
        "/graphql",
        "/graphql/console",
        "/graphql.php",
        "/graphiql",
        "/graphiql.php",
        "/explorer",
        "/altair",
        "/playground"
    ]
    versionDict = [
        "",
        "/v1",
        "/v2",
        "/v3",
        "/v4",
        "/v5"
    ]
    matrix = []
    liveconsoles = []
    gqlendpoints = []

    for vers in versionDict:
        for con in consoleDict:
            matrix.append(vers+con)

    

    if ctx.obj['proxies'] is not None:
        proxies = {
            'http': 'http://127.0.0.1:8080',
            'https': 'http://127.0.0.1:8080',
            }
    else:
        proxies = None

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:68.0) Gecko/20100101 Firefox/68.0",
        "Content-Type": "application/json",
        'Accept':'application/json'
    }
    ctx.obj['headers'] = headers

    click.secho('[INFO] TESTING FOR CONSOLES AND ENDPOINTS', fg='yellow')

    with open('requests/probe/introspection_get.txt', 'r') as queriesstring:
        with click.progressbar(matrix, label='SCANNING....') as bar:
            get_introspection = queriesstring.read()
            for ep in bar:
                get_endpoint = ctx.obj['url']+ep
                
                # click.secho('| TESTING: '+get_endpoint, fg='yellow')
                try:
                    r = requests.get(get_endpoint+get_introspection, proxies=proxies, headers=headers, verify=False, timeout=3)
                except requests.exceptions.Timeout:
                    continue
                except requests.exceptions.ProxyError:
                    click.secho('[ERROR] PROXY ERROR - PLEASE CHECK UPSTREAM PROXY', fg='red')
                    sys.exit(1)

                if r.status_code == 200:
                    liveconsoles.append(get_endpoint)
                elif r.status_code != 200:
                    # click.secho('| BAD RESPONSE.. TRYING POST REQUEST', fg='red')
                    with open('requests/probe/introspection-post.txt', 'r') as postdata:
                        pr = requests.post(get_endpoint, proxies=proxies, headers=headers, verify=False, data=postdata)
                        if pr.status_code == 200:
                            gqlendpoints.append(get_endpoint)

    if len(liveconsoles) > 0:
        for item in liveconsoles:
            click.secho('| POSSIBLE CONSOLE LOCATED AT: '+item, fg='green')
            click.secho('|--------------------------------------------------------| ', fg='blue')

    if len(gqlendpoints) > 0:
        # for endp in gqlendpoints:
        endp = gqlendpoints[0]
        click.secho('| POSSIBLE POST ENDPOINT LOCATED AT: '+endp, fg='green')
        click.secho('[INFO] TESTING FOR INTROSPECTION', fg='yellow')
        
        with open('requests/probe/introspection-post.txt', 'r') as postdata:
            pr = requests.post(endp, proxies=proxies, headers=headers, verify=False, data=postdata)
            if pr.status_code == 200:
                ctx.obj['method'] = "POST"
                ctx.obj['endpoint'] = endp
                raw_resp = pr.content
                click.secho('[SUCCESS] INTROSPECTION QUERY EXECUTED', fg='green')
                filename = 'responses/introspection-response-%s.json' % str(datetime.now().strftime('%Y_%m_%d_%H_%M_%S'))
                with open(filename, mode='wb') as localfile:
                    localfile.write(raw_resp)
                ctx.obj['irespfile'] = filename
                click.secho('[SAVED] SCHEMA SAVED TO: %s' % ctx.obj['irespfile'], fg='blue')
                parseIntroResp()
                sendQueries(proxies)
            else:
                click.secho('[FAIL] INTROSPECTION NOT SUCCESSFUL', fg='red')

    

@click.pass_context    
def parseIntroResp(ctx):
    outdir = os.path.dirname(os.path.realpath(__file__))+"/OUTPUT/%s/" % (str(datetime.now().strftime('%Y_%m_%d_%H_%M_%S')))
    os.makedirs(outdir, exist_ok=True)
    ctx.obj['outdir'] = outdir

    with open('./'+ctx.obj['irespfile'], "r") as introFile:
        data = introFile.read()
        schema = json.loads(data)

        if schema['data']['__schema']['types'] is not None:
            schemaTypes = schema['data']['__schema']['types']
        
        for type in schemaTypes:
            if type['kind'] == "OBJECT":
                if type['name'] == "Query":
                    for field in type['fields']:
                        for arg in field['args']:
                            if arg['type']['kind'] == "SCALAR":
                                if arg['type']['name'] == 'Int':
                                    createQuery(field['name'], arg['name'], 'Int')

                                if arg['type']['name'] == 'Float':
                                    createQuery(field['name'], arg['name'], 'Float')

                                if arg['type']['name'] == 'String':
                                    createQuery(field['name'], arg['name'], 'String')

                                if arg['type']['name'] == 'Boolean':
                                    createQuery(field['name'], arg['name'], 'Boolean')
                                
                                if arg['type']['name'] == 'ID':
                                    createQuery(field['name'], arg['name'], 'ID')

                                if arg['type']['name'] == 'DateTime':
                                    createQuery(field['name'], arg['name'], 'DateTime')
                                
                                if arg['type']['name'] == 'EmailAddress':
                                    createQuery(field['name'], arg['name'], 'EmailAddress')  

                                if arg['type']['name'] == 'NegativeFloat':
                                    createQuery(field['name'], arg['name'], 'NegativeFloat')                                    

                                if arg['type']['name'] == 'NegativeFloat':
                                    createQuery(field['name'], arg['name'], 'NegativeFloat')                                    
                                
                                if arg['type']['name'] == 'NonNegativeFloat':
                                    createQuery(field['name'], arg['name'], 'NonNegativeFloat') 

                                if arg['type']['name'] == 'NonNegativeInt':
                                    createQuery(field['name'], arg['name'], 'NonNegativeInt') 

                                if arg['type']['name'] == 'NonPositiveFloat':
                                    createQuery(field['name'], arg['name'], 'NonPositiveFloat')

                                if arg['type']['name'] == 'NonPositiveInt':
                                    createQuery(field['name'], arg['name'], 'NonPositiveInt')

                                if arg['type']['name'] == 'PhoneNumber':
                                    createQuery(field['name'], arg['name'], 'PhoneNumber')
                                
                                if arg['type']['name'] == 'PositiveFloat':
                                    createQuery(field['name'], arg['name'], 'PositiveFloat')
                                
                                if arg['type']['name'] == 'PositiveInt':
                                    createQuery(field['name'], arg['name'], 'PositiveInt')

                                if arg['type']['name'] == 'PostalCode':
                                    createQuery(field['name'], arg['name'], 'PositiveInt')

                                if arg['type']['name'] == 'UnsignedFloat':
                                    createQuery(field['name'], arg['name'], 'UnsignedFloat')

                                if arg['type']['name'] == 'UnsignedInt':
                                    createQuery(field['name'], arg['name'], 'UnsignedInt')

                                if arg['type']['name'] == 'URL':
                                    createQuery(field['name'], arg['name'], 'URL')

                                if arg['type']['name'] == 'JSON' or arg['type']['name'] == 'JSONObject':
                                    createQuery(field['name'], arg['name'], 'JSON')

                                if arg['type']['name'] == 'FuzzyDateInt':
                                    createQuery(field['name'], arg['name'], 'FuzzyDateInt')    
    return

@click.pass_context 
def sendQueries(ctx, proxies):
    query_dir = os.path.abspath(ctx.obj['outdir']+"/Queries")+"/"

    for file in os.listdir(query_dir):
        if file.endswith(".json"):
            f = open(query_dir+file, "r")
            if f.mode == 'r':
                payload = f.read()
                pr = requests.post(ctx.obj['endpoint'], proxies=proxies, headers=ctx.obj['headers'], verify=False, data=payload)

                if pr.status_code == 200:
                    click.secho('[SUCCESS] %s QUERY EXECUTED' % file, fg='green')
                else:
                    retry = parseFailedQuery(pr, payload)
                    pr = requests.post(ctx.obj['endpoint'], proxies=proxies, headers=ctx.obj['headers'], verify=False, data=retry)
                    
                    if pr.status_code == 200:
                        click.secho('[RETRY SUCCESS] %s QUERY EXECUTED' % file, fg='green')

def createQuery(field_name,arg_name,scalar):
    if scalar == 'Int':
        query = "{\"query\":\"query{"+field_name+ "(" +arg_name +":"+ genInt() + "){" + arg_name + "}}\",\"variables\":null,\"operationName\":null}"
    
    elif scalar == 'Float':
        query = "{\"query\":\"query{"+field_name+ "(" +arg_name +":"+ genDoubleFloat() + "){" + arg_name + "}}\",\"variables\":null,\"operationName\":null}"
    
    elif scalar == 'String':
        query = "{\"query\":\"query{"+field_name+ "(" +arg_name +":"+ genStr() + "){" + arg_name + "}}\",\"variables\":null,\"operationName\":null}"
    
    elif scalar == 'Boolean':
        query = "{\"query\":\"query{"+field_name+ "(" +arg_name +":"+ genBoolean() + "){" + arg_name + "}}\",\"variables\":null,\"operationName\":null}"
    
    elif scalar == 'ID':
        query = "{\"query\":\"query{"+field_name+ "(" +arg_name +":"+ genId() + "){" + arg_name + "}}\",\"variables\":null,\"operationName\":null}"
    
    elif scalar == 'DateTime':
        query = "{\"query\":\"query{"+field_name+ "(" +arg_name +":"+ genDateTime() + "){" + arg_name + "}}\",\"variables\":null,\"operationName\":null}"
    
    elif scalar == 'EmailAddress':
        query = "{\"query\":\"query{"+field_name+ "(" +arg_name +":"+ genEmail() + "){" + arg_name + "}}\",\"variables\":null,\"operationName\":null}"
    
    elif scalar == 'NegativeFloat':
        query = "{\"query\":\"query{"+field_name+ "(" +arg_name +":"+ genNegFloat() + "){" + arg_name + "}}\",\"variables\":null,\"operationName\":null}"
    
    elif scalar == 'NegativeInt':
        query = "{\"query\":\"query{"+field_name+ "(" +arg_name +":"+ genNegInt() + "){" + arg_name + "}}\",\"variables\":null,\"operationName\":null}"
    
    elif scalar == 'NonNegativeFloat':
        query = "{\"query\":\"query{"+field_name+ "(" +arg_name +":"+ genDoubleFloat() + "){" + arg_name + "}}\",\"variables\":null,\"operationName\":null}"
    
    elif scalar == 'NonNegativeInt':
        query = "{\"query\":\"query{"+field_name+ "(" +arg_name +":"+ genInt() + "){" + arg_name + "}}\",\"variables\":null,\"operationName\":null}"
    
    elif scalar == 'NonPositiveFloat':
        query = "{\"query\":\"query{"+field_name+ "(" +arg_name +":"+ genNegFloat() + "){" + arg_name + "}}\",\"variables\":null,\"operationName\":null}"
    
    elif scalar == 'NonPositiveInt':
        query = "{\"query\":\"query{"+field_name+ "(" +arg_name +":"+ genNegInt() + "){" + arg_name + "}}\",\"variables\":null,\"operationName\":null}"
    
    elif scalar == 'PhoneNumber':
        query = "{\"query\":\"query{"+field_name+ "(" +arg_name +":"+ genPhone() + "){" + arg_name + "}}\",\"variables\":null,\"operationName\":null}"
    
    elif scalar == 'PositiveFloat':
        query = "{\"query\":\"query{"+field_name+ "(" +arg_name +":"+ genDoubleFloat() + "){" + arg_name + "}}\",\"variables\":null,\"operationName\":null}"
    
    elif scalar == 'PositiveInt':
        query = "{\"query\":\"query{"+field_name+ "(" +arg_name +":"+ genInt() + "){" + arg_name + "}}\",\"variables\":null,\"operationName\":null}"
    
    elif scalar == 'PostalCode':
        query = "{\"query\":\"query{"+field_name+ "(" +arg_name +":"+ genPostalCode() + "){" + arg_name + "}}\",\"variables\":null,\"operationName\":null}"
    
    elif scalar == 'UnsignedFloat':
        query = "{\"query\":\"query{"+field_name+ "(" +arg_name +":"+ genDoubleFloat() + "){" + arg_name + "}}\",\"variables\":null,\"operationName\":null}"
    
    elif scalar == 'UnsignedInt':
        query = "{\"query\":\"query{"+field_name+ "(" +arg_name +":"+ genInt() + "){" + arg_name + "}}\",\"variables\":null,\"operationName\":null}"
    
    elif scalar == 'URL':
        query = "{\"query\":\"query{"+field_name+ "(" +arg_name +":"+ genUrl() + "){" + arg_name + "}}\",\"variables\":null,\"operationName\":null}"
    
    elif scalar == 'JSON':
        query = "{\"query\":\"query{"+field_name+ "(" +arg_name +":"+ genJson() + "){" + arg_name + "}}\",\"variables\":null,\"operationName\":null}"
    
    elif scalar == 'FuzzyDateInt':
        query = "{\"query\":\"query{"+field_name+ "(" +arg_name +":"+ genFuzzyDateInt() + "){" + arg_name + "}}\",\"variables\":null,\"operationName\":null}"
    
    
    writeFile("Queries", scalar, field_name+"-"+arg_name, query) 

def parseFailedQuery(resp, payload):
    try:
        content = resp.text
        if not resp.status_code == 404:
            if "Cannot query field" in content:
                tests = ['inline fragment', 'requires type']
                if not any(x in content for x in tests):
                    if 'Did you mean' in content:
                        click.secho('[QUERY FAILED] ATTEMPTING SHAPE SHIFT AND RETRYING...', fg='red')
                        matches = re.findall(r'\\\".*?\\"', content)
                        find = "{"+matches[0].strip('\\"')+"}"
                        repl = "{"+matches[2].strip('\\"')+"}"
                        retry = payload.replace(find, repl)
                        return retry
    except ValueError:
        click.secho("ERROR PARSING RESPONSE BODY", fg='red')

    
    





def genStr(size=8, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

def genInt():
    return str(random.randint(0,999))

def genDoubleFloat():
    return round(random.uniform(10.1,999.5), 2)

def genBoolean():
    bools = ['true', 'false']
    return random.choice(bools)

def genId():
    return str(random.randint(100,9999))

def genDateTime():
    return datetime.now() - relativedelta(years=2)

def genEmail():
    return "%s@%s.com" % (genStr(), genStr())

def genNegFloat():
    return round(random.uniform(-10.1,-999.5), 2)

def genNegInt():
    return str(random.randint(0,-999))
    
def genPhone():
    return "+17895551234"
    
def genPostalCode():
    return "12345"

def genUrl():
    return "HTTP://%s.COM" % genStr()

def genJson():
    return '[{"_id":"5d6f4899eb64efd6db721e0c","index":0,"guid":"84c17e20-888e-4398-b64e-ea964252db08","isActive":true,"admin":true}]'

def genFuzzyDateInt(size=8, chars=string.digits):
    return "20170000"


@click.pass_context
def writeFile(ctx, kind, scalar, name, data):
    parentDir = ctx.obj['outdir']+"%s/" % kind

    try:
        os.mkdir(parentDir)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise

    file = open(parentDir+name+'-'+scalar+".json","x+")
    file.write(data)
    file.close()
    click.secho('| Request written to: '+kind+'/'+name+'-'+scalar+'.json', fg='green')
    return True