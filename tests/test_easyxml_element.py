from easyxml_test_util import *


ns = Namespace('http://example.com/')

elem1 = ns.foo()
elem2 = ns.bar()


def test_create():
	element = Element(ns.foo, { ns.a: '123' }, ['test'])
	
	assert element.name == ns.foo
	assert set(element.attrs.items()) == { (ns.a, '123') }
	assert list(element) == ['test']


def test_create_attribute_no_namespace():
	with pytest.raises(ValueError):
		Element(ns.foo, { null.a: 'a' })


def test_create_attribute_invalid_type():
	with pytest.raises(TypeError):
		Element(ns.foo, { ns.a: 1 })


def test_create_content_invalid_type():
	with pytest.raises(TypeError):
		Element(ns.foo, { }, [1])


def test_compare():
	foo1 = ns.foo()
	foo2 = ns.foo()
	bar = ns.foo()
	
	assert foo1 != bar
	assert foo1 != foo2
	assert foo1 == foo1


def crate_multiple_text():
	element = ns.foo('foo', 'bar')
	
	assert list(element) == ['foobar']


def crate_multiple_text():
	element = ns.foo('foo', 'bar')
	
	assert list(element) == ['foobar']
