# Some random stuff used by many test cases.
import pytest, xml.sax
from upshot.easyxml import *
from upshot.easyxml.namespaces import null


def elements_check_equal(x, y):
	assert x.name == y.name
	assert dict(x.attrs) == dict(y.attrs)
	assert len(x) == len(y)
	
	for ix, iy in zip(x, y):
		if isinstance(ix, Element):
			assert isinstance(iy, Element)
			
			elements_check_equal(ix, iy)
		else:
			assert isinstance(iy, str)
			assert ix == iy
