from odoo import http
from odoo.http import request
import json


class GisviewerManagementController(http.Controller):

    @http.route("/gisviewer_config", auth='none', type='json', method=['GET'])
    def gisviewer_config(self, **values):
        all_layers = request.env['gisviewer.layer'].sudo().search([])
        output = {}
        for layer in all_layers:
            profile_configs = {}
            for layerprofile in layer.layerprofile_ids:
                profile_configs['activePublic'] = layerprofile.active_public
                profile_configs['visiblePublic'] = layerprofile.visible_public
                profile_configs['activePrivate'] = layerprofile.active_private
                profile_configs['visiblePrivate'] = \
                    layerprofile.visible_private
            output[layer.code] = {
                'profileConfigs': profile_configs
            }
        return json.dumps(output)
