odoo.define('album_gallery.album_gallery', function (require) {
    'use strict';

    var publicWidget = require('web.public.widget');

    publicWidget.registry.AlbumGallery = publicWidget.Widget.extend({
        selector: '.lightgallery',
        start: function () {
            if (this.$el.length) {
                var lgOptions = {
                    plugins: [lgThumbnail, lgVideo, lgShare, lgZoom, lgFullscreen, lgAutoplay],
                    thumbnail: true,
                    videojs: true,
                    showThumbByDefault: false,
                    autoplayFirstVideo: true,
                    appendThumbnailsTo: '.lg-outer',
                    closable: true,
                    download: false,
                    fullscreen: true,
                    showZoomInOutIcons: true,
                    actualSize: false,
                    share: true,
                    googlePlus: false,
                };
                window.lightGallery(this.el, lgOptions);
            }
            return this._super.apply(this, arguments);
        },
    });
});
