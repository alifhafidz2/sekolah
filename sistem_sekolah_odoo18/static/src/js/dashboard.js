/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component } from "@odoo/owl";

export class SekolahDashboard extends Component {
    setup() {
        // Dashboard setup logic
    }
}

SekolahDashboard.template = "sistem_sekolah_odoo18.Dashboard";

registry.category("actions").add("sekolah_dashboard", SekolahDashboard);
