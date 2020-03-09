/* To avoid CSS expressions while still supporting IE 7 and IE 6, use this script */
/* The script tag referencing this file must be placed before the ending body tag. */

/* Use conditional comments in order to target IE 7 and older:
	<!--[if lt IE 8]><!-->
	<script src="ie7/ie7.js"></script>
	<!--<![endif]-->
*/

(function() {
	function addIcon(el, entity) {
		var html = el.innerHTML;
		el.innerHTML = '<span style="font-family: \'jolly-icons-free\'">' + entity + '</span>' + html;
	}
	var icons = {
		'hdg-mobile': '&#x21;',
		'hdg-printer': '&#x22;',
		'hdg-map-route': '&#x23;',
		'hdg-pin': '&#x24;',
		'hdg-mail': '&#x25;',
		'hdg-paperplane': '&#x26;',
		'hdg-settings': '&#x27;',
		'hdg-gear': '&#x28;',
		'hdg-network': '&#x29;',
		'hdg-like-thumbs-up': '&#x2a;',
		'hdg-globe': '&#x2b;',
		'hdg-bomb': '&#x2c;',
		'hdg-lightning': '&#x2d;',
		'hdg-picture': '&#x2e;',
		'hdg-cloud': '&#x2f;',
		'hdg-line-chart': '&#x30;',
		'hdg-briefcase': '&#x31;',
		'hdg-checklist-todo': '&#x32;',
		'hdg-folder': '&#x33;',
		'hdg-bookmark': '&#x34;',
		'hdg-savings': '&#x35;',
		'hdg-shopping-cart-ecommerce': '&#x36;',
		'hdg-gifts-giftbox': '&#x37;',
		'hdg-coffee': '&#x38;',
		'hdg-food-chicken-leg': '&#x39;',
		'hdg-food-apple': '&#x3a;',
		'hdg-icecream': '&#x3b;',
		'hdg-trumpet': '&#x3c;',
		'hdg-pipe': '&#x3d;',
		'hdg-diamond-ruby': '&#x3e;',
		'hdg-face-robot': '&#x3f;',
		'hdg-social-facebook': '&#x40;',
		'hdg-social-google-gplus': '&#x41;',
		'hdg-social-twitter-tweet-bird': '&#x42;',
		'hdg-social-dribbble': '&#x43;',
		'hdg-social-github-octocat': '&#x44;',
		'0': 0
		},
		els = document.getElementsByTagName('*'),
		i, c, el;
	for (i = 0; ; i += 1) {
		el = els[i];
		if(!el) {
			break;
		}
		c = el.className;
		c = c.match(/hdg-[^\s'"]+/);
		if (c && icons[c[0]]) {
			addIcon(el, icons[c[0]]);
		}
	}
}());
