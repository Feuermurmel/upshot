from easyxml_test_util import *


def test_dump_load_round_trip():
	cases = [
		'<a />',
		'<a b="" />',
		'<foo:a b="" xmlns:foo="A" />',
		'<a foo:b="" xmlns:foo="A" />',
		'<foo:a bar:b="" xmlns:foo="A" xmlns:bar="B" />',
		'<foo:a xmlns:foo="A"><b /></foo:a>']
	
	for i in cases:
		doc1 = load(i)
		output = dump(doc1)
		doc2 = load(output)
		
		elements_check_equal(doc1, doc2)
