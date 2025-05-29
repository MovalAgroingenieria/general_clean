# -*- coding: utf-8 -*-
# 2025 Moval Agroingeniería
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import re
from email.utils import formataddr
from odoo import tools

_EMAIL_ONLY_RE = re.compile(
    r'<\s*([^>]+)\s*>'
    r'|'
    r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b'
)


def email_split_custom(text):
    if not text:
        return []
    emails = []
    for m in _EMAIL_ONLY_RE.finditer(text):
        raw = m.group(1) or m.group(0)
        if m.group(1) and (';' in raw or ',' in raw):
            for part in re.split(r'[;,]', raw):
                part = part.strip()
                if part:
                    emails.append(part)
        else:
            emails.append(raw.strip())
    return emails


def email_split_and_format_custom(text):
    if not text:
        return []
    return [
        formataddr(('', addr))
        for addr in email_split_custom(text)
    ]


tools.email_split = email_split_custom
tools.email_split_and_format = email_split_and_format_custom
