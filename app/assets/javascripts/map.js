var map;
var markers = [];
function initMap() {
  map = new google.maps.Map(document.getElementById('map'), {
    center: {lat: 30.2672, lng: -97.7431},
    zoom: 8
  });

  infoWindow = new google.maps.InfoWindow({maxWidth: 300});

  // Event that closes the InfoWindow with a click on the map
  google.maps.event.addListener(map, 'click', function() {
      infoWindow.close();
  });

  if(loggedIn == true) {
    displayMarkers();
  }
}

function displayMarkers() {
	var i;

  for(i=0;i<markers.length;i++) {
    markers[i].setMap(null);
  }

  map.setCenter({lat: parseFloat(defaultLat), lng: parseFloat(defaultLon)});

  var bounds = new google.maps.LatLngBounds();
	for(i=0;i<eventData.length;i++) {
		var item = eventData[i];
		if(item.venue != null && isDistanceGood(item)) {
			createMarker(
         item.category,
         item.name,
         item.venue.name,
         item.venue.address.localized_address_display,
         item.start.utc, item.url, item.venue.latitude,
         item.venue.longitude );
      bounds.extend({lat: parseFloat(item.venue.latitude), lng: parseFloat(item.venue.longitude)});
		}
	}
  map.fitBounds(bounds);
}

function createMarker(category, name, venueName, venueAddress, startDate, url, latitude, longitude) {
	var contentString = '<div class="panel panel-primary" style="border-radius:4px;border-width:4px">' +
	        	'<div class="panel-title" style="background-color: #051838;color:white;padding:2px 6px">'+category+'</div>'+
	            '<div class="panel-body">'+
			    	'<p><b>Name:</b>'+ name + '</p>'+
			    	'<p><b>Venue:</b>' + venueName + ',' + venueAddress + '</p>'+
			    	'<p><b>Date:</b>' + startDate + '</p>'+
			    	'<p>'+
			    		'<a href="' + url + '" target="_blank">Web Link</a>'+
			    	'</p>'+
		    	'</div>'+
		    '</div>';


  var uluru = {lat: parseFloat(latitude), lng: parseFloat(longitude)};
  var marker = new google.maps.Marker({
    position: uluru,
    map: map,
    title: name
  });


  marker.addListener('click', function() {
    infoWindow.setContent(contentString);
    infoWindow.open(map, marker);
  });

  markers.push(marker);
}