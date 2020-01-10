$(function(){

	$("[name=compDate]").datepicker();
	$("[name=workDate]").datepicker();

	$(".nav-link").on("click",function(){
		$(".nav-link").removeClass("active");
		$(this).addClass("active");
		$(".card-body:not(.Comment)").hide();
		$(".card-body" + "#"+$(this).prop("id")).show();
	});
	$("[name=status]").val($("[name=selectedStatus]").val())
	$('[data-toggle="tooltip"]').tooltip();
})