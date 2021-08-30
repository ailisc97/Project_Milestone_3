$(document).ready(function(){
    // JS to make the navigation items expand out from the right side on smaller devices where it is collapsed.
    $('.sidenav').sidenav({edge: "right"});
    // Select options
    $('select').formSelect();
    // Collapsible events
    $('.collapsible').collapsible();
    // Modal initialiser
    $('.modal').modal();
    

    // Function to validate materialize form select elements and add different CSS depending on valid or invalid entry
    validateMaterializeSelect();
    function validateMaterializeSelect() {
        // Variable containing CSS for valid option
        let classValid = { "border-bottom": "1px solid #4caf50", "box-shadow": "0 1px 0 0 #4caf50" };
        // Variable containing CSS for invalid option
        let classInvalid = { "border-bottom": "1px solid #f44336", "box-shadow": "0 1px 0 0 #f44336" };
        if ($("select.validate").prop("required")) {
            $("select.validate").css({ "display": "block", "height": "0", "padding": "0", "width": "0", "position": "absolute" });
        }
        $(".select-wrapper input.select-dropdown").on("focusin", function () {
            $(this).parent(".select-wrapper").on("change", function () {
                // If list item is select that is not disabled ("Choose Option" Default value is) then add isValid CSS 
                if ($(this).children("ul").children("li.selected:not(.disabled)").on("click", function () { })) {
                    $(this).children("input").css(classValid);
                }
            });
        }).on("click", function () {
            if ($(this).parent(".select-wrapper").children("ul").children("li.selected:not(.disabled)").css("background-color") === "rgba(0, 0, 0, 0.03)") {
                $(this).parent(".select-wrapper").children("input").css(classValid);
            } else {
                // Else add invalid CSS if above conditions not satisfied as valid entry
                $(".select-wrapper input.select-dropdown").on("focusout", function () {
                    if ($(this).parent(".select-wrapper").children("select").prop("required")) {
                        if ($(this).css("border-bottom") != "1px solid rgb(76, 175, 80)") {
                            $(this).parent(".select-wrapper").children("input").css(classInvalid);
                        }
                    }
                });
            }
        });
    }
});