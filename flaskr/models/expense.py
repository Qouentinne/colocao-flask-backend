from .user import User
from .base import BaseModel
from sqlalchemy import Column, String, ForeignKey, Float
from sqlalchemy.orm import relationship

class Expense(BaseModel):
    __tablename__ = "expenses"
    amount = Column(Float, nullable=False)
    debitor_id = Column(ForeignKey(User.id), nullable=False)
    creditor_id = Column(ForeignKey(User.id), nullable=False)
    name = Column(String, nullable=False)

    debitor = relationship(User, foreign_keys=[debitor_id], back_populates="debits")
    creditor = relationship(User, foreign_keys=[creditor_id], back_populates="credits")


def get_per_user_amount(user: User):
    debits = user.debits
    credits = user.credits

    debits_amount = float(sum([debit.amount for debit in debits]) )
    credits_amount = float(sum([credit.amount for credit in credits]))

    total = {"total": credits_amount - debits_amount}

    creditors = set([debit.creditor for debit in debits])
    debitors = set([credit.debitor for credit in credits])
    relations: list[User] = list(creditors.union(debitors))
    sorted_relations = sorted(relations, key=lambda relation: relation.username)

    subtotals = {relation.id: {'name': relation.username, 'amount': 0} for relation in sorted_relations}

    for debit in debits:
        subtotals[debit.creditor_id]['amount'] -= debit.amount

    for credit in credits:
        subtotals[credit.debitor_id]['amount'] += credit.amount

    subtotals = [{"id": k, "name": v["name"], "amount": v["amount"]} for k, v in subtotals.items()]

    return dict(**total, participants = subtotals)