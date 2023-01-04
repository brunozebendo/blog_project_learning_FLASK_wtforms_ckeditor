"""a intenção do exercício é criar novamente um site de um um blog, mas aprimorado das versões
anteriores, pois agora será possível criar, editar e deletar posts dentro do próprio site """
"""bibliotecas utilizadas, Flask, para trabalhar com sites no Python, render template para lidar com o html,
redirect e url_for para lidar com as rotas, bootstrap para lidar com o bootstrap e seus templates já 
pré construídos, sqlalchemy para lidar com banco de dados, wtf para lidar com formulários e suas validações,
já o CKEditor faz parte dos editores WYSIWYG (What You See Is What You Get - O que você vê é o que você obtém),
é um editor para sites, pelo que vi é um editor para sites que contém várias funções (presets) como autocomplete,
e mais um monte de funções que se vê normalmente em sites."""
from flask import Flask, render_template, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditor, CKEditorField
from datetime import date


## Delete this code:
# import requests
# posts = requests.get("https://api.npoint.io/43644ec4f0013682fc0d").json()

"""aqui o código de iniciação de cada biblioteca"""
app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
ckeditor = CKEditor(app)
Bootstrap(app)
"""a sintaxe para conectar ao DB"""
##CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
"""o código para a criação de cada item do banco de dados"""
##CONFIGURE TABLE
class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(250), nullable=False)
    img_url = db.Column(db.String(250), nullable=False)

"""o código para criação de cada item do site, do formulário do site"""


##WTForm
class CreatePostForm(FlaskForm):
    title = StringField("Blog Post Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle", validators=[DataRequired()])
    author = StringField("Your Name", validators=[DataRequired()])
    img_url = StringField("Blog Image URL", validators=[DataRequired(), URL()])

    # Notice body's StringField changed to CKEditorField
    body = CKEditorField("Blog Content", validators=[DataRequired()])
    submit = SubmitField("Submit Post")

"""a rota abaixo serve para adicionar um novo post ao banco de dados, por isso há uma função e dentro
a função CreatePostForm que eu ACHO que é uma função interna do Flask. Assim, se o formulário for
 validado, os campos do db são preenchidos com cada elemento e a rota é redirecionada. Olhar observação
 sobre o safe no post.html"""
@app.route("/new-post", methods=["GET", "POST"])
def add_new_post():
    form = CreatePostForm()
    if form.validate_on_submit():
        new_post = BlogPost(
            title=form.title.data,
            subtitle=form.subtitle.data,
            body=form.body.data,
            img_url=form.img_url.data,
            author=form.author.data,
            date=date.today().strftime("%B %d, %Y")
        )
        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for("get_all_posts"))
    return render_template("make-post.html", form=form)



"""criação da página inicial. O blog anterior puxava as informações de uma API, por isso as informações
comentadas acima. Já nesse, foi criado um banco inicial, o posts.db, então a variável posts guarda o resultado
da busca por todas as informação dentro do db e depois retorna no index.html"""
@app.route('/')
def get_all_posts():
    posts = BlogPost.query.all()
    return render_template("index.html", all_posts=posts)

"""aqui a rota para acessar o post de acordo com a sua id, já transformada em int e retornando o html 
no post.html"""
@app.route("/post/<int:post_id>")
def show_post(post_id):
    requested_post = BlogPost.query.get(post_id)
    return render_template("post.html", post=requested_post)

"""abaixo, o código para editar o post quando for clicado o botão de edit, onde o usuário 
vai um dar get request e post_id vai ser a identificação do post. Esse código trabalha junto com o do make-post.html,
 onde há uma distinção entre o edit e o create a new_post. Para que o formulário já esteja preenchido quando
  for clicado no botão de edit, foram reinformados os campos abaixo. Já if trata de quando o usuário 
  clica no botão de submit para postar a edição e assim o post deve ser atualizado no DB, contudo, 
  o HTML forms e o WTForms não aceita os métodos PUT, Patch ou DELETE. Então, enquanto isso seria
  normalmente um PUT request, substituindo a informação existente, como o request vem de um HTML form,
  ele deve aceito um POST request. Por fim, a data (date) deve ser mantida do post original"""

@app.route("/edit-post/<int:post_id>", methods=["GET", "POST"])
def edit_post(post_id):
    post = BlogPost.query.get(post_id)
    edit_form = CreatePostForm(
        title=post.title,
        subtitle=post.subtitle,
        img_url=post.img_url,
        author=post.author,
        body=post.body
    )
    if edit_form.validate_on_submit():
        post.title = edit_form.title.data
        post.subtitle = edit_form.subtitle.data
        post.img_url = edit_form.img_url.data
        post.author = edit_form.author.data
        post.body = edit_form.body.data
        db.session.commit()
        return redirect(url_for("show_post", post_id=post.id))
    return render_template("make-post.html", form=edit_form, is_edit=True)

"""aqui a rota para deletar um post que fica atrelada a um x no index.html que quando clicado
deleta o post no db e redireciona a rota"""

@app.route("/delete/<int:post_id>")
def delete_post(post_id):
    post_to_delete = BlogPost.query.get(post_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for('get_all_posts'))


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")




if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)

