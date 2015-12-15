- List
	- Item 1
		- Item 2
			- Item 3

1. List
	1. Item 1
		1. Item 2
			1. Item 3

Some text. *Italic*. **Bold**. `Console`. http://example.com/. ~~Strikethrough~~. \(x^2\).

---

```tex
f(x) = \int_{-\infty}^\infty
	\hat f(\xi)\,e^{2 \pi i \xi x}
	\,d\xi
```

a \[
f(x) = \int_{-\infty}^\infty
	\hat f(\xi)\,e^{2 \pi i \xi x}
	\,d\xi
\] b

---

~~~py
class Dump:
	def __init__(element : Element):
		"""Foo"""
		
		print('''
			a
		''')
		
		buffer = io.BytesIO()
		generator = xml.sax.saxutils.XMLGenerator(buffer, 'utf-8', short_empty_elements = True)
		
		for prefix, namespace in _iter_namespace_mappings(element):
			generator.startPrefixMapping(prefix, namespace._uri)
		
		def walk(element) -> str:
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
~~~

---

Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.

> 	Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.

	Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.

~~~
Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
~~~

# Title

## Subtitle 2

### Subtitle 3

#### Subtitle 4

##### Subtitle 5

###### Subtitle 6
