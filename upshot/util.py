import pkg_resources, inspect, os, abc


def get_resource(name, frames_back = 0) -> bytes:
	module = _get_calling_module(frames_back + 1)
	
	with pkg_resources.resource_stream(module, name) as file:
		return file.read()


def list_resources(root_name, frames_back = 0):
	module = _get_calling_module(frames_back + 1)
	res = []
	
	def walk(path):
		if pkg_resources.resource_isdir(module, path):
			for i in pkg_resources.resource_listdir(module, path):
				if not i.startswith('.'):
					walk(os.path.join(path, i))
		else:
			res.append(path)
	
	walk(root_name)
	
	return res


def _get_calling_module(frames_back = 0):
	frame = inspect.currentframe()
	
	for _ in range(frames_back + 1):
		frame = frame.f_back
	
	return frame.f_globals['__name__']


def read_file(path):
	with open(path, 'rb') as file:
		return file.read()


def write_file(path, data):
	dir_path = os.path.dirname(path)
	
	if not os.path.exists(dir_path):
		os.makedirs(dir_path)
	
	with open(path, 'wb') as file:
		file.write(data)


class Hashable(metaclass = abc.ABCMeta):
	def __eq__(self, other):
		return type(self) is type(other) and self._hashable_key() == other._hashable_key()
	
	def __hash__(self):
		return hash(self._hashable_key())
	
	@abc.abstractmethod
	def _hashable_key(self): pass
