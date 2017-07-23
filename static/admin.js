$(document).ready(function() {
	$("#continueButton").click(function(event){
		$("#importForm").prepend('<input type="hidden" name="' + event.target.name + '" value="true">').submit();
	});
	$("#replaceExistingButton").click(function(event) {
		$("#replaceAlert").removeClass("hidden");
		event.preventDefault();
	});
});
