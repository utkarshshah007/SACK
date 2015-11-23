$(function(){
	$('#movie1').slider();
	$('#movie2').slider();

	$("#submitButton").click(function(){
	console.log("Button Clicked")
	var value = $('#movie1').slider('getValue');
    var value2 = $('#movie2').slider('getValue');

	outdata = {};
	outdata['movie1'] = value;
	outdata['movie2'] = value2;

    $.post("setup-rating", 	outdata, function (data) {
    	window.location.href = data;
    });
});
});

