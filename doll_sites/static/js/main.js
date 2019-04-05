/**/

/**/


window.onload = function(){

  document.getElementById("button-demo").addEventListener("click", getUserInfo);


  function getUserInfo() {
    const xhr = new XMLHttpRequest();

    xhr.open('GET', '/get_user_info', true);

    xhr.onload = function () {
      if (this.status === 200) {
        const userInfo = JSON.parse(this.responseText);

        console.log(userInfo);


      }
    }

    xhr.send();


  }

};

//

// -- scroll to top


$(document).ready(function() {
  $(window).scroll(function() {
    if ($(this).scrollTop() > 100) {
      $("#scroll").fadeIn();
    } else {
      $("#scroll").fadeOut();
    }
  });
  $("#scroll").click(function() {
    $("html, body").animate({ scrollTop: 0 }, 600);
    return false;
  });
});

// -- copy right year

$("#year").text(new Date().getFullYear());

// -- lazyload
$(document).ready(function() {
  $("img.lazyloadx").lazyload({
    threshold: 100,
    effect: "fadeIn",
    failure_limit: 3000
  });
});

$(".carousel").Carousel({
  interval: 3000,
  keyboard: true,
  pause: "hover"
});

$("#slider").on("slide.bs.carousel", function() {
  console.log("slide!");
});

$("#slider").on("slid.bs.carousel", function() {
  console.log("slid!");
});



  //video.js setup
  // videojs(document.querySelector('.video-js'));
  // videojs('.video-js', {
  //   controls: true,
  //   autoplay: true,
  //   preload: 'auto'
  // });

  

