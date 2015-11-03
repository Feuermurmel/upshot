import os, argparse
from . import slideshow


def _parse_args():
	parser = argparse.ArgumentParser()
	
	parser.add_argument('source', help = 'Path of the source Markdown file.')
	parser.add_argument('destination', nargs = '?', help = 'Path of the directory to place the generated slideshow\'s index.xhtml and any necessary assets in. The directory will be create if it does not already exist. Defaults to the path of the source file with the \'.md\' suffix removed.')
	
	args = parser.parse_args()
	
	if args.destination is None:
		args.destination, _ = os.path.splitext(args.source)
	
	return args


def main(source, destination):
	slideshow.load_slideshow(source).write(destination)


def script_main():
	main(**vars(_parse_args()))
