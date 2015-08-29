$(function(){

    var csrftoken = $.cookie('csrftoken');

    function csrfSafeMethod(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }



    $("#imageForm,#codeForm,#downloadForm").each(function(){
        $(this).submit(function(event){
            console.log("Submitting image");
            var options = {
                beforeSend: function(xhr, settings) {
                    console.log("csrfSafeMethod: " + csrfSafeMethod(settings.type));
                    console.log("this.crossDomain: " + this.crossDomain);
                    if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                        xhr.setRequestHeader("X-CSRFToken", csrftoken);
                    }
                },
                dataType: "json",
                clearForm: true,        // clear all form fields after successful submit
                //beforeSubmit - might be what is needed for CSRF.
                success: function(responseJSON, statusText, xhr, jQwFE){
                    console.log("submit success!" + responseJSON)
                    console.log(responseJSON.resourceCreated)
                }
            };
            $(this).ajaxSubmit(options);
            return false;
        })
    });


    var dialog_image = $( "#dialog-form-image" ).dialog({
        autoOpen: false,
        height: "auto",
        width: "auto",
        modal: true,
        buttons: {
        "Add Resource": function(){
            console.log("Add Resource Button clicked");
            $('#imageForm').submit();
        },
        Cancel: function() {
            $( "#dialog-form-image" ).dialog("close");
            }
        },
        title: "Image"
    });
    var dialog_code = $( "#dialog-form-code" ).dialog({
        autoOpen: false,
        height: "auto",
        width: "auto",
        modal: true,
        buttons: {
        "Add Resource": function(){
            console.log("Add Resource Button clicked");
            $('#codeForm').submit();
        },
        Cancel: function() {
            $( "#dialog-form-code" ).dialog("close");
            }
        },
        title: "Code"
    });
    var dialog_download = $( "#dialog-form-download" ).dialog({
        autoOpen: false,
        height: "auto",
        width: "auto",
        modal: true,
        buttons: {
        "Add Resource": function(){
            console.log("Add Resource Button clicked");
            $('#downloadForm').submit();
        },
        Cancel: function() {
            $( "#dialog-form-download" ).dialog("close");
            }
        },
        title: "Download"
    });
    $( "#addImage" ).click(function() {
        dialog_image.dialog("open");
    });
    $( "#addCode" ).click(function() {
        dialog_code.dialog("open");
    });
    $( "#addDownload" ).click(function() {
        dialog_download.dialog("open");
    });

});
