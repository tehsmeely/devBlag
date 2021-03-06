$(function(){

    //Preset colour input to colour value
    /*
    var preCol = $(".addForm").css("background-color");
    console.log(rgbToHex(preCol));
    $(".color").val(rgbToHex(preCol));

    //used to convert the rgb colour value to Hex
    // from http://stackoverflow.com/questions/5623838/rgb-to-hex-and-hex-to-rgb
    function componentToHex(c) {
        var hex = c.toString(16);
        return hex.length == 1 ? "0" + hex : hex;
    }
    function rgbToHex(rgbStr) { //takes "rgb(r, g, b)" gets values as str with regext, then casts to int with call to componentToHex
        var rgb = rgbStr.replace(/[^\d,]/g, '').split(',');
        return componentToHex(parseInt(rgb[0])) + componentToHex(parseInt(rgb[1])) + componentToHex(parseInt(rgb[2]));
    }
    */

    //The update button sets the background of the form to the entered colour
    $("#updateCol").click(updateColour);

    function updateColour(){
        var colour = $(".color").val();
        console.log(colour);
        //event.preventDefault();
        $(".addForm").css("background-color", "#" + colour);
        return false;
    }

    function typeInTextarea(el, newText) {
        var start = el.prop("selectionStart")
        var end = el.prop("selectionEnd")
        var text = el.val()
        var before = text.substring(0, start)
        var after  = text.substring(end, text.length)
        el.val(before + newText + after)
        el[0].selectionStart = el[0].selectionEnd = start + newText.length
        el.focus()
        return false
    }

    function updateInsertClick(){
        $(".resourceTr").on("click", function() {
            var resID = $(this).attr("resID");
            var resType = $(this).attr("resType");
            var resChar;
            if (resType == "image"){resChar = "i";}
            else if (resType == "code") {resChar = "c";}
            else { resChar = "d"; }
            typeInTextarea($(".bodyTA"), "<<"+resChar+":"+resID+">>");
            /* bodyTA is class of text area - Set in form definition for body TextField */
            return false
        })
    };

    function updateResTooltips(){
        console.log("updateResTooltips");
        $(".resourceTr").tooltip({
            content: function(){
                var resType = $(this).attr("resType")
                if (resType == "image")
                {
                    var imgStr =  "<img src='" + $(this).attr("url") + "'>";
                    console.log(imgStr);
                    return imgStr;
                } else if (resType == "code"){
                    return $(this).attr("code");
                } else {
                    return "Download Link"
                }
            }
        });
    };


    $(".markupHints").click(function(){
        $(".markupHintsText").toggle("fast");
    })


    $("input[name=fileType]").change(updateFieldDisplay);

    function updateFieldDisplay()
    {
    }

    function updateResGrid(resType){
        $("#resTableBody").empty()
                          .append("<tr><td style='text-align: center;'><i class='fa fa-cog fa-spin'></i></td></tr>")

        //"mine" or "public" -> True/False
        var resourceOwner = $("input[name=resourceOwner]:checked").val();
        var publicVal = resourceOwner=="public";
        console.log("publicVal  " + publicVal);
        $.get(
            "/getResources/",
            {"resourceType": resType, "public": publicVal},
            function(data, textStatus, jqXHR){
                console.log("Success! textStatus: " + textStatus);
                console.log(data)
                var resTable = $("#resTableBody");
                resTable.empty()
                var getTr
                if (data.RESOURCE_TYPE == "image") {
                    getTr = getImageTr;
                } else if (data.RESOURCE_TYPE == "code") {
                    getTr = getCodeTr;
                } else {
                    getTr = getDownloadTr;
                }
                if (data.RESOURCES.length>0) {
                    for (iResource in data.RESOURCES){
                        var resource = data.RESOURCES[iResource];
                        var appendLine = getTr(resource)
                        console.log(appendLine);
                        resTable.append(appendLine);
                    }
                } else {
                    resTable.append("<tr><td style='text-align: center;'>No Resources Found for this type</td></tr>")
                }
                updateInsertClick();
                updateResTooltips();
            },
            "json"
        );
    }
    function getImageTr(resource){
        return '<tr class="resourceTr" title="" resType="image" resID="' + resource.id + '" url="' +
                                     resource.imageFile_url.replace("localhost", "192.168.0.6") + '"><td class="resourceTdCaption">'
                                     + resource.caption + '</td><td class="resourceTdOwner">' + resource.owner + '</td></tr>';
    }
    function getCodeTr(resource){
        return '<tr class="resourceTr" title="" resType="code" resID="' + resource.id + '" code="'
        + resource.code + '"><td class="resourceTdCaption">' + resource.caption + '</td><td class="resourceTdOwner">' + resource.owner +'</td></tr>';
    }
    function getDownloadTr(resource){
        return '<tr class="resourceTr" title="" resType="download" resID="' + resource.id + '"><td class="resourceTdCaption">'
                                    + resource.caption+ '</td><td class="resourceTdOwner">' + resource.owner + '</td></tr>';
    }
    $("#imageButton").click(function(){
        updateResGrid("image");
        $(".resourceList").attr("resType", "image");
        $(".resourceList").css("background-color", "#fff");
        //$("#resTableBody").append("<tr><td style='text-align: center;'><i class='fa fa-cog fa-spin'></i></td></tr>")
    });
    $("#codeButton").click(function(){
        updateResGrid("code");
        $(".resourceList").attr("resType", "code");
        $(".resourceList").css("background-color", "#ddd");
        //$("#resTableBody")
    });
    $("#downloadButton").click(function(){
        updateResGrid("download");
        $(".resourceList").attr("resType", "download");
        $(".resourceList").css("background-color", "#bbb");
        //$("#resTableBody").append("<tr><td style='text-align: center;'><i class='fa fa-cog fa-spin'></i></td></tr>")
    });
    $("input[name=resourceOwner]").change(function(){
        updateResGrid($(".resourceList").attr("resType"));
    });

    //This event is triggered in addResource.js when a resource add is successful
    //$("body").on("resourceAdded", updateResGrid($(".resourceList").attr("resType")))
    $("body").on("resourceAdded", function(){
        console.log("resourceAdded - updating resGrid");
        //250ms delay for model to show up
        setTimeout(updateResGrid($(".resourceList").attr("resType")), 250);
    });

    //This function will make all text in the input lowercase
    // It is subsequently triggered on change and keydown events
    // class of input: "postTags" defined in forms
    var lowercasify = function(){
        text = $(".postTags").val();
        $('.postTags').val(text.toLowerCase());
    }
    $(".postTags").change(lowercasify);
    $(".postTags").keydown(lowercasify);
//})


    updateColour();
    updateResGrid("image");
    updateInsertClick();
})
