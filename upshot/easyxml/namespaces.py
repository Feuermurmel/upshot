# Re-export the null namespace.
from ..easyxml import Namespace as _Namespace, null


# Mostly copied from http://www.informit.com/articles/article.aspx?p=31837&seqNum=10
xhtml = _Namespace('http://www.w3.org/1999/xhtml', 'xhtml')
svg = _Namespace('http://www.w3.org/2000/svg')
xml = _Namespace('http://www.w3.org/XML/1998/namespace')
xlink = _Namespace('http://www.w3.org/1999/xlink')
xsd = _Namespace('http://www.w3.org/2001/XMLSchema')
xsi = _Namespace('http://www.w3.org/2001/XMLSchema-instance')
xsl = _Namespace('http://www.w3.org/1999/XSL/Transform')
