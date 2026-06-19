from odoo import api, fields, models


class InvoicesPaymentsWizard(models.TransientModel):
    _name = 'invoices.payments.wizard'
    _description = 'Facturas y Pagos - Wizard de Reporte'

    date_from = fields.Date(string='Fecha inicio', required=True)
    date_to = fields.Date(string='Fecha fin', required=True)

    def action_print_report(self):
        return self.env.ref('bramah_report_account.action_report_invoices_payments').report_action(self)
