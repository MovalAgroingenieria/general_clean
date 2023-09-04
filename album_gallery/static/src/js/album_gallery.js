odoo.define('album_gallery.album_gallery', function (require) {
    'use strict';

    var publicWidget = require('web.public.widget');

    publicWidget.registry.AlbumGallery = publicWidget.Widget.extend({
        selector: '.lightgallery',
        hideInterfaceTimer: false,
        hideInterface: function () {
            document.querySelectorAll('.lg-toolbar').forEach(x => x.style.opacity = '0')
            document.querySelectorAll('.lg-thumb-outer').forEach(x => x.style.opacity = '0')
        },
        showInterface: function () {
            document.querySelectorAll('.lg-toolbar').forEach(x => x.style.opacity = '1')
            document.querySelectorAll('.lg-thumb-outer').forEach(x => x.style.opacity = '1')
        },
        resetTimer: function () {
            clearTimeout(this.hideInterfaceTimer);
            this.showInterface();
            this.hideInterfaceTimer = setTimeout(this.hideInterface, 6000);
        },
        start: function () {
            if (this.$el.length) {
                var lgOptions = {
                    plugins: [lgThumbnail, lgVideo, lgZoom, lgFullscreen, lgAutoplay],
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
            // Reset timer for hiding the interface
            this.resetTimer();
            // When the mouse is moved, the timer is reset
            document.addEventListener('mousemove', this.resetTimer.bind(this));
            // document.addEventListener('keydown', this.resetTimer.bind(this)); //Add this to reactivate using keys
            // Close all galleries functionality
            var closeButton = document.getElementById('close-all-galleries');
            closeButton.addEventListener('click', function () {
                var galleryContainers = document.querySelectorAll('.lightgallery-container');
                galleryContainers.forEach(function (galleryContainer) {
                    galleryContainer.style.display = 'none';
                });
                var openGalleries = document.querySelectorAll('.toggle-gallery-checkbox:checked');
                openGalleries.forEach(function (galleryCheckbox) {
                    galleryCheckbox.checked = false;
                    var arrowLabel = galleryCheckbox.closest('.gallery-toggle-container').querySelector('.toggle-gallery-label');
                    arrowLabel.classList.remove('rotated');
                });
            });
            // Select all toggle checkboxes
            var toggleCheckboxes = document.querySelectorAll('.toggle-gallery-checkbox');
            toggleCheckboxes.forEach(function (checkbox) {
                checkbox.addEventListener('change', function () {
                    var galleryContainer = checkbox.closest('.gallery-toggle-container').querySelector('.lightgallery-container');
                    var arrowLabel = checkbox.closest('.gallery-toggle-container').querySelector('.toggle-gallery-label');
                    if (checkbox.checked) {
                        galleryContainer.style.display = 'block';
                        arrowLabel.classList.add('rotated');
                    } else {
                        galleryContainer.style.display = 'none';
                        arrowLabel.classList.remove('rotated');
                    }
                });
            });
            // Enable clicking on whole album title
            var divs = document.querySelectorAll('.gallery-toggle-container > div');
            var divs = document.querySelectorAll('.gallery-toggle-container > div');
            divs.forEach(function (div, index) {
                console.log("Attaching event listener to div index", index);
                div.addEventListener('click', function (e) {
                    console.log("Event triggered on: ", e.target);
                    e.stopImmediatePropagation();
                    if (e.target.tagName.toLowerCase() !== 'label') {
                        var targetId = div.getAttribute('data-target');
                        var checkbox = document.getElementById(targetId);
                        if (checkbox) {
                            console.log("Checkbox current state: ", checkbox.checked);
                            checkbox.checked = !checkbox.checked;
                            var event = new Event('change', {
                                'bubbles': true,
                                'cancelable': true
                            });
                            checkbox.dispatchEvent(event);
                        }
                    }
                });
            });
        },
    });
});
