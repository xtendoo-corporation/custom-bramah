from collections import OrderedDict

from odoo import api, fields, models


class ReportInvoicesPayments(models.AbstractModel):
    _name = 'report.bramah_report_account.report_invoices_payments'
    _description = 'Reporte de Facturas y Pagos'

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['invoices.payments.wizard'].browse(docids)
        wizard = docs[0] if docs else None

        lines = []

        if not wizard:
            return {
                'doc_ids': docids,
                'docs': docs,
                'data': data,
                'lines': lines,
                'date_from': False,
                'date_to': False,
            }

        payments = self.env['account.payment'].search([
            ('payment_type', '=', 'inbound'),
            ('partner_type', '=', 'customer'),
            ('date', '>=', wizard.date_from),
            ('date', '<=', wizard.date_to),
            ('state', '=', 'posted'),
        ])

        if not payments:
            return {
                'doc_ids': docids,
                'docs': docs,
                'data': data,
                'lines': lines,
                'date_from': wizard.date_from,
                'date_to': wizard.date_to,
            }

        # Map payments by their account.move id for fast lookup
        payment_by_move_id = {p.move_id.id: p for p in payments}

        # Find partial reconciles where payments are the credit side
        partials = self.env['account.partial.reconcile'].search([
            ('credit_move_id.move_id', 'in', list(payment_by_move_id.keys())),
        ])

        # Build flat rows ordered by partner -> invoice -> payment
        partner_map = OrderedDict()
        for partial in partials:
            invoice = partial.debit_move_id.move_id
            if invoice.move_type != 'out_invoice' or invoice.state != 'posted':
                continue
            payment = payment_by_move_id.get(partial.credit_move_id.move_id.id)
            if not payment:
                continue

            partner = invoice.commercial_partner_id
            if partner.id not in partner_map:
                partner_map[partner.id] = {
                    'partner_name': partner.name,
                    'partner_vat': partner.vat,
                    'lines': [],
                }
            partner_map[partner.id]['lines'].append({
                'invoice_name': invoice.name,
                'invoice_date': invoice.invoice_date,
                'invoice_total': invoice.amount_total,
                'payment_date': payment.date,
                'payment_amount': partial.amount,
                'payment_method': payment.journal_id.name,
                'invoice_total_fmt': '{:,.2f} {}'.format(invoice.amount_total, invoice.company_id.currency_id.symbol or ''),
                'payment_amount_fmt': '{:,.2f} {}'.format(partial.amount, invoice.company_id.currency_id.symbol or ''),
            })

        lines = list(partner_map.values())

        return {
            'doc_ids': docids,
            'docs': docs,
            'data': data,
            'lines': lines,
            'date_from': wizard.date_from,
            'date_to': wizard.date_to,
        }
