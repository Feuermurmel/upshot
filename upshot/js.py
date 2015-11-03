import execjs, sys, os
from . import util


# Calling venv/bin/python directly without activating the virtualenv will not adjust NODE_PATH.
def fix_node_path():
	if hasattr(sys, 'real_prefix'):
		node_path = os.environ.get('NODE_PATH')
		node_modules_path = os.path.join(sys.prefix, 'lib/node_modules')
		
		os.environ['NODE_PATH'] = node_modules_path + ('' if node_path is None else ':' + node_path)

fix_node_path()


runtime = execjs.get("Node")


def compile(code : str):
	context = runtime.compile(code)
	
	def function(*args):
		return context.call('apply', *args)
	
	return function


def compile_from_resource(name : str):
	return compile(util.get_resource(name, 1).decode())
