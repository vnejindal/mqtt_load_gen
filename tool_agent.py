import os
import json
import commands
from bottle import route, run, Bottle, request


"""
JSON elements: 
config name
start_offset
load_count
"""

start_script = 'sh start_container.sh'

@route('/tool/start', method='POST')
def tool_start():
     #try:
#         print request.body
         rbody = json.load(request.body)
         config = rbody['config']
         soffset = rbody['soffset']
         tcount = rbody['total_count']
         scmd = ' '.join([start_script, config, str(soffset), str(tcount)])
         (rval, op) = commands.getstatusoutput(scmd)
         return {"success" : True if rval is 0 else False, "error" : op}
     #except:
     #    return {"success" : False, "error" : "Invalid Request. Some Exception" }
@route('/tool/stop', method='POST')
def tool_stop():
    scmd = 'sh stop_container.sh'
    (rval, op) = commands.getstatusoutput(scmd)
    return {"success" : True if rval is 0 else False, "error" : op}
    

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 9876))
    run(host='0.0.0.0', port=port, debug=True)
