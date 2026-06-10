import enum

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.database import Base


class ApiaryMemberRole(str, enum.Enum):
    owner = "owner"
    admin = "admin"
    member = "member"
    viewer = "viewer"


class ApiaryMember(Base):
    __tablename__ = "apiary_members"
    __table_args__ = (UniqueConstraint("apiary_id", "user_id", name="uq_apiary_members_apiary_user"),)

    id = Column(Integer, primary_key=True, index=True)
    apiary_id = Column(Integer, ForeignKey("apiaries.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role = Column(Enum(ApiaryMemberRole), nullable=False, default=ApiaryMemberRole.member)
    invited_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    accepted_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    apiary = relationship("Apiary", back_populates="members")
    user = relationship("User", foreign_keys=[user_id], back_populates="apiary_memberships")
    invited_by = relationship("User", foreign_keys=[invited_by_user_id])
