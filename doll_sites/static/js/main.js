/**/

/**/
// -- scroll to top

$(document).ready(function(){ 
  $(window).scroll(function(){ 
    if ($(this).scrollTop() > 100) { 
        $('#scroll').fadeIn(); 
    } else { 
        $('#scroll').fadeOut(); 
    } 
  }); 
  $('#scroll').click(function(){ 
    $("html, body").animate({ scrollTop: 0 }, 600); 
    return false; 
  }); 
  });


// -- copy right year

$('#year').text(new Date().getFullYear());

// -- lazyload
$(document).ready(function(){
  $('img.lazyloadx').lazyload({
      threshold : 200,
      effect : 'fadeIn',
      failure_limit : 10,
  })
})







