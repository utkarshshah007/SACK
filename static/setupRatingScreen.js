$(function(){
	$('.movie-slider').slider();

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

