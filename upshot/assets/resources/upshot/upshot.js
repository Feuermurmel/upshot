upshot = (function () {
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
	
	function getCurrentSlide() {
		var currentSlide = $(':target');
		
		if (currentSlide.length != 1) {
			currentSlide = $('.slide').first();
		}
		
		return currentSlide;
	}
	
	function gotoSlide(slideElem) {
		if (slideElem.length == 1) {
			window.location.replace('#' + slideElem.attr('id'));
		}
	}
	
	return function () {
		$(document).on('keydown', function (e) {
			if (e.which == keyCodes.left) {
				gotoSlide(getCurrentSlide().prev('.slide'));
			} else if (e.which == keyCodes.right) {
				gotoSlide(getCurrentSlide().next('.slide'));
			}
		});
		
		$(window).on('hashchange', function () {
			console.log(document.location.hash);
		})
		
		$('body').addClass('slideshow');
	};
}());