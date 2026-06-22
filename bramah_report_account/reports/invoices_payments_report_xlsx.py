from collections import OrderedDict

from odoo import models


class ReportInvoicesPaymentsXlsx(models.AbstractModel):
    _name = 'report.bramah_report_account.report_invoices_payments_xlsx'
    _inherit = 'report.report_xlsx.abstract'
    _description = 'Reporte de Facturas y Pagos - XLSX'

    def generate_xlsx_report(self, workbook, data, objects):
        wizard = objects[0] if objects else None
        if not wizard:
            return

        partner_id = wizard.partner_id.id if wizard.partner_id else False
        journal_id = wizard.journal_id.id if wizard.journal_id else False

        payments = self.env['account.payment'].search([
            ('payment_type', '=', 'inbound'),
            ('partner_type', '=', 'customer'),
            ('date', '>=', wizard.date_from),
            ('date', '<=', wizard.date_to),
            ('state', '=', 'posted'),
        ])

        if not payments:
            return

        payment_by_move_id = {p.move_id.id: p for p in payments}

        partials = self.env['account.partial.reconcile'].search([
            ('credit_move_id.move_id', 'in', list(payment_by_move_id.keys())),
        ])

        partner_map = OrderedDict()
        for partial in partials:
            invoice = partial.debit_move_id.move_id
            if invoice.move_type != 'out_invoice' or invoice.state != 'posted':
                continue
            if partner_id and invoice.commercial_partner_id.id != partner_id:
                continue
            payment = payment_by_move_id.get(partial.credit_move_id.move_id.id)
            if not payment:
                continue
            if journal_id and payment.journal_id.id != journal_id:
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
            })

        lines = list(partner_map.values())
        if not lines:
            return

        sheet = workbook.add_worksheet('Facturas y Pagos')

        title_format = workbook.add_format({
            'bold': True, 'font_size': 14, 'align': 'center', 'valign': 'vcenter',
        })
        header_format = workbook.add_format({
            'bold': True, 'font_size': 10, 'bg_color': '#4472C4', 'font_color': 'white',
            'border': 1, 'align': 'center', 'valign': 'vcenter', 'text_wrap': True,
        })
        cell_format = workbook.add_format({
            'font_size': 10, 'border': 1, 'valign': 'vcenter',
        })
        amount_format = workbook.add_format({
            'font_size': 10, 'border': 1, 'valign': 'vcenter', 'align': 'right',
            'num_format': '#,##0.00',
        })
        date_format = workbook.add_format({
            'font_size': 10, 'border': 1, 'valign': 'vcenter', 'align': 'center',
            'num_format': 'dd/mm/yyyy',
        })
        partner_format = workbook.add_format({
            'bold': True, 'font_size': 11,
        })

        sheet.merge_range(0, 0, 0, 5, 'Facturas y Pagos', title_format)
        sheet.write(1, 0, 'Período: {} - {}'.format(wizard.date_from, wizard.date_to))

        row = 3

        headers = ['Factura', 'Fecha Factura', 'Total Factura', 'Fecha Pago', 'Valor Pagado', 'Diario']
        for col, header in enumerate(headers):
            sheet.write(row, col, header, header_format)

        row += 1

        for partner_data in lines:
            partner_label = partner_data['partner_name']
            if partner_data['partner_vat']:
                partner_label += ' ({})'.format(partner_data['partner_vat'])
            sheet.merge_range(row, 0, row, 5, partner_label, partner_format)
            row += 1
            for line in partner_data['lines']:
                sheet.write(row, 0, line['invoice_name'], cell_format)
                sheet.write(row, 1, line['invoice_date'], date_format)
                sheet.write(row, 2, line['invoice_total'], amount_format)
                sheet.write(row, 3, line['payment_date'], date_format)
                sheet.write(row, 4, line['payment_amount'], amount_format)
                sheet.write(row, 5, line['payment_method'], cell_format)
                row += 1

        sheet.set_column(0, 0, 20)
        sheet.set_column(1, 1, 14)
        sheet.set_column(2, 2, 16)
        sheet.set_column(3, 3, 14)
        sheet.set_column(4, 4, 16)
        sheet.set_column(5, 5, 20)
