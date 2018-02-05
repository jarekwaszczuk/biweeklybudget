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

import logging
from sqlalchemy import (
    Column, Integer, Numeric, String, Date, ForeignKey, inspect
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql.expression import null
from biweeklybudget.models.base import Base, ModelAsDict
from biweeklybudget.utils import dtnow
from biweeklybudget.settings import RECONCILE_BEGIN_DATE

logger = logging.getLogger(__name__)


class Transaction(Base, ModelAsDict):

    __tablename__ = 'transactions'
    __table_args__ = (
        {'mysql_engine': 'InnoDB'}
    )

    #: Primary Key
    id = Column(Integer, primary_key=True)

    #: date of the transaction
    date = Column(Date, default=dtnow().date())

    #: Actual amount of the transaction
    actual_amount = Column(Numeric(precision=10, scale=4), nullable=False)

    #: Budgeted amount of the transaction, if it was budgeted ahead of time
    #: via a :py:class:`~.ScheduledTransaction`.
    budgeted_amount = Column(Numeric(precision=10, scale=4))

    #: description
    description = Column(String(254), nullable=False, index=True)

    #: free-form notes
    notes = Column(String(254))

    #: ID of the account this transaction is against
    account_id = Column(Integer, ForeignKey('accounts.id'))

    #: Relationship - :py:class:`~.Account` this transaction is against
    account = relationship(
        "Account", backref="transactions", uselist=False
    )

    #: ID of the ScheduledTransaction this Transaction was created from;
    #: set when a scheduled transaction is converted to a real one
    scheduled_trans_id = Column(
        Integer, ForeignKey('scheduled_transactions.id')
    )

    #: Relationship - the :py:class:`~.ScheduledTransaction`
    #: this Transaction was created from; set when a scheduled transaction
    #: is converted to a real one
    scheduled_trans = relationship(
        "ScheduledTransaction", backref="transactions", uselist=False
    )

    #: ID of the Budget this transaction is against
    budget_id = Column(Integer, ForeignKey('budgets.id'))

    #: Relationship - the :py:class:`~.Budget` this transaction is against
    budget = relationship(
        "Budget", backref="transactions", uselist=False,
        foreign_keys=[budget_id]
    )

    #: ID of the Budget this transaction was planned to be funded by, if it
    #: was planned ahead via a :py:class:`~.ScheduledTransaction`
    planned_budget_id = Column(Integer, ForeignKey('budgets.id'))

    #: Relationship - the :py:class:`~.Budget` this transaction was planned to
    #: be funded by, if it was planned ahead via a
    #: :py:class:`~.ScheduledTransaction`.
    planned_budget = relationship(
        "Budget", backref="planned_transactions", uselist=False,
        foreign_keys=[planned_budget_id]
    )

    #: If the transaction is one half of a transfer, the Transaction ID of the
    #: other half/side of the transfer.
    transfer_id = Column(Integer, ForeignKey('transactions.id'))

    #: Relationship - the :py:class:`~.Transaction` that makes up the other
    #: half/side of a transfer, if this transaction was for a transfer.
    transfer = relationship(
        "Transaction", remote_side=[id], post_update=True, uselist=False
    )

    def __repr__(self):
        return "<Transaction(id=%s)>" % (
            self.id
        )

    @staticmethod
    def unreconciled(db):
        """
        Return a query to match all unreconciled Transactions.

        :param db: active database session to use for queries
        :type db: sqlalchemy.orm.session.Session
        :return: query to match all unreconciled Transactions
        :rtype: sqlalchemy.orm.query.Query
        """
        return db.query(Transaction).filter(
            Transaction.reconcile.__eq__(null()),
            Transaction.date.__ge__(RECONCILE_BEGIN_DATE),
            Transaction.account.has(reconcile_trans=True)
        )

    def set_budget_amounts(self, budget_amounts):
        """
        Manage child :py:class:`~.BudgetTransaction` objects corresponding to
        budget allocations of the amount of this transaction. Given a dictionary
        (``budget_amounts``) of budgets (either int ID or :py:class:`~.Budget`
        instances) to Decimal amounts, ensure that the BudgetTransactions for
        this Transaction match those amounts.

        :param budget_amounts: Mapping of one or more Budgets to the amount of
          this Transaction allocated to that Budget. Keys may be either an int
          :py:attr:`~.Budget.id` or a :py:class:`~.Budget` instance, values must
          be a Decimal.
        :type budget_amounts: dict
        """
        sess = inspect(self).session
