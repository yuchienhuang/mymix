// client-side js
// run by the browser each time your view template is loaded

// by default, you've got jQuery,
// add other scripts at the bottom of index.html


$(function() {  
  $('form').submit(function(event) {
    event.preventDefault();
    
    let song = $('input[name="song"').val();
    let artist = $('input[name="artist"]').val();
    
    $.get('/search?' + $.param({song: song, artist: artist}), function(string) {
      $('input[type="text"]').val('');
      $('input').focus();
      
      if(string==""){

        location.reload();

        

       }else {

        const spotifyDiv = document.getElementById('results');
        spotifyDiv.innerHTML = "";

        const azlyricsDiv = document.getElementById('no results');
        azlyricsDiv.innerHTML = string;
      }
       
       
      //else if(string=="no results found"){

      //   const spotifyDiv = document.getElementById('results');
      //   spotifyDiv.innerHTML = string;

      //   const azlyricsDiv = document.getElementById('no results');
      //   azlyricsDiv.innerHTML = string;
      // }else{
      //   // location.reload();
      //   const spotifyDiv = document.getElementById('results');
      //   spotifyDiv.innerText = string;
        

        

      // }

      
      // const data_json  = JSON.parse(data);
      

      // const storiesDiv = document.getElementById('results');
      

      // for (var key in data_json) {
      //   storiesDiv.appendChild(storyDOMObject(key,data_json[key]));
      // }
      
      
      //const data_json  = JSON.parse(data);
      
      
      // const spotify_versions = data_json[0];
      // const no_spotify_versions = data_json[1];
      
      
      // sessionStorage.clear();
      // for (var key in spotify_versions) {
      //   sessionStorage.setItem(key, spotify_versions[key]);
      // };

      
      // renderStories(stories);
      
      
      // const otherVersionsDiv = document.getElementById('no results');
      
      // console.log('no_spotify_versions');
      // console.log(data);
      // otherVersionsDiv.innerHTML = data;

      
      // for (let i = 0; i < Object.keys(data_json).length; i++) {
      //   const currentStory = storiesArr[i];
      //   storiesDiv.prepend(storyDOMObject(currentStory, user));
      // }

      //storiesDiv.appendChild(storyDOMObject(data_json[0]));
        

      })
    });
  });
