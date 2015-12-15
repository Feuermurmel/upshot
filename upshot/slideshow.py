import os, markdown, pystache, itertools, re
from . import util, js, easyxml, assets
from .easyxml.namespaces import xhtml


katex = js.compile_from_resource('katex.js')
# slideshow_template = pystache.parse(util.get_resource('slideshow.mustache').decode(), )

# slideshow_template = pystache.Renderer(partials = dict(toc_node = util.get_resource('slideshow.mustache').decode()))

assets_dir = os.path.join(os.path.dirname(__file__), 'assets')


def mustache(template_name, context):
	class Partials:
		@staticmethod
		def get(name):
			return util.get_resource(name + '.mustache').decode()
	
	renderer = pystache.Renderer(partials = Partials)
	
	return renderer.render('{{>' + template_name + '}}', context)


class Slide:
	def __init__(self, title : str, level : int):
		self.title = title
		self.level = level
		self.body_fragment = []
		self.child_slides = []


class Slideshow:
	def __init__(self, root_slide : Slide, assets : list):
		self._root_slide = root_slide
		self._assets = assets
	
	def write(self, dest_dir, *, link_resources : bool):
		headers = []
		files = []
		
		for i in self._assets:
			asset = i.prepare()
			
			headers.extend(asset.header_fragment)
			files.extend(asset.files)
		
		id_counter = itertools.count(0)
		
		def get_slides_context(slide : Slide, fallback_title = ''):
			id = next(id_counter)
			title = slide.title or fallback_title
			nodes = [get_slides_context(x, '{} ({})'.format(title, i + 1)) for i, x in enumerate(slide.child_slides)]
			content = easyxml.dump_fragment(slide.body_fragment)
			
			return dict(id = id, title = title, nodes = nodes, content = content)
		
		context = dict(
			headers = easyxml.dump_fragment(headers),
			slides = get_slides_context(self._root_slide))
		
		# To remove redundant namespace declarations.
		document = easyxml.dump(easyxml.load(mustache('slideshow', context)))
		
		files.append(assets.create_bytes_file('index.xhtml', lambda: document.encode()))
		
		for i in files:
			i.write(dest_dir, link_file = link_resources)


def fixup_math(elem):
	return easyxml.load(katex(elem.text))


def fixup_pre(elem):
	"""
	Takes the text in 
	
	Also, it removes <code> elements inside <pre> elements. The GFM plugin outputs a <pre> inside a <div>, while indented code blocks are output as a <code> inside a <pre>, which makes consistent styling awkward.
	"""
	
	if len(elem) == 1:
		code, = elem
		
		if isinstance(code, easyxml.Element) and code.name == xhtml.code:
			elem[:] = code
	
	def iter_unwrapped_fragments():
		for i in elem:
			if isinstance(i, easyxml.Element):
				yield lambda x, i = i: i.name(x, attrs = i.attrs), i.text
			else:
				yield lambda x: x, i
	
	def iter_line_fragments():
		line = []
		
		for wrapper, text in iter_unwrapped_fragments():
			first, *rest = text.split('\n')
			
			if first:
				line.append((wrapper, first))
			
			for j in rest:
				yield line
				
				line = []
				
				if j:
					line.append((wrapper, j))
		
		if line:
			yield line
	
	def split_indentation(line_fragment):
		indentation = []
		content = []
		
		if line_fragment:
			for i, (wrapper, text) in enumerate(line_fragment):
				match = re.match('^ +', text)
				
				if match:
					indentation.append((wrapper, match.group()))
					
					if match.end() < len(text):
						content.append((wrapper, text[match.end():]))
				else:
					break
			else:
				i += 1
			
			content += line_fragment[i:]
		
		assert sum(len(i) for _, i in indentation) + sum(len(i) for _, i in content) == sum(len(i) for _, i in line_fragment)
		
		return indentation, content
	
	def dump_unwrapped_fragment(fragment):
		return easyxml.dump_fragment([wrapper(text) for wrapper, text in fragment])
	
	def get_line_context(line_fragment, newline):
		indentation, content = split_indentation(line_fragment)
		
		return dict(
			indentation_width = sum(len(x) for _, x in indentation),
			indentation = dump_unwrapped_fragment(indentation),
			content = dump_unwrapped_fragment(content),
			line_break = '\n' if newline else '')
	
	line_fragments = list(iter_line_fragments())
	line_contexts = [get_line_context(x, i < len(line_fragments) - 1) for i, x in enumerate(line_fragments)]
	
	return easyxml.load(mustache('code', dict(lines = line_contexts)))


def fixup_markdown_output(elem : easyxml.Element):
	if elem.name == xhtml.script and elem.attrs[xhtml.type].split(';')[0].strip() == 'math/tex':
		return fixup_math(elem)
	elif elem.name == xhtml.pre:
		return fixup_pre(elem)
	else:
		for i in elem:
			if isinstance(i, easyxml.Element):
				res = fixup_markdown_output(i)
				
				if res is not None:
					elem[elem.index(i)] = res


break_element_level = { x: i for i, x in enumerate([xhtml.h1, xhtml.h2, xhtml.h3, xhtml.h4, xhtml.h5, xhtml.h6, xhtml.hr]) }


def extract_slides(rendered_document):
	slides_ancestry = [Slide('', -1)]
	
	def add_slide(title, level):
		while slides_ancestry[-1].level >= level:
			del slides_ancestry[-1]
		
		new_slide = Slide(title, level)
		
		slides_ancestry[-1].child_slides.append(new_slide)
		slides_ancestry.append(new_slide)
	
	for i in rendered_document:
		if isinstance(i, easyxml.Element):
			level = break_element_level.get(i.name)
			
			if level is not None:
				add_slide(i.text, level)
		
		# Never add content to the root slide.
		if slides_ancestry[-1].level < 0:
			add_slide('', break_element_level[xhtml.hr])
		
		slides_ancestry[-1].body_fragment.append(i)
	
	return slides_ancestry[0]


def load_slideshow(markdown_file_path : str):
	markdown_output = markdown.markdown(
		util.read_file(markdown_file_path).decode(),
		output_format = 'xhtml1',
		extensions = ['gfm', 'math'])
	
	rendered_document = easyxml.load('<_ xmlns="http://www.w3.org/1999/xhtml">{}</_>'.format(markdown_output))
	
	fixup_markdown_output(rendered_document)
	
	root_slide = extract_slides(rendered_document)
	
	return Slideshow(root_slide, [assets.katex, assets.pygments, assets.upshot])
