odoo.define('sale_order_comercionet.get_orders',function (require) {
    let core = require('web.core');
    let ListController = require('web.ListController');
    let rpc = require('web.rpc');
    let session = require('web.session');
    let _t = core._t;
    ListController.include({
        renderButtons: function ($node) {
            this._super.apply(this,arguments);
            if(this.$buttons){
                this.$buttons.find('#getorders').click(this.proxy('action_get_orders'));
            }
        },
        action_get_orders: function () {
            let self = this;
            let user = session.uid;
            rpc.query({
                model: 'sale.order.comercionet',
                method: 'get_orders',
                args: [{'id': user}],
            })
        }
    })
})