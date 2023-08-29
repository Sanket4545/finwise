from flask import Flask, render_template, url_for, request, redirect, session
import mysql.connector
import matplotlib.pyplot as plt
import pandas as pd
import io
import base64

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/login')
def login():
    return render_template('login.html')


# Replace with your MySQL connection details
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Dreams@2024',
    'database': 'login_info'
}

conn = mysql.connector.connect(**db_config)
cursor = conn.cursor()

# @app.route('/')
# def login_page():
#     return render_template('login.html')

user1=[]
@app.route('/logged', methods=['POST'])
def logged():
    username = request.form['username']
    passward = request.form['passward']
    
    query = "SELECT * FROM users WHERE username = %s AND passward = %s"
    cursor.execute(query, (username, passward))
    user = cursor.fetchone()
    
    if user:
        # Successful login logic
        user1.append(user[0])
        return render_template('dashboard.html')
    else:
        return "Login Failed"

@app.route('/registerd', methods=['GET', 'POST'])
def registerd():
    if request.method == 'POST':
        username = request.form['username']
        passward = request.form['passward']
        
        # Check if username already exists
        check_query = "SELECT * FROM users WHERE username = %s"
        cursor.execute(check_query, (username,))
        existing_user = cursor.fetchone()
        
        if existing_user:
            return "Username already exists"
        else:
            insert_query = "INSERT INTO users (username, passward) VALUES (%s, %s)"
            cursor.execute(insert_query, (username, passward))
            conn.commit()
            return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/logout')
def logout():
    return render_template('home.html')

# @app.route('/dashboard')
# def dashboard():
#     return "your dashboard"

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():

    amount=request.form['amount']
    tags=request.form['tags']
    Date=request.form['Date']
    if len(user1)>0:
        user_id=int(user1[0])


        insert_query = "INSERT INTO transactions (user_id, amount, tags, Date) VALUES (%s,%s, %s, %s)"
        cursor.execute(insert_query, (user_id,amount, tags, Date))
        conn.commit()

        message="Transaction is added sucessfully"
        return render_template('dashboard.html', message=message)
    else:
        message_logout="Please Login again..."
        return render_template('login.html', message_logout=message_logout)

@app.route('/dashboard2', methods=['GET', 'POST'])  # New route for filtered dashboard
def dashboard2():
    filter_type = request.form['filter']

    # # SQL query based on filter type
    
    if filter_type == 'daily':
        query = "SELECT DATE(Date) AS Date, SUM(amount) AS TotalAmount FROM transactions where user_id=1 GROUP BY DATE(Date)"
    elif filter_type == 'weekly':
        query = "SELECT YEARWEEK(Date) AS Week, SUM(amount) AS TotalAmount FROM transactions GROUP BY YEARWEEK(Date)"
    elif filter_type == 'monthly':
        query = "SELECT MONTH(Date) AS Month, SUM(amount) AS TotalAmount FROM transactions GROUP BY MONTH(Date)"
    elif filter_type == 'yearly':
        query = "SELECT YEAR(Date) AS Year, SUM(amount) AS TotalAmount FROM transactions GROUP BY YEAR(Date)"
    elif filter_type == 'tags':
        query = "SELECT tags AS tags, SUM(amount) AS TotalAmount FROM transactions GROUP BY tags"
    
    else:
        return "Invalid filter"
    
    cursor.execute(query)
    data = cursor.fetchall()
    column_names = [desc[0] for desc in cursor.description]

    
    df = pd.DataFrame(data, columns=column_names)
    # if not df.empty:
    #     df_html = df.to_html()  # Convert DataFrame to HTML
    #     return df_html
    
    # Generate chart
    plt.figure(figsize=(8, 4))
    if filter_type == 'daily':
        plt.bar(df['Date'], df['TotalAmount'])
        plt.xlabel('Date')
        plt.xticks(rotation=45)
    elif filter_type == 'weekly':
        plt.plot(df['Week'], df['TotalAmount'])
        plt.xlabel('Week')
    elif filter_type == 'monthly':
        plt.plot(df['Month'], df['TotalAmount'])
        plt.xlabel('Month')
    elif filter_type == 'yearly':
        plt.plot(df['Year'], df['TotalAmount'])
        plt.xlabel('Year')
    elif filter_type == 'tags':
        plt.bar(df['tags'], df['TotalAmount'])
        plt.xlabel('Categories')
    
    plt.ylabel('Total Amount')
    plt.title(f'{filter_type.capitalize()} Chart')
    
    # Convert chart to base64 for embedding in HTML
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    plt.close()
    buffer.seek(0)
    img_base64 = base64.b64encode(buffer.read()).decode()
    
    return render_template('charts.html', img_base64=img_base64)

    
    
# ... (existing code) ...



if __name__ == '__main__':
    app.run(debug=True)
