$(function(){

	$(document).ready(function() {
		var firstdata = {};
		firstdata['genre'] = $('.active').text();
		$.post("suggestions", firstdata, function (data) {

	    		$("#movieYear").text(data["year"]);
	    		$("#movieName").text(data["title"]);

	    });
	});


	$(".list-group-item").click(function() {
		$(".list-group-item").removeClass("active")
		$(this).addClass("active")

		var outdata = {};
		outdata['genre'] = $(this).text();

		$.post("suggestions", outdata, function (data) {

    		$("#movieYear").text(data["year"]);
    		$("#movieName").text(data["title"]);

    	});
	});

	$("#movieName").click(function() {
		var name = $("#movieName").text().split(" ");

		
		var url = "https://www.bing.com/search?q=";
		var s;
		for (s in name) {
			url += name[s] + "+";
		}
		url += "trailer"

		window.location.href = url;

	});

});