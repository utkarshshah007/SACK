$(function(){
	$('#movie1').slider();
	$('#movie2').slider();
	$('#movie3').slider();
	$('#movie4').slider();
	$('#movie5').slider();

	$("#submitButton").click(function(){
		console.log("Button Clicked")
		var value = $('#movie1').slider('getValue');
	    var value2 = $('#movie2').slider('getValue');
	    var value3 = $('#movie3').slider('getValue');
	    var value4 = $('#movie4').slider('getValue');
	    var value5 = $('#movie5').slider('getValue');

		outdata = {};
		outdata['movie1'] = value;
		outdata['movie2'] = value2;
		outdata['movie3'] = value3;
		outdata['movie4'] = value4;
		outdata['movie5'] = value5;

	    $.post("setup-rating", 	outdata, function (data) {
	    	window.location.href = data;
	    });
	});
});

