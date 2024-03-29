$(function(){
	$('.movie-slider').slider();

	var load_movie = function(outdata) {
		$.post("suggestions", outdata, function (data) {

	    		$("#movieYear").text(data["year"]);
	    		$("#movieName").text(data["title"]);
	    		$("#movieReviews").text(data["num_ratings"] + " reviews");
	    		$(".loading-movies").addClass("hide");
	    		$(".suggested-movie").removeClass("hide");
	    		$(".movie-slider").attr('id', data["mid"]);
	    		$(".movie-slider").attr('genre', data["genre"]);
	    		$(".img-responsive").attr('src',data["picture"]);

	    		// Updating Stars
	    		$(".stars").html("");
	    		var rating = Math.round(data["avg_rating"]);
	    		for (var i = 0; i < 5; i++) {
	    			if (i < rating) {
	    				$(".stars").append("<span class='glyphicon glyphicon-star'></span>");
	    			} else {
	    				$(".stars").append("<span class='glyphicon glyphicon-star-empty'></span>");
	    			}	
	    		};
	    		$(".stars").append(" " + (Math.round(data["avg_rating"] * 100) / 100) + " stars")
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

	$('#rate').click(function(){
		var outdata = {};
		outdata['mid'] = $(this).parent().find(".movie-slider").attr('id');
		outdata['rating'] = $(this).parent().find(".movie-slider").slider('getValue');
		outdata['genre'] = $(this).parent().find(".movie-slider").attr('genre');
	    $.post("suggestions/rate-movie", outdata, function (data) {
	    	$('#' + data.genre).click();
	    });
	});

	$('#new-suggestion').click(function(){
		var outdata = {};
		outdata['mid'] = $(this).parent().find(".movie-slider").attr('id');
		outdata['genre'] = $(this).parent().find(".movie-slider").attr('genre');
	    $.post("suggestions/get-new-suggestion", outdata, function (data) {
	        $('#' + data.genre).click();
	    });
	});

});