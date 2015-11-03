var katex = require('katex');

function apply(math, display) {
	return katex.renderToString(math, { displayMode: display });
}
