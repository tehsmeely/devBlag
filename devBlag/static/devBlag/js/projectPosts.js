$AJAX_POST_GET_URL = "/ajaxRouting/getPosts/";
$(function(){
    $('pre code').each(function(i, block) {
        hljs.highlightBlock(block);
    });

    $("#sortDirectionButton").click(function(){
        if ($(this).attr("state") == "of")
        {
            $(this).attr("state", "nf")
        } else {
            $(this).attr("state", "of")
        }
        $(this).toggleClass("fa-caret-up fa-caret-down");
        getPostJSON();
    })

    $("#filterButton").click(getPostJSON);
    $("#orderCriterion").change(getPostJSON);


    function getPostJSON()
    {
        var getCriteria = getFilterCriteria();
        getCriteria.projectID = $(".filterBar").attr("projectID");
        console.log(getCriteria);
        $.get(
            $AJAX_POST_GET_URL,
            getCriteria,
            function(data, textStatus, jqXHR ){
                console.log(data);
                var postCont = $("#postContainer");
                postCont.empty();
                if (data.POSTS.length>0) {
                    for (iPost in data.POSTS){
                        if (iPost%2 === 0) { var cornerClass = "round7_tr_bl"; }
                        else { var cornerClass = "round7_tl_br"; }
                        var post = data.POSTS[iPost];
                        postCont.append(generatePostDiv(post, cornerClass));
                    }
                }
            }
        )
    }

    function getFilterCriteria()
    {
        var orderCriterion = $("#orderCriterion").val();
        var tagFilterInput = $("#tagFilterInput").val();
        var orderDirection = $("#sortDirectionButton").attr("state");
        return {"orderCriterion": orderCriterion,
        "tagFilterInput": tagFilterInput,
        "orderDirection": orderDirection};
    }

    function generatePostDiv(post, cornerClass)
    {
        //linebreak regex from:
        //http://stackoverflow.com/questions/784539/how-do-i-replace-all-line-breaks-in-a-string-with-br-tags
        var divStr = "" +
        '<div class="post ' + cornerClass +
        '" style="background-color:#' +post.backgroundColour + '">' +
            "<div class='postControlButton' postID='" + post.id + "'>" +
                "<i class='fa fa-eye postViewButton'></i></i>" +
            "</div>" +
            '<h3>' + post.title + '</h3>' +
            post.body.replace(/(?:\r\n|\r|\n)/g, '<br />') +
            '<br>' +
            '<div class="postInfoBar">' +
                '<div class="postInfoDates">' +
                    '<p>Published: ' + post.publishedDate + '</p>' +
                '</div>' +
                '<div class="postInfoTags">' +
                    post.postTags +
                '</div>' +
            '</div>' +
        '</div>' +
        '<br>';
        return divStr;
    }

    $(".postViewButton").click(function(){
        var postID = $(this).parent().attr("postID");
        window.location = "/post/" + postID + "/";
    })

    //This function will make all text in the input lowercase
    // It is subsequently triggered on change and keydown events
    // id of input: "postTags" defined in html template
    var lowercasify = function(){
        text = $("#tagFilterInput").val();
        $('#tagFilterInput').val(text.toLowerCase());
    }
    $("#tagFilterInput").change(lowercasify);
    $("#tagFilterInput").keydown(lowercasify);
})
