import collections.abc, xml.sax.handler, xml.sax.saxutils, xml.sax.xmlreader, io, collections
from .. import util


__all__ = 'Namespace Name Element load load_fragment dump dump_fragment'.split()


def _check_child(child):
	if not isinstance(child, str) and not isinstance(child, Element):
		raise TypeError('child is neither a str nor an Element instance: {}'.format(child))


class Namespace(util.Hashable):
	"""
	Not a str subclass because no-one wants to compare with the full namespace URI anyways.
	"""
	
	def __init__(self, uri : str, preferred_prefix : str = None):
		# TODO: Check for valid xml identifiers.
		if not isinstance(uri, str):
			raise TypeError('uri must be a str instance: {}'.format(uri))
		
		if preferred_prefix is not None and not isinstance(preferred_prefix, str):
			raise TypeError('preferred_prefix must be None ro a str instance: {}'.format(uri))
		
		self._uri = uri
		self._preferred_prefix = preferred_prefix
	
	def __repr__(self):
		return 'Namespace({!r})'.format(self._uri)
	
	def __str__(self):
		if self._uri:
			return '{' + self._uri + '}'
		else:
			return ''
	
	def __bool__(self):
		return bool(self._uri)
	
	def __getattr__(self, item):
		if item.startswith('_'):
			# Prevent confusing errors when misspelling attribute access for a real Namespace attribute.
			raise AttributeError('Cannot create Name object for identifiers starting with _ using attribute access.')
		else:
			return Name(self, item)
			
	
	def _hashable_key(self):
		return self._uri	


null = Namespace('')


def _cast_namespace(namespace):
	if not isinstance(namespace, Namespace):
		namespace = Namespace(namespace)
	
	return namespace


class Name(tuple):
	__slots__ = []
	
	# noinspection PyInitNewSignature
	@staticmethod
	def __new__(cls, namespace : Namespace, id : str):
		namespace = _cast_namespace(namespace)
		
		if not isinstance(id, str):
			raise TypeError('id is not a str instance: {}'.format(id))
		
		if not id:
			raise TypeError('The id of a name may not be empty.')
		
		return super().__new__(cls, (namespace, id))
	
	def __repr__(self):
		return 'Name({!r}, {!r})'.format(self.namespace._uri, self.id)
	
	def __str__(self):
		return str(self.namespace) + self.id
	
	def __call__(self, *args, **kwargs):
		return Element(self, kwargs, args)
	
	@property
	def namespace(self):
		return self[0]
	
	@property
	def id(self):
		return self[1]


def _cast_name(name, element_namespace : Namespace = ''):
	if isinstance(name, Name):
		return name
	elif isinstance(name, tuple):
		return Name(*name)
	else:
		return Name(element_namespace, name)


# noinspection PyAbstractClass
class Element(collections.abc.MutableSequence):
	__slots__ = '_name _attributes _children'.split()
	
	def __init__(self, name : Name, attributes : dict = { }, children : list = []):
		self._name = _cast_name(name)
		self._attributes = { }
		self._children = []
		
		# Use accessors to get validation for free.
		self.attrs.update(attributes)
		self[:] = children
	
	def __repr__(self):
		return 'Element({!r}, {!r}, {!r})'.format((self.name.namespace._uri, self.name.id), self._attributes, self._children)
	
	def __str__(self):
		def iter_parts():
			yield '<'
			yield self._name
			
			for name, value in self._attributes.items():
				yield ' '
				yield name
				yield '='
				yield repr(value)
			
			if self._children:
				yield '>'
				
				for i in self._children:
					yield i
				
				yield '</>'
			else:
				yield ' />'
		
		return ''.join(map(str, iter_parts()))
	
	def __getitem__(self, index):
		return self._children[index]
	
	def __setitem__(self, index, value):
		if not isinstance(index, slice):
			self[index:index + 1] = value,
		else:
			def iter_elements():
				for i in value:
					_check_child(i)
					
					if isinstance(i, Element):
						# Copy elements assigned as children. This will create a deep copy.
						i = Element(i.name, i.attrs, i)
					
					yield i
			
			self._children[index] = list(iter_elements())
			
			self._fixup_children()
	
	def __delitem__(self, index):
		self[index:index] = ()
	
	def __len__(self):
		return len(self._children)
	
	def insert(self, index, value):
		self[index:index] = value,
	
	def _fixup_children(self):
		def iter_children():
			current_text_node = ''
			
			for i in self._children:
				if isinstance(i, str):
					current_text_node += i
				else:
					if current_text_node:
						yield current_text_node
						
						current_text_node = ''
					
					yield i
			
			if current_text_node:
				yield current_text_node
		
		self._children = list(iter_children())
	
	@property
	def name(self):
		return self._name
	
	@property
	def text(self):
		return ''.join(i.text if isinstance(i, Element) else i for i in self)
	
	@property
	def attrs(self):
		return AttributeMap(self)
	
	@property
	def child_elements(self):
		return [i for i in self if isinstance(i, Element)]


