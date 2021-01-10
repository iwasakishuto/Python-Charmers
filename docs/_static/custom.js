(function (){

  $(function(){
    $("dl.py.method dt:has(em.property)").addClass("dt-property");
  });

  $(function(){

    var items = document.querySelectorAll('div.sphinxsidebarwrapper li[class*="toctree-"]');
    items.forEach((item) => {
      var text  = item.querySelector("a").innerHTML
      var text_components = text.split(".");
      var num_components = text_components.length;
      if (num_components>0){
        text = text_components[num_components-1];
      }
      text = text.replace(/\spackage/g,' <span class="package-name">package</span>')
                .replace(/(.*)\smodule/g, '<span class="program-name">$1.py</span>')
                .replace(/(Subpackages|Submodules)/g,'<span class="package-subtitle">$1</span>');
      item.querySelector("a").innerHTML = text
    });

  });
})(jQuery);

