"""
The latest version of this package is available at:
<http://github.com/jantman/biweeklybudget>

################################################################################
Copyright 2016 Jason Antman <jason@jasonantman.com> <http://www.jasonantman.com>

    This file is part of biweeklybudget, also known as biweeklybudget.

    biweeklybudget is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    biweeklybudget is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with biweeklybudget.  If not, see <http://www.gnu.org/licenses/>.

The Copyright and Authors attributions contained herein may not be removed or
otherwise altered, except to add the Author attribution of a contributor to
this work. (Additional Terms pursuant to Section 7b of the AGPL v3)
################################################################################
While not legally required, I sincerely request that anyone who finds
bugs please submit them at <https://github.com/jantman/biweeklybudget> or
to me via email, and that you send any contributions or improvements
either as a pull request on GitHub, or to me via email.
################################################################################

AUTHORS:
Jason Antman <jason@jasonantman.com> <http://www.jasonantman.com>
################################################################################
"""

from flask.views import MethodView
from flask import render_template, jsonify

from biweeklybudget.flaskapp.app import app
from biweeklybudget.db import db_session
from biweeklybudget.models.budget_model import Budget
from biweeklybudget.models.account import Account


class BudgetsView(MethodView):

    def get(self):
        standing = db_session.query(Budget).filter(
            Budget.is_active.__eq__(True), Budget.is_periodic.__eq__(False)
        ).order_by(Budget.name).all()
        periodic = db_session.query(Budget).filter(
            Budget.is_active.__eq__(True), Budget.is_periodic.__eq__(True)
        ).order_by(Budget.name).all()
        accts = {}
        for a in db_session.query(Account).all():
            accts[a.name] = a.id
        return render_template(
            'budgets.html',
            standing=standing,
            periodic=periodic,
            accts=accts
        )


class BudgetAjax(MethodView):
    """
    Handle GET /ajax/budget/<int:budget_id> endpoint.
    """

    def get(self, budget_id):
        budget = db_session.query(Budget).get(budget_id)
        return jsonify(budget.as_dict)


app.add_url_rule('/budgets', view_func=BudgetsView.as_view('budgets_view'))
app.add_url_rule(
    '/ajax/budget/<int:budget_id>',
    view_func=BudgetAjax.as_view('budget_ajax')
)
