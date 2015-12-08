import os, markdown, pystache, collections, itertools
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


break_element_level = { x: i for i, x in enumerate([xhtml.h1, xhtml.h2, xhtml.h3, xhtml.h4, xhtml.h5, xhtml.h6, xhtml.hr]) }


def load_slideshow(markdown_file_path : str):
	markdown_output = markdown.markdown(
		util.read_file(markdown_file_path).decode(),
		output_format = 'xhtml1',
		extensions = ['gfm', 'math'])
	
	rendered_document = easyxml.load('<_ xmlns="http://www.w3.org/1999/xhtml">{}</_>'.format(markdown_output))
	
	def replace_math(elem : easyxml.Element):
		for i in elem.child_elements:
			if i.name == xhtml.script:
				elem[elem.index(i)] = easyxml.load(katex(i.text))
			else:
				replace_math(i)
	
	replace_math(rendered_document)
	
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
	
	return Slideshow(slides_ancestry[0], [assets.upshot, assets.katex, assets.pygments])
