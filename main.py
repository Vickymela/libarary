from flask import Flask,jsonify,request
from flask_sqlalchemy import SQLAlchemy
from datetime import date, datetime

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///travel.db"
db = SQLAlchemy(app)


class Books(db.Model):
    id =db.Column(db.Integer,primary_key=True)
    book_name = db.Column(db.String(150),nullable=False)
    book_author = db.Column(db.String(300),nullable=False)
    is_avaliable = db.Column(db.Boolean, default=False)


    def to_dict(self):
        return{
            "book_name":self.book_name,
            "book_author":self. book_author,
            "is_avaliable":self.is_avaliable
        }
    
class User(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    user_name = db.Column(db.String(300),nullable=False)
   
   

    
    def to_dict(self):
        return{
            "user_name":self.user_name,
             
        }
    
class Records(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    user_id = db.Column(db.Integer,db.ForeignKey('user.id'))
    user_book = db.Column(db.Integer,db.ForeignKey('books.id'))
    status=db.Column(db.String(50),default="borrowed")
    date_collected = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship(User, backref='user_obj')
    book = db.relationship(Books, backref='book_obj')

 

    def to_dict(self):
        return{
            "user_name":self.user_id,
            "book":self.user_book,
            "date_collected":self.date_collected ,
            "status":  self.status
        }
    

@app.route("/")
def home():
    return jsonify({"message":"welcome home"})

@app.route("/add_member",methods=["POST"])
def membership(): 
    user = request.get_json()
    username = User(user_name=user["user_name"])
    db.session.add(username)
    db.session.commit()
    return jsonify({"details":username.to_dict(),
                   "message":"this user has been sucessfully created"})


@app.route('/borrow',methods=["GET"])
def Borrow():
    user_input = request.get_json()
    if "user_name" in user_input:
            user = User.query.filter_by(user_name=user_input["user_name"]).first()
            if user:
                avaliable = Books.query.filter_by(book_name = user_input["book_name"]).first()
                if avaliable is not None:
                    avaliable.is_avaliable = False 
                    record = Records(user_id=user.id,user_book=avaliable.id)
                    db.session.add(record)
                    db.session.commit()
                    return jsonify({
                        "message":"you have sucessfully borrowed this book",
                        "boook name":avaliable.book_name,
                        "avaliable": avaliable.is_avaliable ,
                        "user details":user.to_dict(),
                        "testing":record.to_dict(),
                        "message":"PLEASE NOTE YOU HAVE A PERIOD OF 7 DAYS TO RETURN THID BOOK"
                        })
        
                else:
                    return jsonify({"message":"this book is not avalible right now "}),404
                
            else:
                return jsonify({"message":"this user does not exist",
                                }),404
    else:
         return jsonify({"message":"please input a username"})

    
@app.route('/return',methods=["GET"])
def Return():
     user_input = request.get_json()
     if "user_name" in user_input:
        user = User.query.filter_by(user_name=user_input["user_name"]).first()
        if user:
            book_returned = Books.query.filter_by(book_name=user_input["book_name"]).first()
            if book_returned:
                book_returned.is_avaliable = True
                record = Records(user_id=user.id,user_book=book_returned.id)
                record.status = "Returned"        
                db.session.add(record)
                db.session.commit()
                search_record = Records.query.filter_by(user_book=book_returned.id).first()


                borrowed_at = search_record.date_collected
                now = datetime.utcnow()
                days_held = (now - borrowed_at).days
                MAX_DAYS = 7

                overdue = days_held > MAX_DAYS
                return jsonify({"message":"thanks for returning the book",
                                " book_returned": book_returned.to_dict(),
                                "borrowed_at": borrowed_at.isoformat(),
                                "days_held": days_held,
                                "overdue": overdue,
                                "record":record.to_dict()})
            else:
                return jsonify({"message":"this book doesnt belong to us"})
        else:
            return jsonify({"message":"please input a username"})

    

@app.route("/add",methods=["POST"])
def create_books():
    new_book = request.get_json()
    if 'book_name' not in new_book :
        return jsonify({"message":"book name required"}),400
    
    if 'book_author' not in new_book :
        return jsonify({"message":"book author required"}),400
    
    book= Books(book_name=new_book["book_name"],book_author=new_book["book_author"])
    db.session.add(book)
    book.is_avaliable = True
    db.session.commit()
    return jsonify({
        "message":"this book has been sucessfully added",
        "book details":book.to_dict()
    })
   


@app.route("/search",methods=["GET"])
def search():
    #user_search is now a dictionary
    user_search = request.get_json()
    if "book_name" in user_search  and "book_author" in user_search:   
     book = Books.query.filter_by(book_name=user_search["book_name"],book_author= user_search["book_author"]).first()
    elif "book_name" in user_search:
        book = Books.query.filter_by(book_name=user_search["book_name"]).first()
    elif "book_author" in user_search:
         book = Books.query.filter_by(book_author= user_search["book_author"]).first()
    else: 
        return jsonify({
            "message":"please search by with book name or author"
        })
        
    if book and book.is_avaliable == True:
        return jsonify({
            "message": "this book is available",
            "book-details": book.to_dict()
        })
            
    else: 
        return jsonify({"message":"this book is not avaliable"})






         
         


    

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
