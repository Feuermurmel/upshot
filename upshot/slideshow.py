import os, markdown, pystache
from . import util, js, easyxml, assets
from .easyxml.namespaces import xhtml


katex = js.compile_from_resource('katex.js')
slideshow_template = util.get_resource('slideshow.mustache').decode()

assets_dir = os.path.join(os.path.dirname(__file__), 'assets')


class Slide:
	def __init__(self, title : str, level : int):
		self.title = title
		self.level = level
		self.body_fragment = []
		self.child_slides = []


class Slideshow:
	def __init__(self, slides : list, assets : list):
		self._slides = slides
		self._assets = assets
	
	def write(self, dest_dir, *, link_resources : bool):
		headers = []
		files = []
		
		for i in self._assets:
			asset = i.prepare()
			
			headers.extend(asset.header_fragment)
			files.extend(asset.files)
		
		slide_contexts = [dict(content = easyxml.dump_fragment(i.body_fragment)) for i in self._slides]
		context = dict(headers = easyxml.dump_fragment(headers), slides = slide_contexts)
		
		# To remove redundant namespace declarations.
		document = easyxml.dump(easyxml.load(pystache.Renderer().render(slideshow_template, context)))
		
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
	
	slides = []
	
	def walk_slides(slide : Slide):
		if slide.level >= 0:
			slides.append(slide)
		
		for i in slide.child_slides:
			walk_slides(i)
	
	walk_slides(slides_ancestry[0])
	
	return Slideshow(slides, [assets.slidy, assets.katex, assets.pygments])
