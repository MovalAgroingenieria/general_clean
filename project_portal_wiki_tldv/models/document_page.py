# -*- coding: utf-8 -*-
# 2025 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api
import requests


class DocumentPage(models.Model):
    _inherit = 'document.page'
    _TLDV_ENDPOINT_URL = 'https://pasta.tldv.io/v1alpha1/meetings'

    allowed_portal_user_ids = fields.Many2many(
        comodel_name='res.users',
        string='Visible to',
        store=True,
        readonly=False,
        copy=False,
    )

    tldv_meeting_id = fields.Char(
        string="TLDV Meeting ID"
    )

    tldv_meeting_url = fields.Char(
        string="TLDV Meeting URL"
    )

    tldv_meeting_time = fields.Datetime(
        string="TLDV Meeting Time"
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            project_id = vals.get('project_id')
            if project_id:
                project = self.env['project.project'].browse(project_id)
                if project.privacy_visibility == 'portal':
                    vals['allowed_portal_user_ids'] = [
                        (6, 0, project.allowed_portal_user_ids.ids)]
        return super().create(vals_list)

    def write(self, vals):
        if 'project_id' in vals or 'allowed_portal_user_ids' not in vals:
            for record in self:
                project = record.project_id
                if vals.get('project_id'):
                    project = self.env['project.project'].browse(
                        vals['project_id'])
                if project and project.privacy_visibility == 'portal':
                    vals['allowed_portal_user_ids'] = [
                        (6, 0, project.allowed_portal_user_ids.ids)]
        return super().write(vals)

    def _get_document_page_from_tldv(self):
        pass

    def generate_highlights_html(self, data, url):
        html = []
        categories = {}
        html.append(f"<a href=\"{url}\">{url}</a>")
        for item in data:
            cat = item.get("category", {}).get("label", "")
            categories.setdefault(cat, []).append(item)
        for cat, items in categories.items():
            if items:
                html.append(f"<section><h4><b>{cat}</b> <br></h4><ul>")
                for item in items:
                    startTime = item.get("startTime", 0)
                    if startTime >= 3600:
                        hours, remainder = divmod(startTime, 3600)
                        minutes, seg = divmod(remainder, 60)
                        time_str = f"{hours:02d}:{minutes:02d}:{seg:02d}"
                    else:
                        minutes, seg = divmod(startTime, 60)
                        time_str = f"{minutes:02d}:{seg:02d}"
                    meeting_url = url
                    link = f"{meeting_url}?t={startTime}"
                    text = item.get("text", "")
                    html.append(f'<li>{text}<!-- -->&nbsp;'
                                f'<a href="{link}">{time_str}</a></li>')
                html.append("</ul><br> </section>")
        return "\n".join(line.strip() for line in html)

    @api.model
    def cron_retrieve_meetings_data(self):
        last_meeting = self.env['document.page'].search(
            [('tldv_meeting_id', '!=', False)], order="id desc", limit=1)
        last_meeting_date = last_meeting["create_date"] if last_meeting \
            else None
        last_meeting_date = last_meeting_date.date().isoformat() if \
            last_meeting_date else None

        API_KEY = self.env['ir.config_parameter'].get_param(
            'project_portal_wiki_tldv.api_key')
        API_URL = self.env['ir.config_parameter'].get_param(
            'project_portal_wiki_tldv.tldv_url')
        DEFAULT_CATEG = int(self.env['ir.config_parameter'].get_param(
            'project_portal_wiki_tldv.tldv_default_category_id'))
        DEFAULT_PROJECT = int(self.env['ir.config_parameter'].get_param(
            'project_portal_wiki_tldv.tldv_default_project_id'))
        HEADERS = {
            "x-api-key": API_KEY
        }
        params = {
            "from": last_meeting_date,
            "limit": 100
        }
        meetings = []
        try:
            response = requests.get(
                f"{API_URL}v1alpha1/meetings",
                headers=HEADERS, params=params
            )
            meetings = response.json()
        except Exception as e:
            print("Error fetching meetings:", e)
            return

        results = meetings.get("results", [])

        for item in results:
            exists = self.env['document.page'].search([
                ('tldv_meeting_id', '=', item["id"]),])
            if not exists:
                try:
                    response2 = requests.get(
                        f"{API_URL}v1alpha1/meetings/{item['id']}",
                        headers=HEADERS
                    )
                    response3 = requests.get(
                        f"{API_URL}v1alpha1/meetings/{item['id']}/highlights",
                        headers=HEADERS
                    )
                    details = response2.json()
                    details2 = response3.json()
                    html = self.generate_highlights_html(details2["data"],
                                                         url=details["url"])
                    self.env["document.page"].create({
                            "name": details["name"],
                            "tldv_meeting_id": details["id"],
                            "tldv_meeting_url": details["url"],
                            "draft_name": 'Rev 01',
                            "draft_summary": 'Retrieve from TLDV',
                            "parent_id": DEFAULT_CATEG,
                            "project_id": DEFAULT_PROJECT,
                            "content": html,
                    })
                except Exception as e:
                    print("Error fetching meetings:", e)
                    return
