import json
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.template import RequestContext
import pymysql
from datetime import date
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
import random
from django.http import JsonResponse
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.contrib.auth import authenticate, login
from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse
from django.contrib.auth.decorators import login_required


#========== Model ML Libries ===========#
import os
import cv2
import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator # type: ignore
from tensorflow.keras.models import Model # type: ignore
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D # type: ignore
from tensorflow.keras.applications import MobileNetV2 # type: ignore
from tensorflow.keras.optimizers import Adam # type: ignore
from tensorflow.keras.models import load_model # type: ignore
from tensorflow.keras.preprocessing.image import ImageDataGenerator # type: ignore
import re





#database Connection
import pymysql


mydb=pymysql.connect(host="localhost",user="root",password="root",database="food_calories_prediction")

def index(request):
    return render(request,"index.html")



#============ Model Code Starts ===========#

# Load Food Dataset and Nutrition CSV
foodimg_dir = 'D:\\code\\code\\Recommendationsystem\\dataset\\Indian Food Images'
nutrition_data = pd.read_csv('D:\\code\\code\\Recommendationsystem\\dataset\\new_cal.csv')

# Ensure column names are clean
nutrition_data.columns = nutrition_data.columns.str.strip()

# Load the model
model = load_model('D:\\code\\code\\Recommendationsystem\\models\\NutriTrack4545.h5')

# Preprocess images (resize and normalize)
def preprocess_image(img_path, img_size=(224, 224)):
    img = cv2.imread(img_path)
    img = cv2.resize(img, img_size)
    img = img / 255.0  # Normalize to [0, 1]
    return img


# Reinitialize train_datagen
train_datagen = ImageDataGenerator(rescale=1./255)

# Load training data again
train_data = train_datagen.flow_from_directory(
    'D:\\code\\code\\Recommendationsystem\\dataset\\Indian Food Images\\Train',  # Change this to your actual training dataset path
    target_size=(224, 224),  
    batch_size=32,  
    class_mode='categorical'
)

# Now you can access class indices
food_label = train_data.class_indices


# Ensure this is defined before using in test_model
train_data = train_datagen.flow_from_directory('D:\\code\\code\\Recommendationsystem\\dataset\\Indian Food Images\\Train', target_size=(224, 224), batch_size=32, class_mode='categorical')

food_label = train_data.class_indices


# Match food label to calories



def extract_number(value):
    """Extracts the first number from strings like '250 (1 cup)' or '10g'"""
    if isinstance(value, (int, float)):
        return float(value)
    if pd.isna(value):  # Handle NaN/None if using pandas
        return 0.0
    match = re.search(r'\d+\.?\d*', str(value))  # Finds numbers with decimals
    return float(match.group()) if match else 0.0





def get_nutrition(food_item):
    # Find the row matching the food_item
   # nutrition_row = nutrition_data[nutrition_data['Food Item'].str.lower() == food_item.lower()]
    # Get data for the food item or use defaults if not found
    matches = nutrition_data[
        nutrition_data['Food Item'].str.lower().str.replace(r'[^\w\s]', '', regex=True) == food_item
    ]
    
    if not matches.empty:
        return {
            'quantity': str(matches['Quantity'].values[0]),  # Add this line
            'calories': extract_number(matches['Calories'].values[0]),
            'protein': extract_number(matches['Proteins'].values[0]),
            'carbs': extract_number(matches['Carbs'].values[0])
        }
    return {'quantity': '1 serving', 'calories': 0, 'protein': 0, 'carbs': 0}



# Test the model on a sample image
def test_model(test_image_path):
    img = preprocess_image(test_image_path)
    img = np.expand_dims(img, axis=0)  # Add batch dimension
    
    prediction = model.predict(img)
    print(f"Raw Prediction: {prediction}")

    # Get the predicted class
    food_label = train_data.class_indices
    predicted_food = list(food_label.keys())[np.argmax(prediction)]

    # Get all nutrition info from dataset
    nutrition_info = get_nutrition(predicted_food)

    print(f'Predicted food: {predicted_food}, Nutrition: {nutrition_info}')
    
    return {
        'food_item': str(predicted_food),
        'quantity': str(nutrition_info['quantity']),  # Add this line
        'calories': float(nutrition_info['calories']),
        'protein': float(nutrition_info['protein']),
        'carbs': float(nutrition_info['carbs'])
    }


