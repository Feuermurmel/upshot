var handlebars = require('handlebars');
var template = null;

function apply(source, context) {
	template = handlebars.compile(source);
	
	return template(context);
}
