  // This is called with the results from from FB.getLoginStatus().
  function statusChangeCallback(response) {
    console.log('statusChangeCallback');
    console.log(response);
    // The response object is returned with a status field that lets the
    // app know the current login status of the person.
    // Full docs on the response object can be found in the documentation
    // for FB.getLoginStatus().
    if (response.status === 'connected') {
      // Logged into your app and Facebook.
      testAPI();
    } else if (response.status === 'not_authorized') {
      // The person is logged into Facebook, but not your app.
      document.getElementById('status').innerHTML = 'Please log ' +
        'into this app.';
    } else {
      // The person is not logged into Facebook, so we're not sure if
      // they are logged into this app or not.
      document.getElementById('status').innerHTML = 'Please log ' +
        'into Facebook.';
    }
  }
  // This function is called when someone finishes with the Login
  // Button.  See the onlogin handler attached to it in the sample
  // code below.
  function checkLoginState() {
    FB.getLoginStatus(function(response) {
      statusChangeCallback(response);
    });
  }
  window.fbAsyncInit = function() {
  FB.init({
    appId      : '105719696577356',
    cookie     : true,  // enable cookies to allow the server to access 
                        // the session
    xfbml      : true,  // parse social plugins on this page
    version    : 'v2.8' // use graph api version 2.8
  });
  // Now that we've initialized the JavaScript SDK, we call 
  // FB.getLoginStatus().  This function gets the state of the
  // person visiting this page and can return one of three states to
  // the callback you provide.  They can be:
  //
  // 1. Logged into your app ('connected')
  // 2. Logged into Facebook, but not your app ('not_authorized')
  // 3. Not logged into Facebook and can't tell if they are logged into
  //    your app or not.
  //
  // These three cases are handled in the callback function.
  FB.getLoginStatus(function(response) {
    statusChangeCallback(response);
  });
  };
  // Load the SDK asynchronously
  (function(d, s, id) {
    var js, fjs = d.getElementsByTagName(s)[0];
    if (d.getElementById(id)) return;
    js = d.createElement(s); js.id = id;
    js.src = "//connect.facebook.net/en_US/sdk.js";
    fjs.parentNode.insertBefore(js, fjs);
  }(document, 'script', 'facebook-jssdk'));

   var pageLikes = {
    pages: []
  };
  function getLikes(response){
   if (response.paging && response.paging.next){
       FB.api(response.paging.next, getLikes);
       for (var i = 0; i < response.data.length; i++) {
            //add all posts to the items array
            pageLikes.pages.push({ 
          "name" : response.data[i].name,
         });
        }
      }  
      else{
        callback_likes();
      }
      // console.log(pageLikes.pages);
      // return pageLikes.pages;
    }
  
    function callback_likes(){
      console.log(pageLikes.pages);
    }

  // Here we run a very simple test of the Graph API after login is
  // successful.  See statusChangeCallback() for when this call is made.
  function testAPI() {
    console.log('Welcome!  Fetching your information.... ');

  FB.api('/me?fields=id,first_name,last_name,gender,location', function(response) {
      document.getElementById('status').innerHTML =
        'Thanks for logging in, ' + response.name + '!';
      var location =response.location;
      var locResponse;
      FB.api('/' + location.id, {
              fields: 'location'
          }, function(locationResponse) {
              locResponse = locationResponse;
              loggedIn = true;
              defaultLat = locResponse.location.latitude;
              defaultLon = locResponse.location.longitude;
              displayMarkers();
              sendNotification(markers.length);
          });

      FB.api("me/likes?limit=100", getLikes);
    });
    FB.api('/me?fields=id,first_name,last_name,gender,location,hometown,email',function(response) {
      console.log('Successful login for: ' + response.name);
      console.log(response);
    });
  }

  function sendNotification(numNotifications){
    FB.api('/me', function(response) {
    var req ="/"+response.id+"/notifications";
    FB.api(req, 
       'post', 
       {
           access_token: '105719696577356|79c6db8c9fb0bc8c93c9b6b58ffb7ead',
           template: 'You have ' + numNotifications + ' events waiting to be reviewed',
           href: ''        
       }, 
       function(response)
       {
          if (!response || response.error)
          {
             alert(response.error.message);
          } 
          else 
          {
             alert('Success :D');
          }
       }
    );
  });
  }