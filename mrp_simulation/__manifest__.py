# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Simulation de production",
    "version": "14.0.0.0.2",
    "category": "Manufacturing",
    "author": "ArPol-dev",
    "license": "AGPL-3",
    "website": "https://github.com/arpol-dev",
    "depends": ["mrp", "sale_management"],
    "data": [
        "views/sale_order_view.xml",
        "security/ir.model.access.csv",
        "report/report_simulation.xml",
        "report/simulation_report_print.xml"
    ],
    "installable": True,
}
