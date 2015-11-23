$(function(){
	$(".list-group-item").click(function() {
			$(".list-group-item").removeClass("active")
			$(this).addClass("active")
	});
});