# noinspection PyAbstractClass
class AttributeMap(collections.abc.MutableMapping):
	__slots__ = '_element'.split()
	
	def __init__(self, element : Element):
		self._element = element
	
	def __repr__(self):
		return '<AttributeMap {!r}>'.format(self._element)
	
	def __getitem__(self, key):
		return self._element._attributes[self._cast_key(key)]
	
	def __setitem__(self, key, value):
		if not isinstance(value, str):
			raise TypeError('value is not a str instance: {}'.format(value))
		
		key = _cast_name(key, self._element._name.namespace)
		
		self._element._attributes[self._cast_key(key)] = value
	
	def __delitem__(self, key):
		del self._element._attributes[self._cast_key(key)]
	
	def __iter__(self):
		return iter(self._element._attributes)
	
	def __len__(self):
		return len(self._element._attributes)
	
	def _cast_key(self, name):
		name = _cast_name(name, self._element._name.namespace)
		
		if not name.namespace and self._element._name.namespace:
			raise ValueError('Attributes of elements with a namespace must also have a namespace. XML requires this. :(')
		
		return name


def load(content : str):
	element_info_stack = [(None, None, [])]
	
	class Handler(xml.sax.handler.ContentHandler):
		def characters(self, content):
			element_info_stack[-1][2].append(content)
		
		def ignorableWhitespace(self, whitespace):
			self.characters(whitespace)
		
		def startElementNS(self, name, _, attrs):
			if name[0] is None:
				name = name[1]
			
			def iter_attrs():
				for attr_name, value in attrs.items():
					# Expat does not report namespaces of attributes if they are inherited from the element name.
					if attr_name[0] is None:
						attr_name = attr_name[1]
					
					yield attr_name, value
			
			element_info_stack.append((name, list(iter_attrs()), []))
		
		def endElementNS(self, name, _):
			element = Element(*element_info_stack.pop())
			
			element_info_stack[-1][2].append(element)
	
	parser = xml.sax.make_parser()
	
	parser.setContentHandler(Handler())
	parser.setFeature(xml.sax.handler.feature_namespaces, True)
	parser.parse(io.BytesIO(content.encode()))
	
	return element_info_stack[0][2][0]


def load_fragment(content : str, default_namespace = null):
	fragment_container = dump(default_namespace.a('{}'))
	
	# FIXME: Breaks if the namespace contains a {} part.
	return list(load(fragment_container.format(content)))


def _gather_namespaces(element : Element):
	namespaces = set()
	
	def walk(element):
		namespaces.add(element.name.namespace)
		
		for i in element.attrs:
			namespaces.add(i.namespace)
		
		for i in element.child_elements:
			walk(i)
	
	walk(element)
	
	return namespaces


def _iter_namespace_mappings(element : Element):
	"""
	Only the empty namespace -> No mappings (use empty namespace as default namespaces).
	The empty namespace and some other namespaces -> mappings for all other namespaces (use empty namespace as default namespaces).
	Only non-empty namespace -> Mappings for all namespaces, use namespace of root element as default namespace
	"""
	
	namespaces = _gather_namespaces(element)
	
	if null in namespaces:
		namespaces.remove(null)
	else:
		root_namespace = element.name.namespace
		namespaces.remove(root_namespace)
		
		yield None, root_namespace
	
	for i, namespace in enumerate(sorted(namespaces)):
		yield 'ns{}'.format(i + 1), namespace


def _get_name_tuple(name : Name):
	namespace, id = name
	
	return namespace._uri, id


def dump(element : Element) -> str:
	buffer = io.BytesIO()
	generator = xml.sax.saxutils.XMLGenerator(buffer, 'utf-8', short_empty_elements = True)
	
	for prefix, namespace in _iter_namespace_mappings(element):
		generator.startPrefixMapping(prefix, namespace._uri)
	
	def walk(element):
		name = _get_name_tuple(element.name)
		attrs = collections.OrderedDict((_get_name_tuple(name), value) for name, value in sorted(element.attrs.items()))
		
		generator.startElementNS(name, None, attrs)
		
		for i in element:
			if isinstance(i, Element):
				walk(i)
			else:
				generator.characters(i)
		
		generator.endElementNS(name, None)
	
	walk(element)
	
	return buffer.getvalue().decode()


def dump_fragment(fragment : list):
	def iter_parts():
		for i in fragment:
			if isinstance(i, Element):
				yield dump(i)
			else:
				yield i
	
	return ''.join(iter_parts())