#============ Model Code Ends ===========#


def about(request):
    return render(request, "about.html")

def team(request):
    return render(request, "team.html")

def registration(request):
    return render(request, 'registration.html')

def Reg(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        contact = request.POST.get('contact')
        password = request.POST.get('password')
        sql = "INSERT INTO registration(name,email,contact,password) VALUES (%s,%s,%s,%s)"
        values = (name, email, contact, password)
        cur = mydb.cursor()
        cur.execute(sql, values)
        mydb.commit()
        
        return render(request, "login.html") 

def login(request):
    return render(request, "login.html")
    


# def dologin(request):
#     if request.method == "POST":
#         user_email = request.POST.get("email")
#         passw = request.POST.get("password")

#         # Check login credentials
#         c1 = mydb.cursor()
#         sql = "SELECT * FROM registration WHERE email = %s AND password = %s;"
#         c1.execute(sql, (user_email, passw))
#         user = c1.fetchone()

#         if user:
#             request.session["id"] = user[0]
#             request.session["email"] = user_email
            
#             # Check if profile exists and is complete
#             c2 = mydb.cursor()
#             profile_sql = """
#                 SELECT age, height, weight, gender, activity 
#                 FROM user_profile 
#                 WHERE email = %s
#             """
#             c2.execute(profile_sql, (user_email,))
#             profile = c2.fetchone()
            
#             if profile and all(profile):  # Check if all profile fields are filled
#                 return redirect("user_dashboard")
#             else:
#                 return redirect("update_profile")
#         else:
#             return render(request, "invalid.html")

#     return HttpResponse("Invalid request method", status=400)






from django.shortcuts import render, redirect
from django.http import HttpResponse
from datetime import datetime, timedelta

# def dologin(request):
#     if request.method == "POST":
#         user_email = request.POST.get("email")
#         passw = request.POST.get("password")
        
#         # Check if user is temporarily locked out
#         if 'login_attempts' in request.session:
#             last_attempt_time = request.session.get('last_attempt_time')
#             if last_attempt_time:
#                 last_attempt_time = datetime.strptime(last_attempt_time, "%Y-%m-%d %H:%M:%S")
#                 if datetime.now() - last_attempt_time < timedelta(minutes=10):
#                     if request.session['login_attempts'] >= 3:
#                         return render(request, "login.html", {
#                             'error': "Too many failed attempts. Please try again after 10 minutes.",
#                             'email_value': user_email,  # Preserve the email in the form
#                             'disabled': True  # Add this to your template to disable fields
#                         })

#         # Check login credentials
#         c1 = mydb.cursor()
#         sql = "SELECT * FROM registration WHERE email = %s AND password = %s;"
#         c1.execute(sql, (user_email, passw))
#         user = c1.fetchone()

#         if user:
#             # Reset attempt counter on successful login
#             if 'login_attempts' in request.session:
#                 del request.session['login_attempts']
#                 if 'last_attempt_time' in request.session:
#                     del request.session['last_attempt_time']
            
#             request.session["id"] = user[0]
#             request.session["email"] = user_email
            
#             # Check if profile exists and is complete
#             c2 = mydb.cursor()
#             profile_sql = """
#                 SELECT age, height, weight, gender, activity 
#                 FROM user_profile 
#                 WHERE email = %s
#             """
#             c2.execute(profile_sql, (user_email,))
#             profile = c2.fetchone()
            
#             if profile and all(profile):
#                 return redirect("user_dashboard")
#             else:
#                 return redirect("update_profile")
#         else:
#             # Increment attempt counter
#             request.session['login_attempts'] = request.session.get('login_attempts', 0) + 1
#             request.session['last_attempt_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
#             attempts_remaining = 3 - request.session['login_attempts']
            
#             if attempts_remaining <= 0:
#                 error_msg = "Too many failed attempts. Please try again after 10 minutes."
#             else:
#                 error_msg = f"Wrong password. {attempts_remaining} attempts remaining."
            
#             return render(request, "login.html", {
#                 'error': error_msg,
#                 'email_value': user_email,  # Preserve the email in the form
#                 'disabled': attempts_remaining <= 0  # Disable fields if locked out
#             })

#     return redirect('login_page')  # Assuming you have a URL named 'login_page'


def dologin(request):
    if request.method == "POST":
        user_email = request.POST.get("email")
        passw = request.POST.get("password")

        # Check login credentials
        c1 = mydb.cursor()
        sql = "SELECT * FROM registration WHERE email = %s AND password = %s;"
        c1.execute(sql, (user_email, passw))
        user = c1.fetchone()

        if user:
            request.session["id"] = user[0]
            request.session["email"] = user_email
            
            # Check if profile exists and is complete
            c2 = mydb.cursor()
            profile_sql = """
                SELECT age, height, weight, gender, activity 
                FROM user_profile 
                WHERE email = %s
            """
            c2.execute(profile_sql, (user_email,))
            profile = c2.fetchone()
            
            if profile and all(profile):  # Check if all profile fields are filled
                return redirect("user_dashboard")
            else:
                return redirect("update_profile")
        else:
            return render(request, "invalid.html")

    return HttpResponse("Invalid request method", status=400)




def update_profile(request):
    # Get email from session first (works for both GET and POST requests)
    email = request.session.get('email')

    if not email:
        return redirect('login')
    
    if request.method == "POST":
        # Get user inputs from the form
        age = int(request.POST.get("age"))
        height = int(request.POST.get("height"))
        weight = int(request.POST.get("weight"))
        gender = request.POST.get("gender")
        activity = request.POST.get("activity")

        # Calculate daily calorie intake
        if gender == "male":
            calories = 88.36 + (13.4 * weight) + (4.8 * height) - (5.7 * age)
        else:
            calories = 447.6 + (9.2 * weight) + (3.1 * height) - (4.3 * age)

        # Apply activity multiplier
        activity_multiplier = {
            "sedentary": 1.2,
            "light": 1.375,
            "moderate": 1.55,
            "active": 1.725
        }
        calories *= activity_multiplier.get(activity.lower(), 1.2)
        calories = round(calories)

        # Store user data in database
        sql = """
            INSERT INTO user_profile (email, age, height, weight, gender, activity, daily_calories)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                age = VALUES(age),
                height = VALUES(height),
                weight = VALUES(weight),
                gender = VALUES(gender),
                activity = VALUES(activity),
                daily_calories = VALUES(daily_calories)
        """
        values = (email, age, height, weight, gender, activity, calories)
        cur = mydb.cursor()
        cur.execute(sql, values)
        mydb.commit()

        # Optional: store in session as well
        request.session["user_info"] = {
            "email": email,
            "age": age,
            "height": height,
            "weight": weight,
            "gender": gender,
            "activity": activity,
            "daily_calories": calories
        }

        return redirect("user_dashboard")

    # GET request - render form with email
    return render(request, "update_profile.html", {'email': email})









def user_dashboard(request):
    email = request.session.get('email')
    if not email:
        return redirect('login')

    # Get user profile
    cur = mydb.cursor()
     
    cur.execute("""
        SELECT name, email FROM registration WHERE email = %s
    """, (email,))
    user_basic_info = cur.fetchone()

    cur.execute("""
        SELECT age, height, weight, gender, activity, daily_calories 
        FROM user_profile 
        WHERE email = %s
    """, (email,))
    profile = cur.fetchone()
    
    # Calculate today's consumed calories
    cur.execute("""
        SELECT SUM(f.calories * m.serving_size) 
        FROM user_meals m
        JOIN food_items f ON m.food_id = f.food_id
        WHERE m.user_email = %s AND m.date = CURDATE()
    """, (email,))
    consumed = cur.fetchone()[0] or 0
    
    daily_goal = profile[5] if profile else 2000
    remaining = max(0, daily_goal - consumed)
    
    # Get recommendations (only if remaining calories > 0)
    recommendations = []
    if remaining > 0:
        cur.execute("""
            SELECT name, calories, protein, carbs, food_id
            FROM food_items
            WHERE calories BETWEEN %s AND %s
            ORDER BY ABS(calories - %s)
            LIMIT 3
        """, (remaining*0.7, remaining*1.3, remaining))
        recommendations = cur.fetchall()
    
    return render(request, 'dashboard.html', {
        'user_basic_info': {
            'name': user_basic_info[0] if user_basic_info else '',
            'email': user_basic_info[1] if user_basic_info else email
        },


        'user_info': {
            'age': profile[0] if profile else '',
            'height': profile[1] if profile else '',
            'weight': profile[2] if profile else '',
            'gender': profile[3] if profile else '',
            'activity': profile[4] if profile else '',
            'daily_calories': daily_goal
        },
        'consumed_calories': consumed,
        'remaining_calories': remaining,
        'recommendations': recommendations
    })



def log_meal(request):
    if request.method == "POST":
        email = request.session.get('email')
        if not email:
            return JsonResponse({'status': 'error', 'message': 'Not logged in'}, status=401)
            
        data = json.loads(request.body)
        
        try:
            cur = mydb.cursor()
            cur.execute("""
                INSERT INTO user_meals 
                (user_email, food_id, date, meal_type)
                VALUES (%s, %s, CURDATE(), %s)
            """, (email, data['food_id'], data['meal_type']))
            mydb.commit()
            
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    
    return JsonResponse({'status': 'error'}, status=405)





def edit_profile(request):
    email = request.session.get('email')
    if not email:
        return redirect('login')

    if request.method == "POST":
        try:
            # Get updated values from form
            age = int(request.POST.get("age"))
            height = int(request.POST.get("height"))
            weight = int(request.POST.get("weight"))
            gender = request.POST.get("gender")
            activity = request.POST.get("activity").lower()

            # Update database
            cur = mydb.cursor()
            sql = """
                UPDATE user_profile 
                SET age=%s, height=%s, weight=%s, gender=%s, activity=%s 
                WHERE email=%s
            """
            cur.execute(sql, (age, height, weight, gender, activity, email))
            mydb.commit()

            # Update session data
            request.session['user_info'] = {
                'email': email,
                'age': age,
                'height': height,
                'weight': weight,
                'gender': gender,
                'activity': activity
            }
            request.session.modified = True

            return redirect('dashboard')

        except Exception as e:
            # Handle any errors and show the form again with submitted values
            return render(request, "edit_profile.html", {
                'error': str(e),
                'user_info': {
                    'email': email,
                    'age': request.POST.get('age'),
                    'height': request.POST.get('height'),
                    'weight': request.POST.get('weight'),
                    'gender': request.POST.get('gender'),
                    'activity': request.POST.get('activity')
                }
            })

    # GET request handling
    cur = mydb.cursor()
    cur.execute("SELECT age, height, weight, gender, activity FROM user_profile WHERE email = %s", (email,))
    profile = cur.fetchone()
    
    print(f"Database results: {profile}")  # Debug 2
    
    context = {
        'email': email,
        'age': profile[0] if profile else 'DEBUG_NO_AGE',
        'height': profile[1] if profile else 'DEBUG_NO_HEIGHT',
        'weight': profile[2] if profile else 'DEBUG_NO_WEIGHT',
        'gender': profile[3] if profile else 'male',
        'activity': profile[4] if profile else 'sedentary'
    }
    
    print(f"Template context: {context}")  # Debug 3
    return render(request, "edit_profile.html", context)






def upload_food_image(request):
    if request.method == "POST" and request.FILES.get("food_image"):
        try:
            image = request.FILES["food_image"]
            image_path = default_storage.save(f"uploads/{image.name}", ContentFile(image.read()))
            absolute_path = default_storage.path(image_path)

            if os.path.exists(absolute_path):
                nutrition_data = test_model(absolute_path)
                
                return JsonResponse({
                    "success": True, 
                    "image_url": default_storage.url(image_path),
                    "quantity": nutrition_data['quantity'],
                    "food_item": nutrition_data['food_item'],
                    "calories": nutrition_data['calories'],
                    "protein": nutrition_data['protein'],
                    "carbs": nutrition_data['carbs']
                })
            else:
                return JsonResponse({"success": False, "error": "File not saved correctly"})
        
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

    return JsonResponse({"success": False, "error": "Invalid request"})




def logout(request):
    return render(request, "index.html")
