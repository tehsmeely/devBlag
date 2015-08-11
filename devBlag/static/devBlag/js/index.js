$(function(){

    //Tooltips for projects
    //
    $(".projLink").tooltip({
        content: function(){
            //collect info
            var title = $(this).attr("title");
            var inProgress = $(this).attr("inProgress");
            var engine = $(this).attr("engine");
            var language = $(this).attr("language");
            //Convert inProgress boolean to text inDev
            if (inProgress == "True") {
                var inDev = "In Progress";
            } else {
                var inDev = "Completed";
            }
            /*
            var output = 	"<p>"+title+"</p>"+
                            "<p>"+inDev+"</p>"+
                            "<p>E: "+engine+"</p>"+
                            "<p>L: "+language+"</p>";
            */
            var output = 	title+"<br>"+
                            inDev+"<br>"+
                            (engine == "" ? "" : "E: "+engine+"<br>")+
                            (language == "" ? "" : "L: "+language+"<br>");
            return output;
        }
    });

    //Tooltips for developers
    //
    $(".devLink").tooltip({
        content: function(){
            //collect info
            var name = $(this).attr("name");
            var output = name;
            return output;
        }
    });

})
