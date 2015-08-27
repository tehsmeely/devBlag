$(function(){


    $(".projectView").click(function(){
        var projectID = $(this).parent().attr("projectID");
        window.location = "/project/" + projectID;
    });
    $(".projectDelete").click(function(){
        var conf = confirm("Are you sure you want to delete this project?\nNote: This will delete ALL posts in it");
        if (conf == true)
        {
            var projectID = $(this).parent().attr("projectID");
            $.get(
                "/deleteProject/",
                {"projectID": projectID},
                function(){
                    location.reload(true);
                })
        }
    });

    $(".postHeader").click(function(){
        window.location = "/post/" + $(this).attr("postID");
    });

    $("#newProjectButton").button({
        icons:{ primary: "ui-icon-plusthick" }
    });


    $("#dialog").dialog({
        autoOpen: false,
        resizable: false,
        width: "auto"
    });
    $(".infoViewBox").on("click", function(e) {
        e.preventDefault();
        var type = $(this).attr("type")
        if (type == "Image")
        {
            var content = "<img src='" + $(this).attr("url") + "' >";
        }
        else if (type == "Code")
        {
            var content = "<p>" + $(this).attr("code") + "</p>";
        }
        else if (type == "Download")
        {
            var content = "<a href='" + $(this).attr("url") + "'>Download</a>";
        }
        else //Fail when views for other view buttons without types
        {
            return;
        }

        console.log(content);
        $("#dialog").html(content);
        $("#dialog").attr("Title", "")
        $("#dialog").dialog("option", "position", {
            my: "center",
            at: "center",
            of: "#resTable_image"
        });
        if ($("#dialog").dialog("isOpen") == false) {
            $("#dialog").dialog("open");
        }
    });

    $(".resDeleteBox").click(function(){
        var resID = $(this).parent().attr("resourceID");
        var resType = $(this).parent().attr("resourceType");

        var conf = confirm("Are you sure you want to delete this resource?\n(It'll be gone for good!)\n\nPosts with this resource will show blank space in its stead" +
            "\n\n" + resID + " " + resType);
        if (conf == true)
        {
            //var projectID = $(this).parent().attr("projectID");
            $.ajax({
                url: "/deleteResource/",
                type: "GET",
                data: {
                    "resourceID": resID,
                    "resourceType" : resType
                },
                success: function(){
                    location.reload(true);
                },
                error: function(data){
                    //console.log(data)
                    alert("Cannot delete this as it is " + data.responseJSON.REASON +"\n");
                }

            })
        }

    });

    $(".postHeader").each(function(){
        $(this).css("background-color", $(this).attr("background-color"));
    });

})
