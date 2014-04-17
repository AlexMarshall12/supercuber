supercuber
==========

It is probably best to visit this website at www.supercuber.net and see what I am trying to explain before you read this.

Now that you have seen it, this is a website built on the pyramid-python framework. It takes stl formatted file uploads and uses them to create standalone manipulatable 3d models based on the vertex values and orderings given in the file. It can handle binary or ASCII stl files.  

This process uses three javascript libaries: thingiview.js, three.js, and plane.js. Three.js allows 3d objects such as these models to be displayed and maniuplated in a web browser. Plane.js sets up the grey 3d environment upon which the 3d model is placed. thingiview.js is what actually creates the 3d model in the space provided.

Usually, thingiview.js runs entirely client-side. The verticies and orderings are parsed in the clients browser and displayed on it. However, supercuber does this all on the server. The verticies and orderings are put into an array and passed onto the server which saves them into an appropriately formated static html file which is stored in an amazon s3 bucket. This file can be called at any time and the model will load and be viewable in the browser window. This means that once created, you can share stl files and access them forever. You can show your friends an stl file you made and they will be able to see it in their browser without knowing anything about thingiview.js, plane.js, etc. Additionally, you can embed these standalone stl files in your blog or website so that visitors can see them as long as their browser is WebGL enabled.   
