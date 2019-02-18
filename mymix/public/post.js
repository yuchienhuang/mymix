function renderStories(stories) {

    const data_json  = JSON.parse(stories);
    const storiesDiv = document.getElementById('results');
    
    
    spotify_data = data_json[0]
    azlyrics_data = data_json[1]


    for (let i = 0; i < spotify_data.length; i++){
        storiesDiv.appendChild(StoryDOMObject('/features/' + spotify_data[i]['id'],spotify_data[i]['artist_names']));
        
    }

    const otherStoriesDiv = document.getElementById('no results');    
    
    for (let i = 0; i < azlyrics_data.length; i++){
        otherStoriesDiv.appendChild(StoryDOMObject(azlyrics_data[i]['web'],azlyrics_data[i]['artist_names'],true));
        
    }
  
  }
  
  
  function StoryDOMObject(web_link,artist,newtab=false) {
    const card = document.createElement('div');
    // card.setAttribute('id', storyJSON._id);
    card.className = 'story card';
  
    const cardBody = document.createElement('div');
    cardBody.className = 'card-body';
    card.appendChild(cardBody);
  
    const creatorSpan = document.createElement('a');
    creatorSpan.className = 'story-creator card-title';
    creatorSpan.innerHTML = artist;
    creatorSpan.setAttribute('href', web_link);
    if(newtab == true){
      creatorSpan.target = "_blank"
    }
    cardBody.appendChild(creatorSpan);
  
    // const contentSpan = document.createElement('p');
    // contentSpan.className = 'story-content card-text';
    // console.log(storyJSON );
    // contentSpan.innerHTML = storyJSON.energy;
    // cardBody.appendChild(contentSpan);
  
    const cardFooter = document.createElement('div');
    cardFooter.className = 'card-footer';
    card.appendChild(cardFooter);
  
  
    return card;
  }
  
  