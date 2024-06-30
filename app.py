from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from langchain_community.llms import HuggingFaceHub
from langchain_huggingface import HuggingFaceEndpoint
from langchain_core.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_core.output_parsers import StrOutputParser
import warnings
warnings.filterwarnings("ignore")

import os
os.environ['HUGGINGFACEHUB_API_TOKEN']   = "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"
prompt = PromptTemplate(
    input_variables=["message"],
    template="{message}"
)

llm = HuggingFaceHub(repo_id = "meta-llama/Meta-Llama-3-8B-Instruct")

chain = prompt | llm | StrOutputParser()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)



class Todo(db.Model):
    id = db.Column(db.Integer,primary_key = True)
    question = db.Column(db.String(200), nullable = False)
    answer = db.Column(db.String(200), nullable = False)
    date_created = db.Column(db.DateTime, default = datetime.now())

    def __repr__(self):
        return '<Task %r>' % self.id
    
with app.app_context():
    db.create_all()
    db.session.commit()        

@app.route('/', methods = ['POST', 'GET'])
def index():
    if request.method=='POST':
        question = request.form['Question']
        answer = chain.invoke({"message":question})
        answer = answer[len(question):]
        new_task = Todo(question = question, answer = answer)

        try:
            db.session.add(new_task)
            db.session.commit()
            return redirect('/')
        except:
            return 'There was a problem with LLM query'
    else:
        tasks = Todo.query.order_by(Todo.date_created).all()
        return render_template('index.html', tasks = tasks)

@app.route('/delete/<int:id>')
def delete(id):
    task_to_delete = Todo.query.get_or_404(id)
    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect('/')
    except:
        return 'problem deleting task'

if __name__ == "__main__":
    app.run(debug=True)