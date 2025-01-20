# -*- coding: utf-8 -*-
# 2024 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import json
from odoo import http
from odoo.http import request


class OmaAppBlogController(http.Controller):

    @http.route('/api/news', type='http',
                auth='public', methods=['GET'], csrf=False)
    def get_blog_news_list(self, **kwargs):
        base_web_url = \
            request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        page = int(kwargs.get('page', 1))
        limit = int(kwargs.get('limit', 10))
        offset = (page - 1) * limit
        domain = [('active', '=', True), ('website_published', '=', True)]
        blog_posts = request.env['blog.post'].sudo().search(
            domain, offset=offset, limit=limit)
        data = []
        for post in blog_posts:
            url_image = base_web_url + \
                json.loads(post.cover_properties)['background-image']\
                .replace('url(', '').replace(')', '')
            data.append({
                "id": int(post.id),
                "title": post.name,
                "subtitle": post.subtitle or "",
                "publish_date": post.published_date,
                "url_image": url_image,
                "url_blog": base_web_url + post.website_url
            })
        total = request.env['blog.post'].sudo().search_count(domain)
        return http.Response(
            json.dumps({
                "status": "success",
                "data": data,
                "total": total,
                "page": page,
                "limit": limit
            }),
            content_type='application/json',
            status=200
        )

    @http.route('/api/news/<id>', type='http',
                auth='public', methods=['GET'], csrf=False)
    def get_blog_news(self, **kwargs):
        base_web_url = \
            request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        blog_id = kwargs.get('id')
        post = request.env['blog.post'].sudo().browse(int(blog_id))
        url_image = base_web_url + \
            json.loads(post.cover_properties)['background-image']\
            .replace('url(', '').replace(')', '')
        url_blog = base_web_url + post.website_url
        return http.Response(
            json.dumps({
                "status": "success",
                "id": int(blog_id),
                "title": post.name,
                "subtitle": post.subtitle or "",
                "publish_date": post.published_date,
                "url_image": url_image,
                "content": post.content,
                "url_blog": url_blog
            }),
            content_type='application/json',
            status=200,
            )
