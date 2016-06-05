var upshot = function () {
	'use strict';

	var keyCodes = {
		backspace: 8,
		comma: 188,
		del: 46,
		down: 40,
		end: 35,
		enter: 13,
		escape: 27,
		home: 36,
		left: 37,
		pageDown: 34,
		pageUp: 33,
		period: 190,
		right: 39,
		space: 32,
		tab: 9
	};

	// Add help text.
	var helpText = 'Toggle slideshow mode with ESC, switch slides with LEFT and RIGHT.';
	var helpElem = $('<div id="help">' + helpText + '</div>');

	$('body').prepend(helpElem);

	var slideElems = $('.slide');
	var firstSlideElem = slideElems.first();
	var lastSlideElem = slideElems.last();
	var tocElem = $('#toc');

	// Set an ID to allow styling.
	var slideNumberFloatElem = $('<div id="slide-number"><a href="#toc"><span/> / <span/></a></div>');
	var slideNumberElem = $('span:eq(0)', slideNumberFloatElem);
	var slideCountElem = $('span:eq(1)', slideNumberFloatElem);

	tocElem.prepend(slideNumberFloatElem);

	// Set slide count.
	slideCountElem.text(lastSlideElem.attr('id'));

	function getCurrentSlide() {
		return $('.slide:target');
	}

	function gotoSlide(slideElem) {
		if (slideElem.length !== 1) {
			slideElem = firstSlideElem;
		}

		var id = slideElem.attr('id');

		// Set hash (which shows/jumps to the right .slide element).
		window.location.replace('#' + id);
	}

	function toggleSlideshowMode() {
		$('body').toggleClass('handout').toggleClass('slideshow');
	}

	$(document).on('keydown', function (e) {
		if (e.which === keyCodes.left) {
			gotoSlide(getCurrentSlide().prev('.slide'));
		} else if (e.which === keyCodes.right) {
			gotoSlide(getCurrentSlide().next('.slide'));
		} else if (e.which === keyCodes.escape) {
			toggleSlideshowMode();

			// Go to the first slide, if none is selected already.
			gotoSlide(getCurrentSlide());
		}
	});

	function handleSlideChanged() {
		var slideElem = getCurrentSlide();

		if (slideElem.length === 1) {
			var id = slideElem.attr('id');
			var tocListElem = $('#toc-' + id);

			// Show/hide toc elements.
			tocListElem.parentsUntil('#toc', 'li').andSelf().each(function () {
				var x = $(this);

				x.removeClass('hidden');
				x.siblings().addClass('hidden');
			});

			// Hide the children of the current slide.
			tocListElem.children('ul').children('li').addClass('hidden');

			// Set slide number.
			slideNumberElem.text(id);
		}
	}

	$(window).on('hashchange', handleSlideChanged);
	handleSlideChanged();
};
