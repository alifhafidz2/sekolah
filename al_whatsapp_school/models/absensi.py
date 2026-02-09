import logging
import requests
from datetime import datetime

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class AbsensiWhatsApp(models.Model):
    _inherit = 'sekolah.absensi'

    whatsapp_sent = fields.Boolean(string='WhatsApp Terkirim', default=False, copy=False)
    whatsapp_log_ids = fields.One2many('whatsapp.log', 'absensi_id', string='Log WhatsApp')

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for record in records:
            if record.status == 'alfa':
                record._send_whatsapp_notification()
        return records

    def write(self, vals):
        res = super().write(vals)
        if vals.get('status') == 'alfa':
            for record in self:
                if not record.whatsapp_sent:
                    record._send_whatsapp_notification()
        return res

    def _send_whatsapp_notification(self):
        self.ensure_one()
        config = self.env['whatsapp.config'].get_active_config()
        if not config:
            _logger.warning('WhatsApp config not found or not active')
            return

        siswa = self.siswa_id
        if not siswa:
            return

        message = self._prepare_whatsapp_message(config)
        recipients = self._get_recipients(config, siswa)

        for recipient_type, phone in recipients:
            if phone:
                self._send_single_whatsapp(config, phone, message, recipient_type)

        self.whatsapp_sent = True

    def _prepare_whatsapp_message(self, config):
        siswa = self.siswa_id
        mapel_name = self.mata_pelajaran_id.name if self.mata_pelajaran_id else '-'
        kelas_name = self.kelas_id.name if self.kelas_id else '-'
        tanggal_str = self.tanggal.strftime('%d %B %Y') if self.tanggal else '-'

        message = config.message_template or ''
        message = message.replace('{nama_siswa}', siswa.name or '')
        message = message.replace('{kelas}', kelas_name)
        message = message.replace('{nis}', siswa.nis or '')
        message = message.replace('{tanggal}', tanggal_str)
        message = message.replace('{mapel}', mapel_name)

        return message

    def _get_recipients(self, config, siswa):
        recipients = []
        if config.send_to_ayah and siswa.telepon_ayah:
            recipients.append(('ayah', self._format_phone_number(siswa.telepon_ayah)))
        if config.send_to_ibu and siswa.telepon_ibu:
            recipients.append(('ibu', self._format_phone_number(siswa.telepon_ibu)))
        if config.send_to_wali and siswa.telepon_wali:
            recipients.append(('wali', self._format_phone_number(siswa.telepon_wali)))
        return recipients

    def _format_phone_number(self, phone):
        if not phone:
            return ''
        phone = phone.strip().replace(' ', '').replace('-', '')
        if phone.startswith('08'):
            phone = '62' + phone[1:]
        elif phone.startswith('+62'):
            phone = phone[1:]
        return phone

    def _send_single_whatsapp(self, config, phone, message, recipient_type):
        log = self.env['whatsapp.log'].create({
            'siswa_id': self.siswa_id.id,
            'absensi_id': self.id,
            'phone_number': phone,
            'recipient_type': recipient_type,
            'message': message,
            'status': 'pending',
        })

        try:
            response = self._call_whatsapp_api(config, phone, message)
            log.write({
                'status': 'sent',
                'response': str(response),
                'sent_date': fields.Datetime.now(),
            })
            _logger.info(f'WhatsApp sent to {phone} for siswa {self.siswa_id.name}')
        except Exception as e:
            log.write({
                'status': 'failed',
                'error_message': str(e),
            })
            _logger.error(f'Failed to send WhatsApp to {phone}: {str(e)}')

    def _call_whatsapp_api(self, config, phone, message):
        if not config.api_url:
            raise ValueError('API URL tidak dikonfigurasi')

        if config.provider != 'waha' and not config.api_token:
            raise ValueError('API Token tidak dikonfigurasi')

        headers = {}
        payload = {}
        use_json = True

        if config.provider == 'waha':
            chat_id = f"{phone}@c.us"
            headers = {
                'Content-Type': 'application/json',
            }
            if config.api_token:
                headers['X-Api-Key'] = config.api_token
            payload = {
                'chatId': chat_id,
                'text': message,
                'session': config.waha_session or 'default',
            }
        elif config.provider == 'fonnte':
            headers = {
                'Authorization': config.api_token,
            }
            payload = {
                'target': phone,
                'message': message,
            }
            use_json = False
        elif config.provider == 'wablas':
            headers = {
                'Authorization': config.api_token,
                'Content-Type': 'application/json',
            }
            payload = {
                'phone': phone,
                'message': message,
            }
        elif config.provider == 'woowa':
            headers = {
                'Content-Type': 'application/json',
            }
            payload = {
                'api_key': config.api_token,
                'phone_no': phone,
                'message': message,
            }
        else:
            headers = {
                'Authorization': f'Bearer {config.api_token}',
                'Content-Type': 'application/json',
            }
            payload = {
                'phone': phone,
                'message': message,
            }

        response = requests.post(
            config.api_url,
            headers=headers,
            json=payload if use_json else None,
            data=payload if not use_json else None,
            timeout=30
        )

        return response.json()

    def action_resend_whatsapp(self):
        self.ensure_one()
        if self.status == 'alfa':
            self.whatsapp_sent = False
            self._send_whatsapp_notification()
        return True

    def action_view_whatsapp_logs(self):
        self.ensure_one()
        return {
            'name': 'Log WhatsApp',
            'type': 'ir.actions.act_window',
            'res_model': 'whatsapp.log',
            'view_mode': 'tree,form',
            'domain': [('absensi_id', '=', self.id)],
            'context': {'default_absensi_id': self.id},
        }
