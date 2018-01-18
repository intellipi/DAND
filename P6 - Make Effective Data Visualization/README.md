## Summary

After the most violent mass shooting in modern US history, kiling 58 and injuring 527 people in Las Vegas, October 2017, a lot of attention was once more drawn to the causes leading to such acts.
The aim of this graph is to shed some light on the subject, which in the past decade seem more frequent than ever.  <p>
Far from being conclusive about the causes, it's clear that such coward acts against civilians are a recent phenomenon concentrated in certain regions.  <p> 
Some aspects can be easily spotted on this map, being the most striking the magnitude of last Las Vegas shooting in relation to previous massacres nationwide. It also makes us wonder how some States have such low shooting rates being neighbor to violent States all around: Indiana to the East and New Mexico to the West are the most obvious examples. 
Of couse, some other States draw attention for the exact opposite reason: why are there so many shootings in Washington and Colorado? <p>
Feel free to [explore the map](https://bl.ocks.org/intellipi/raw/eba6ea42d28af2c4c35010e61ab86a7b/) and draw your own conclusions. 

## Design

The chosen graphic representation for the selected data is a choropleth map, where feature groups are evidenced by color.<br>
It has a clear advantage over other graphic types when location and quantity are the most important features.<br>
I also used a technique called "Martini glass" visualization, which animates the graph automatically and, at the end, 
let users interact with it and explore the way best suits them. 
<br>
The graphic representation has three main features: <br>
  <ul>
    <li>Total number of shootings per State, color filled in a light yellow to red scale;<br>
    <li>Decade when each shooting happened, represented by colors in a grey to black scale circles;<br>
    <li>Total victims (including the shooter, if commited suicide or shot by the police), represented on the graph by the circle size. 
   </ul>
<p>
In order to project these variables on a map, the [Albers Usa](https://bl.ocks.org/mbostock/5545680) projection was used, where Alaska and Hawaii are displaced for a compact visualization of the whole country.   
<p>
The color scales were chosen for being universally associated with crimes. <br>
Red was the obvious choice for the bloodiest States, but even States with low shooting rates were painted yellow (color used for warning signs). After all, no matter how rarely it happens, it's never a reason for celebration.<br>
North Dakota, New Hampshire and Rhode Island, which never experienced a single mass shooting, were left the original light grey color. <br>
Each individual shooting is represented in a grey to black scale according to the decade it happened, being black the most recent decade. The color scale was chosen for two reasons: 
 for black being associated with mourning and for better contrasting with a yellow to red background. The circle stroke (the border) was painted grey for better visualization of several recent shootings around the same location. For instance in Florida, where three small black circles are emcompassed by a larger black circle.
<p>
Color scales (buckets) were splitted using custom values. It means the decision about from which value on a certain State would be painted a certain color were based solely on my personal judgement.<br>
With few States with a high count and many with only 1, 2 or 3 cases, the automatic functions to color based on variable values were returning crazy outputs. 
 It was also virtually impossible to know which value was splitting the colors, making it very hard (and error prone) to write legend text. 
<p>
For last, the hover feature let users interact with the map by hovering the mouse over individual shooting locations, when a tooltip is presented with details about the city/county it happened and the number of both fatalities and injuries.
<p>
One last design aspect is the screen split between header, footer and main screen, where the graph was plotted. 
It immensely helps draw viewer's attention to what matters most.
  
## Feedback

[First version](https://bl.ocks.org/intellipi/raw/bcbe186b0087c799b3dd26773f623eaa/)

1. [Feedback #1](https://photos.app.goo.gl/j2w5873ECioVOUDI3)
  * Remove color from States with no shootings  
  * Remove the first 2 years from the DB, making it 50 years in total  
  * Email link under my name  

2. [Feedback #2](https://photos.app.goo.gl/AvHgyE2nV7D5tJjw2)
  * Annimation: "Martini glass" technique  

3. [Feedback #3](https://photos.app.goo.gl/FrVRtPmtn75Ph6bX2)
  * Better html layout  
  * Remove text explanantion after graph  


## Resources

Kaggle. [US Mass Shootings](https://www.kaggle.com/zusmani/us-mass-shootings-last-50-years), 2017. **Note**: original shootings data, which was cleansed for the project.<br>
Murray, S. [Interactive Data Visualization for the Web](http://chimera.labs.oreilly.com/books/1230000000345), 2013. **Note**: first map sketch was drawn using Choropleth example @ chapter 12.<br> 
Bostock, M. [D3.js](https://d3js.org). **Of course :-)** <br>
Bostock, M. [Let’s Make a Bubble Map](https://bost.ocks.org/mike/bubble-map/). **Note**: Explains how to draw the bubble size legend.
https://bost.ocks.org/mike/bubble-map/ <br>
Chandra, M. [Basic US State Map - D3](http://bl.ocks.org/michellechandra/0b2ce4923dc9b5809922), 2017. **Note**: also based on Scott Murray's book, it was unvaluable both as my first goal and for the legends, which I couldn't deal with. When my code went wrong (many times!), I returned to her to check what was done differently. Special thanks :-)<br>
[Mozilla Development Network](https://developer.mozilla.org/en-US/). **Note**: HTML, CSS and Javascript reference. <br>
[Dashing D3.js](https://www.dashingd3js.com/table-of-contents). **Note**: excellent, helpful tutorial. <br>