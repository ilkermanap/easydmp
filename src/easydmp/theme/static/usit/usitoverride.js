/*! jQuery v1.11.3 | (c) 2005, 2015 jQuery Foundation, Inc. | jquery.org/license */
$( document ).ready(function() {
  //$(".uninett-color-darkBlue").css("background-color", "red");
  $('h3').each(function() {
         if ($(this).text() == "") {
                   //Do Something
                   $(this).css("border-top", "none");
                   $(this).css("display", "none");
         }
       });
});