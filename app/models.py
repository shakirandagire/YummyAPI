from app import db

class Category(db.Model):
    """This class represents the bucketlist table."""

    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    categoryname = db.Column(db.String(255))
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())
    date_modified = db.Column(
        db.DateTime, default=db.func.current_timestamp(),
        onupdate=db.func.current_timestamp())

    def __init__(self, categoryname):
        """initialize with name."""
        self.categoryname = categoryname

    def save(self):
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def get_all():
        return Category.query.all()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def __repr__(self):
        return "<Category: {}>".format(self.categoryname)