$(function(){
	$('[data-toggle="tooltip"]').tooltip();

	$(".task-list tbody tr").on("click",function(){
		window.location.href = '/Content?TaskId='+$(this).data("task");
	});
})