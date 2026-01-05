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
    date_collected = db.Column(db.DateTime, default=datetime.now())

@app.route("/")
def home():
    return jsonify({"message":"welcome home"})

@app.route("/add",methods=["POST"])
def create_books():
    new_book = request.get_json()
    book= Books(book_name=new_book["book_name"],book_author=new_book["book_author"])
    if book:
        db.session.add(book)
        book.is_avaliable = True
        db.session.commit()
        return jsonify({
            "message":"this book has been sucessfully added",
            "book details":book.to_dict(),
            

        })
    else:
        return jsonify({"message":"please enter a valid input"})





@app.route("/search",methods=["GET"])
def search():
    #user_search is now a dictionary
    user_search = request.get_json()
    book = Books.query.filter_by(book_name=user_search["book_name"],book_author= user_search["book_author"]).first()
    if book and book.is_avaliable == True:
        return jsonify({
            "message": "this book is available",
            "book-details": book.to_dict()
        })
            
    else: 
        return jsonify({"message":"this book is not avaliable"})
    

@app.route('/borrow',methods=["GET"])
def Borrow():
    #user_input is now a dictionary
    user_input = request.get_json()
    avaliable = Books.query.filter_by(book_name = user_input["book_name"]).first()
    if avaliable is not None:
        avaliable.is_avaliable = False
        db.session.commit()
        return jsonify({
            "message":"you have sucessfully borrowed this book",
            "boook name":avaliable.book_name,
            "avaliable": avaliable.is_avaliable 
            })
    
    # if avaliable.is_avaliable == False:
    #      print("just checking")
    #      return jsonify({"message":"this book is not avalible right now"})


    else:
        return jsonify({"message":"this book is not avalible right now "}),404

@app.route('/return',methods=["GET"])
def Return():
     user_input = request.get_json()
    #  auth_user = User.query.filter_by(user_name=user_input["user_name"])
     book_returned = Books.query.filter_by(book_name=user_input["book_name"]).first()
     if book_returned:
         book_returned.is_avaliable = True
         db.session.commit()
         return jsonify({"message":"thanks for returning the book"})
     else:
           return jsonify({"message":"this book doesnt belong to us"})
         
         


    

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
