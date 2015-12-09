$(function(){
	$('.movie-slider').slider();

    $('.NSBut').click(function(){
    	var genre = $(this).closest(".container").attr('id')
    	var outdata = {};
    	outdata['genre'] = genre;
    	var $curr = $(this)

    	$.post("setup-rating/get-next-movie", outdata, function (data) {
	    	$curr.parent().find('.movie-title').text(data.movie_title);
			$curr.parent().find('.movie-slider').attr('id', data.mid);
	    });
		
	});

	$('#submitButton').click(function(){
		var outdata = {};

		$('.movie-slider').each( function(index) {
			outdata[$(this).attr('id')] = $(this).slider('getValue');
		});	

	    $.post("setup-rating", 	outdata, function (data) {
	    	window.location.href = data;
	    });


	});
});

