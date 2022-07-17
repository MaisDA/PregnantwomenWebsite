function submitForms(){
    setTimeout(function(){document.getElementById("form1").submit();},1000);
    setTimeout(function(){document.getElementById("form2").submit();},10000);
}

$('#form1').submit(doubleSubmit);

function doubleSubmit(e1) {
    e1.preventDefault();
    e1.stopPropagation();
    var post_form1 = $.post($(this).action, $(this).serialize());

    post_form1.done(function(result) {
            // would be nice to show some feedback about the first result here
            $('#form2').submit();
        });
};