from easyxml_test_util import *


ns = Namespace('http://example.com/')


def test_construct():
	name = Name(ns, 'foo')
	
	assert name.namespace == ns
	assert name.id == 'foo'


def test_compare():
	foo1 = ns.foo
	foo2 = ns.foo
	bar = ns.bar
	
	assert foo1 == foo1
	assert foo1 == foo2
	assert foo1 != bar


def test_tuple():
	name = Name(ns, 'foo')
	namespace, id = name
	
	assert namespace == ns
	assert id == 'foo'


def test_compare_tuple():
	foo = ns.foo
	
	assert foo == (ns, 'foo')


def test_create_element():
	name = ns.foo
	element = name('test', '123', a = '1', b = '2')
	
	elements_check_equal(element, Element(ns.foo, { ns.a: '1', ns.b: '2' }, ['test123']))


def test_create_element_no_namespace():
	name = null.foo
	element = name(a = '1')
	
	elements_check_equal(element, Element(null.foo, { null.a: '1' }))


def test_create_element_pass_name_dict():
	"""
	Used to check wether this restriction has been removed: https://cuu508.wordpress.com/2011/01/27/keywords-must-be-strings/
	"""
	
	attrs = { null.a: '1' }
	
	with pytest.raises(TypeError):
		element = null.foo(**attrs)


def test_create_element_attrs_dict():
	attrs = { null.a: '1' }
	
	element = null.foo(attrs = attrs)
	
	elements_check_equal(element, Element(null.foo, { null.a: '1' }))


def test_create_element_attrs_attr():
	element = null.foo(attrs = '1')
	
	elements_check_equal(element, Element(null.foo, { null.attrs: '1' }))


def test_create_element_attrs_attr_multiple():
	element = null.foo(attrs = '1', b = '2')
	
	elements_check_equal(element, Element(null.foo, { null.attrs: '1', null.b: '2' }))


def test_create_element_attrs_dict_attrs_attr():
	attrs = { null.attrs: '1' }
	
	element = null.foo(attrs = attrs)
	
	elements_check_equal(element, Element(null.foo, { null.attrs: '1' }))


def test_create_element_attrs_dict_attrs_attr_both():
	attrs = { null.a: '1' }
	
	with pytest.raises(ValueError):
		null.foo(attrs = attrs, b = '2')
