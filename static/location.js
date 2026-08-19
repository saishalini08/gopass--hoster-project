// 1. Check if the browser supports Geolocation
if ("geolocation" in navigator) {
  // 2. Ask for the user's location
  // This triggers the "Allow Location" popup in the browser
  navigator.geolocation.getCurrentPosition(
    successCallback, 
    errorCallback, 
    {
      enableHighAccuracy: true, // Asks the device to use GPS if available (slower but more accurate)
      timeout: 10000,           // Give up if it takes more than 10 seconds
      maximumAge: 0             // Force a fresh location, don't use a cached one
    }
  );
} else {
  alert("Geolocation is not supported by your browser.");
}

// 3. What to do if the user clicks "Allow"
function successCallback(position) {
  // Extract latitude and longitude from the position object
  const userLat = position.coords.latitude;
  const userLon = position.coords.longitude;
  

  // Add this line to pop up your real coordinates!
    alert("My real coordinates are: " + userLat + ", " + userLon);
  
  // The location of the target (e.g., the specific desk or building)
  const targetLat = 12.7987861; // Example latitude (Kanchipuram area)
  const targetLon = 79.8619084; // Example longitude

  console.log("Your Location:", userLat, userLon);

  // 4. Send the coordinates to your Python Flask backend
  sendToBackend(userLat, userLon, targetLat, targetLon);
}

// 5. What to do if the user clicks "Block" or an error occurs
function errorCallback(error) {
  switch(error.code) {
    case error.PERMISSION_DENIED:
      alert("You denied the request for Geolocation. We cannot verify your location.");
      break;
    case error.POSITION_UNAVAILABLE:
      alert("Location information is unavailable.");
      break;
    case error.TIMEOUT:
      alert("The request to get user location timed out.");
      break;
    case error.UNKNOWN_ERROR:
      alert("An unknown error occurred.");
      break;
  }
}

// 6. The function to send data to your Flask server
function sendToBackend(userLat, userLon, targetLat, targetLon) {
  // This uses the standard Fetch API to make a POST request
  fetch('/book_ticket', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      user_lat: userLat,
      user_lon: userLon,
      target_lat: targetLat,
      target_lon: targetLon
    })
  })
  .then(response => response.json())
  .then(data => {

    
                
      // Get the current time (e.g., 10:45:02 AM)
      const timeNow = new Date().toLocaleTimeString();
    // Handle the response from your Python code (success or failed)
    if (data.status === "success") {
        alert("Success: " + data.message);
    } else {
        alert("Blocked: " + data.reason);
    }
    console.log("Server Response:", data);
  })
  .catch((error) => {
    console.error('Error connecting to backend:', error);
  });
}