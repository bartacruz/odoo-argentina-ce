# -*- coding: utf-8 -*-
from openerp import fields, models, api, _
from openerp.exceptions import Warning
import logging
_logger = logging.getLogger(__name__)


class afip_point_of_sale(models.Model):
    _inherit = 'afip.point_of_sale'

    afip_ws = fields.Selection([
        ('wsfe', 'Mercado interno -sin detalle- RG2485 (WSFEv1)'),
        ('wsmtxca', 'Mercado interno -con detalle- RG2904 (WSMTXCA)'),
        ('wsfex', 'Exportación -con detalle- RG2758 (WSFEXv1)'),
        ('wsbfe', 'Bono Fiscal -con detalle- RG2557 (WSMTXCA)'),
        ],
        'AFIP WS',
        )

    @api.multi
    def check_document_local_remote_number(self):
        msg = ''
        for j_document_class in self.journal_document_class_ids.filtered(
                lambda r: r.journal_id.type in ['sale', 'sale_refund']):
            next_by_ws = int(
                j_document_class.get_pyafipws_last_invoice()['result']) + 1
            next_by_seq = j_document_class.sequence_id.number_next_actual
            if next_by_ws != next_by_seq:
                msg += _(
                    '* Document Class %s (id %i), Local %i, Remote %i\n' % (
                        j_document_class.afip_document_class_id.name,
                        j_document_class.id,
                        next_by_seq,
                        next_by_ws))
        if msg:
            msg = _('There are some doument desynchronized:\n') + msg
            raise Warning(msg)
        else:
            raise Warning(_('All documents are synchronized'))

    @api.multi
    def test_pyafipws_dummy(self):
        """
        AFIP Description: Método Dummy para verificación de funcionamiento de
        infraestructura (FEDummy)
        """
        self.ensure_one()
        afip_ws = self.afip_ws
        if not afip_ws:
            raise Warning(_('No AFIP WS selected'))
        ws = self.company_id.get_connection(afip_ws).connect()
        ws.Dummy()
        title = _("AFIP service %s\n") % afip_ws
        msg = (
            "AppServerStatus: %s DbServerStatus: %s AuthServerStatus: %s" % (
                ws.AppServerStatus,
                ws.DbServerStatus,
                ws.AuthServerStatus))
        raise Warning(title + msg)

    @api.multi
    def test_pyafipws_point_of_sales(self):
        self.ensure_one()
        afip_ws = self.afip_ws
        if not afip_ws:
            raise Warning(_('No AFIP WS selected'))
        ws = self.company_id.get_connection(afip_ws).connect()
        if afip_ws == 'wsfex':
            ret = ws.GetParamPtosVenta()
        else:
            ret = ws.ParamGetPtosVenta(sep=" ")
        msg = (_(" %s %s") % (
            '. '.join(ret), " - ".join([ws.Excepcion, ws.ErrMsg, ws.Obs])))
        title = _('Enabled Point Of Sales on AFIP\n')
        raise Warning(title + msg)

    @api.multi
    def get_pyafipws_cuit_document_classes(self):
        self.ensure_one()
        afip_ws = self.afip_ws
        if not afip_ws:
            raise Warning(_('No AFIP WS selected'))
        ws = self.company_id.get_connection(afip_ws).connect()
        if afip_ws == 'wsfex':
            ret = ws.GetParamPtosVenta(sep=" ")
        else:
            ret = ws.ParamGetTiposCbte(sep=" ")
        msg = (_(" %s %s") % (
            '. '.join(ret), " - ".join([ws.Excepcion, ws.ErrMsg, ws.Obs])))
        title = _('Authorized Document Clases on AFIP\n')
        raise Warning(title + msg)

    @api.multi
    def get_pyafipws_currencies(self):
        self.ensure_one()
        afip_ws = self.afip_ws
        if not afip_ws:
            raise Warning(_('No AFIP WS selected'))
        ws = self.company_id.get_connection(afip_ws).connect()
        if afip_ws == 'wsfex':
            raise Warning('Not implemented yet')
            # ret = ws.GetParamPtosVenta(sep=" ")
        else:
            ret = ws.ParamGetTiposMonedas(sep=" ")
        msg = (_(" %s %s") % (
            '. '.join(ret), " - ".join([ws.Excepcion, ws.ErrMsg, ws.Obs])))
        title = _('Authorized Currencies on AFIP\n')
        raise Warning(title + msg)

    @api.multi
    def action_get_connection(self):
        self.ensure_one()
        afip_ws = self.afip_ws
        if not afip_ws:
            raise Warning(_('No AFIP WS selected'))
        self.company_id.get_connection(afip_ws).connect()