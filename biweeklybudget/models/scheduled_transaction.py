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

from sqlalchemy import (
    Column, Integer, String, Boolean, Date, SmallInteger, Numeric,
    ForeignKey
)
from sqlalchemy.orm import relationship, validates
from biweeklybudget.models.base import Base, ModelAsDict


class ScheduledTransaction(Base, ModelAsDict):

    __tablename__ = 'scheduled_transactions'
    __table_args__ = (
        {'mysql_engine': 'InnoDB'}
    )

    #: Primary Key
    id = Column(Integer, primary_key=True)

    #: Amount of the transaction
    amount = Column(Numeric(precision=10, scale=4), nullable=False)

    #: description
    description = Column(String(254), nullable=False, index=True)

    #: notes
    notes = Column(String(254))

    #: ID of the account the transaction is against
    account_id = Column(Integer, ForeignKey('accounts.id'))

    #: Relationship - :py:class:`~.Account` the transaction is against
    account = relationship(
        "Account", backref="scheduled_transactions"
    )

    #: ID of the budget the transaction is against
    budget_id = Column(Integer, ForeignKey('budgets.id'))

    #: Relationship - :py:class:`~.Budget` the transaction is against
    budget = relationship(
        "Budget", backref="scheduled_transactions"
    )

    #: whether the scheduled transaction is enabled or disabled
    is_active = Column(Boolean, default=True)

    #: Denotes a scheduled transaction that will happen once on the given date
    date = Column(Date)

    #: Denotes a scheduled transaction that happens on the same day of each
    #: month
    day_of_month = Column(SmallInteger)

    #: Denotes a scheduled transaction that happens N times per pay period
    num_per_period = Column(SmallInteger)

    def __repr__(self):
        return "<ScheduledTransaction(id=%d)>" % (
            self.id
        )

    @validates('day_of_month')
    def validate_day_of_month(self, _, value):
        assert value > 0
        assert value <= 31
        return value

    @validates('num_per_period')
    def validate_num_per_period(self, _, value):
        assert value > 0
        return value
