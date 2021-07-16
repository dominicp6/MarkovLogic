#include "constant.h"
#include "type.h"

ostream& Constant::print(ostream& out) const
{
  out << id_ << ":" << name_ << ":" << type_->name();
  return out;
}

int Constant::typeId() const { return type_->id(); }

string Constant::typeName() const { return type_->name(); }
