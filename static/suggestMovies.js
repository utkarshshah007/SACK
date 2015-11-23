$(function(){
	$(".list-group-item").click(function() {
		$(".list-group-item").removeClass("active")
		$(this).addClass("active")

		var outdata = {};
		outdata['genre'] = $(this).text();
		console.log(outdata);

		$.post("suggestions", outdata, function (data) {

    		$("#movieYear").text(data["year"]);
    		$("#movieName").text(data["title"]);

    	});
	});
});