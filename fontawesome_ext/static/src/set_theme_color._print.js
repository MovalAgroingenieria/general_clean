odoo.define('fontawesome_ext.set_theme_color_print', function(require) {
    "use strict";

    themeColorElement = document.querySelector('.theme-report-color');
    duotone_print_class = document.querySelector('.duotone-print-color');
    current_color = getComputedStyle(themeColorElement).getPropertyValue("color");
    match = /rgba?\((\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*(,\s*\d+[\.\d+]*)*\)/g.exec(current_color)
    a = 0.4;
    duotone_print_class.style.color = "rgba(" + [match[1],match[2],match[3],a].join(',') +")";


});

