from easyxml_test_util import *


ns_A = Namespace('A')
ns_B = Namespace('B')


def test_parse_basic():
	doc = load('<a b="" />')
	
	assert doc.name == null.a
	assert list(doc.attrs) == [null.b]


def test_parse_default_namespace():
	doc = load('<a b="" xmlns="A" />')
	
	assert doc.name == ns_A.a
	assert list(doc.attrs) == [ns_A.b]


def test_parse_unused_namespace():
	doc = load('<a b="" xmlns:foo="A" />')
	
	assert doc.name == null.a
	assert list(doc.attrs) == [null.b]


def test_parse_attribute_inherited_namespace():
	doc = load('<foo:a b="" xmlns:foo="A" />')
	
	assert doc.name == ns_A.a
	assert list(doc.attrs) == [ns_A.b]


def test_parse_attribute_different_namespace():
	doc = load('<foo:a bar:b="" xmlns:foo="A" xmlns:bar="B" />')
	
	assert doc.name == ns_A.a
	assert list(doc.attrs) == [ns_B.b]


def test_parse_apostrophe_attrs():
	doc = load('<a b=\'"\' />')
	
	assert doc.name == null.a
	assert list(doc.attrs.items()) == [(null.b, '"')]


def test_parse_entities_attributes():
	doc = load('<a b="&lt;&gt;&quot;&apos;&amp;" />')
	
	assert list(doc.attrs.items()) == [(null.b, '<>"\'&')]


def test_parse_entities_text():
	doc = load('<a>&lt;&gt;&quot;&apos;&amp;</a>')
	
	assert list(doc) == ['<>"\'&']


def test_parse_attributes():
	doc = load('<a b=">\'" />')
	
	assert list(doc.attrs.items()) == [(null.b, '>\'')]


def test_parse_text():
	doc = load('<a>>"\'</a>')
	
	assert list(doc) == ['>"\'']


def test_parse_cdata():
	doc = load('<a><![CDATA[<>"\'&]]></a>')
	
	assert list(doc) == ['<>"\'&']


def test_parse_cdata_concat():
	doc = load('<a><![CDATA[foo]]>*<![CDATA[bar]]></a>')
	
	assert list(doc) == ['foo*bar']


def test_invalid_characters():
	cases = [
		'<'
		'>',
		'&',
		'<a b="<">',
		'<a b=""">']
	
	for i in cases:
		with pytest.raises(xml.sax.SAXParseException):
			load(i)


def test_invalid_tags():
	cases = [
		'<a>',
		'<a></b>',
		'</b>']
	
	for i in cases:
		with pytest.raises(xml.sax.SAXParseException):
			load(i)


def test_invalid_syntax():
	cases = [
		'<>',
		'</>',
		'<a b=>',
		'<a b=">',
		'<a>&<a>',
		'<a>&;<a>',
		'<a b="&" />',
		'<a b="&;" />']
	
	for i in cases:
		with pytest.raises(xml.sax.SAXParseException):
			load(i)


def test_invalid_escapes():
	cases = [
		'<a>&xy;</a>',
		'<a>&#-1;</a>',
		'<a>&#10000000;</a>']
	
	for i in cases:
		with pytest.raises(xml.sax.SAXParseException):
			load(i)


def test_load_fragment():
	fragment = load_fragment('<a /><b></b>')
	
	for x, y in zip(fragment, [null.a(), null.b()]):
		elements_check_equal(x, y)


def test_load_fragment_with_namespace():
	fragment = load_fragment('<a /><b xmlns="B"></b>', ns_A)
	
	for x, y in zip(fragment, [ns_A.a(), ns_B.b()]):
		elements_check_equal(x, y)
