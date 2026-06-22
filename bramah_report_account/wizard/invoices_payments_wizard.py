from odoo import api, fields, models


class InvoicesPaymentsWizard(models.TransientModel):
    _name = 'invoices.payments.wizard'
    _description = 'Facturas y Pagos - Wizard de Reporte'

    date_from = fields.Date(string='Fecha inicio', required=True)
    date_to = fields.Date(string='Fecha fin', required=True)
    partner_id = fields.Many2one('res.partner', string='Cliente')
    journal_id = fields.Many2one('account.journal', string='Diario')

    def action_print_report(self):
        return self.env.ref('bramah_report_account.action_report_invoices_payments').report_action(self)

    def action_download_xlsx(self):
        return self.env.ref('bramah_report_account.action_report_invoices_payments_xlsx').report_action(self)
