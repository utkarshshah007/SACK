$(function(){
	$('.movie-slider').slider();

    $('.NSBut').click(function(){
		$(this).parent().find('.movie-title').text("New title");
	});

	$('#submitButton').click(function(){
		outdata = {};

		$('.movie-slider').each( function(index) {
			outdata[$(this).attr('id')] = $(this).slider('getValue');
		});	

	    $.post("setup-rating", 	outdata, function (data) {
	    	window.location.href = data;
	    });


	});
});

