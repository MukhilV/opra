function isTruncated(ele) {
	return (ele.offsetWidth < ele.scrollWidth);
}

function addTooltips(event) {
	$("th, .li_item").each(function(i, ele) {
		if (isTruncated(ele)) {
			$(ele).addClass("truncated");
			// simple tooltip for now
			$(ele).attr("title", $(ele).text());
		}
		else {
			$(ele).removeClass("truncated");
			// remove title tooltip
			$(ele).attr("title", "");
		}
	});
}

window.addEventListener("resize", addTooltips);

document.addEventListener("DOMContentLoaded", function() {
	/* use this to add jQuery or Introjs tooltips when possible:
	$("th, .li_item").hover(
		function(event) {
			if ($(event.target).hasClass("truncated"))
				console.log("display tooltip please");
		},
		function(event) {
			if ($(event.target).hasClass("truncated"))
				console.log("remove tooltip please");
		}
	);
	*/
	addTooltips();
});

function UICheckboxes(){
	if(document.getElementById("twocol_checkbox").checked 
	|| document.getElementById("onecol_checkbox").checked 
	||document.getElementById("slider_checkbox").checked 
	||document.getElementById("star_checkbox").checked
	||document.getElementById("yesno_checkbox").checked 
	||document.getElementById("yesno2_checkbox").checked
	||document.getElementById("budgetUI_slider_checkbox").checked
	||document.getElementById("listUI_checkbox").checked
	||document.getElementById("InfiniteBudgetUI_checkbox").checked
	){
		return true;
	}
	alert("You must choose at least one voting interface!");
	event.preventDefault();
	return false;
}