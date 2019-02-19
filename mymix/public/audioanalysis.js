$(function() {
    $('a#test').bind('click', function() {
      
      const plotDiv = document.getElementById('plot');

      while (plotDiv.firstChild) {
        plotDiv.removeChild(plotDiv.firstChild);
      }
      
     
        plotDiv.innerText = "generating the results...";

        $.get('/background_process_test',
            function(string) {
              while (plotDiv.firstChild) {
                plotDiv.removeChild(plotDiv.firstChild);
              }     
            if(string=="success") {
              plotDiv.appendChild( imageItem("/public/generated_plots/plot1.png"));
              plotDiv.appendChild( imageItem("/public/generated_plots/plot2.png"));
              plotDiv.appendChild( imageItem("/public/generated_plots/optimal_path.png"));
            }else{plotDiv.innerText = "Please upload TWO files!";}
              
        });
     
      return false;
    });
  });

function imageItem(src) {

  

  const item = document.createElement('IMG');
  item.setAttribute("src", src)
  
  item.setAttribute('width', '900px');
  

  const itemDiv = document.createElement('div');
  
  itemDiv.appendChild(item);

  
  return itemDiv
}