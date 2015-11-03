from easyxml_test_util import *


def test_construct():
	Namespace('http://example.com/')


def test_compare():
	ns1 = Namespace('http://example.com/1')
	ns1b = Namespace('http://example.com/1')
	ns2 = Namespace('http://example.com/2')
	
	assert ns1 == ns1
	assert ns1 == ns1b
	assert ns1 != ns2


def test_create_name():
	ns = Namespace('http://example.com/')
	
	foo = ns.foo
	
	assert foo.namespace == ns
	assert foo.id == 'foo'


def test_booleanness():
	assert bool(Namespace('http://example.com/')) is True
	assert bool(Namespace('')) is False
