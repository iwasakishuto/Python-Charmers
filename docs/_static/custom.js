(function (){

  $(function(){
    $("dl.py.method dt:has(em.property)").addClass("dt-property");
  });

  var items = document.querySelectorAll('li[class*="toctree-"]');
  items.forEach((item) => {
    var text  = item.querySelector("a").innerHTML
    var text_components = text.split(".");
    var num_components = text_components.length;
    if (num_components>0){
      text = text_components[num_components-1];
    }
    text = text.replace(/\spackage/g,' <span style="color:greenyellow">package</span>')
               .replace(/\smodule/g,'<span style="color:aqua">.py</span>')
               .replace(/Subpackages/g,'<span style="color:white;text-decoration: underline;">Subpackages</span>')
               .replace(/Submodules/g,'<span style="color:white:text-decoration: underline;">Submodules</span>');
    item.querySelector("a").innerHTML = text
  });
})(jQuery);