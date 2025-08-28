{
    'name': 'Bulk Vendor Bill Return',
    'version': '1.0',
    'category': 'Accounting/Accounting',
    'summary': 'Enable direct Returning',
    'author': 'gladdema',
    'website': 'https://gladdema.com',
    'depends': ['base', 'account','purchase'],
    'data': [
        'security/ir.model.access.csv', 
        'views/vendor_view.xml',
        'views/res_partner_credit_note_button.xml', 
        'views/account_move.xml', 
        'views/purchase_order.xml',        
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
