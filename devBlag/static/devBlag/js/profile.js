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
        var type = $(this).attr("type");
        var title = "";
        if (type == "Image")
        {
            var content =   "<div class='dialogCenter'>" +
                            "<img src='" + $(this).attr("url") + "' >" +
                            "<p class='dialogCenter'>" + $(this).attr("caption") + "</p>" + 
                            "</div>";
        }
        else if (type == "Code")
        {
            var content =   "<p class='dialogCenter'>" + $(this).attr("caption") + "</p>" +
                            "<br>" +
                            "<p>" + $(this).attr("code") + "</p>";
        }
        else if (type == "Download")
        {
            var content =   "<div class='dialogCenter'>" +
                            "<p><u>" + $(this).attr("filename") + "</u></p>" + 
                            "<p><a href='" + $(this).attr("url") + "' download><i class='fa fa-download fa-lg'></i></a></p>" +
                            "<p>" + $(this).attr("caption") + "</p>" +
                            "</div>";
            
        }
        else //Fail when views for other view buttons without types
        {
            return;
        }

        console.log(content);
        $("#dialog").html(content);
        $("#dialog").attr("title", "")
        $("#dialog").dialog("option", {
            position: {
                my: "center",
                at: "center",
                of: "#resTable_image"
            }
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
