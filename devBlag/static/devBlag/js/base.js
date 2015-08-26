$(function(){

    // Edit the contents of a sibling span when a class "editButton" is present
    // To be used with FontAwesome, fa-pencil and fa-check
    // Spans to be edited must include the followingf attributes
    //	route: the routing for the get url: /ajaxRouting/<route>/
    //  method: the method to act on the value of the span - in the view
    //  blankVal: the value to display is span is blank: e.g. "(blank)"
    $AJAX_URL_EDIT = "/ajaxRouting/";
    $(".editbutton").click(function(){
        var state = $(this).attr("state");
        var parent = $(this).parent();
        var span = $("span", parent);


        if (state == "0") //Edit state
        {

            var original = span.attr("actualVal");
            $(this).switchClass("fa-pencil", "fa-check");
            span.empty();
            span.append("<input type='text' value='" + original + "'>");
            $(this).attr("state", "1");

        } else { //confirm state

            //get value, store that in "actualVal".
            //convert to blank message if blank when
            //displaying in span

            var newVal = $("input", span).val();
            var editButton = $(this);
            var method = span.attr("method");
            var route = span.attr("route");
            console.log(newVal);



            //AJAX
            var ajaxURL = $AJAX_URL_EDIT + route + "/";
            $.get(ajaxURL, {"method" : method,"newVal": newVal}, function(data){
                if (newVal == ""){
                    //var spanVal = "(blank - displays as full name)";
                    var spanVal = span.attr("blankVal");
                } else {
                    var spanVal = newVal;
                }
                span.html(spanVal);
                span.attr("actualVal", newVal);
                editButton.switchClass("fa-check", "fa-pencil");
                editButton.attr("state", "0");
            });
        }
    })

    //All post class divs have background-color set to their backgounr-color attribute
    $(".post").each(function(){
        console.log($(this).attr("background-color"))
        $(this).css("background-color", $(this).attr("background-color"))
    })

})
