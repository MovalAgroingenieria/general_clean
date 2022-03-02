odoo.define('website_blog_sharing_links.website_blog', function (require) {
    'use strict';
    var core = require('web.core');

    const dom = require('web.dom');
    const publicWidget = require('web.public.widget');
    publicWidget.registry.websiteBlog.include({
        /**
         * @override
         * @private
         * @param {Event} ev
         */
         _onShareArticle: function (ev) {
            ev.preventDefault();
            var url = '';
            var $element = $(ev.currentTarget);
            var blogPostTitle = '';
            var articleURL = '';
            if ($element.is('*[class*="blog_share_list"]')) {
                var article = $element.parents().find('.o_wblog_post');
                var articleRef = article.children('a').attr('href')
                blogPostTitle = encodeURIComponent(article.find('.o_blog_post_title').html() || '');
                articleURL = encodeURIComponent(window.location.host + articleRef);
            } else {
                blogPostTitle = encodeURIComponent($('#o_wblog_post_name').html() || '');
                articleURL = encodeURIComponent(window.location.href);
            }
            if ($element.hasClass('o_twitter')) {
                var twitterText = core._t("Amazing blog article: %s! Check it live: %s");
                var tweetText = _.string.sprintf(twitterText, blogPostTitle, articleURL);
                url = 'https://twitter.com/intent/tweet?tw_p=tweetbutton&text=' + tweetText;
            } else if ($element.hasClass('o_facebook')) {
                url = 'https://www.facebook.com/sharer/sharer.php?u=' + articleURL;
            } else if ($element.hasClass('o_linkedin')) {
                url = 'https://www.linkedin.com/sharing/share-offsite/?url=' + articleURL;
            }
            window.open(url, '', 'menubar=no, width=500, height=400');
        },
    });
});
