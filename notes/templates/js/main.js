$(function(){
	$('[data-toggle="tooltip"]').tooltip();
	
	$(".nav-link").on("click",function(){
		$(".nav-link").removeClass("active");
		$(this).addClass("active");
		$(".card-body:not(.Comment)").hide();
		$(".card-body" + "#"+$(this).prop("id")).show();
	});
})