$(function(){

    $("#publishButton").click(function(){
        $.get(
            "/publishPost/",
            {"postID": $(this).attr("postID")},
            function(){
                window.location = "/project/{{post.project.id}}/";
            }
        )
    });



    $("#editPostButton").click(function(){
        var projectID = $(this).attr("projectID");
        var postID = $(this).attr("postID");
        window.location = "/addPost/" + projectID + "/" + postID + "/";
    });

    $("#deletePostButton").click(function(){
        var postID = $(this).attr("postID");
        var projectID = $(this).attr("projectID");
        var conf = confirm("Are you sure you wish to delete this post?")
        if (conf==true)
        {
            $.get(
            "/deletePost/",
            {"postID": postID},
            function(){
                window.location = "/project/" + projectID + "/";
            }
            )
        }
    });

    $("#publishButton").button({
        icons:{ primary: "ui-icon-check" }
    })

    $("#deleteButton").button({
        icons:{ primary: "ui-icon-trash" }
    })

    $(".projectLinkBox").click(function(){
        window.location = "/project/" + $(this).attr("projectID") + "/";
    })

});
