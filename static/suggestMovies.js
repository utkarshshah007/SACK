$(function(){

	var load_movie = function(outdata) {
		$.post("suggestions", outdata, function (data) {

	    		$("#movieYear").text(data["year"]);
	    		$("#movieName").text(data["title"]);
	    		$("#movieReviews").text(data["num_ratings"] + " reviews");
	    		$(".loading-movies").addClass("hide");
	    		$(".suggested-movie").removeClass("hide");

	    });
	}

	$(document).ready(function() {
		var firstdata = {};
		firstdata['genre'] = $('.active').text();
		load_movie(firstdata);
	});


	$(".list-group-item").click(function() {
		$(".list-group-item").removeClass("active");
		$(this).addClass("active");
		$(".suggested-movie").addClass("hide");
		$(".loading-movies").removeClass("hide");

		var outdata = {};
		outdata['genre'] = $(this).text();

		load_movie(outdata);
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