import matplotlib
matplotlib.use('Agg')  # Use a non-GUI backend to avoid Tkinter issues

from flask import Flask, render_template, request
import matplotlib.pyplot as plt
import math
from io import BytesIO
import base64

app = Flask(__name__)

# Mapping answer options for all 7 questions.
# Keys: "Big-L", "small-l", "Big-C", "small-c"
options = {
    # Q1: National politics
    "q1_a1": {"small-c": 1, "small-l": 0.5},
    "q1_a2": {"small-l": 1, "small-c": 0.5},
    "q1_a3": {"Big-L": 1, "Big-C": 0.5},
    "q1_a4": {"Big-C": 1},
    # Q2: New campus architecture
    "q2_a1": {"small-l": 0.5},
    "q2_a2": {"Big-L": 1, "small-l": 0.5},
    "q2_a3": {"Big-C": 1},
    "q2_a4": {"small-c": 1},
    # Q3: Eating Club mask mandates
    "q3_a1": {"Big-C": 1},
    "q3_a2": {"small-c": 1},  # updated from +2 to +1
    "q3_a3": {"small-l": 1},
    "q3_a4": {"Big-L": 0.5},
    # Q4: Professor on same-sex marriage
    "q4_a1": {"small-c": 1},
    "q4_a2": {"small-l": 1},
    "q4_a3": {"Big-C": 1},
    # Q5: Professor used a racial slur
    "q5_a1": {"Big-L": 1},
    "q5_a2": {"small-l": 1},
    "q5_a3": {"Big-C": 1},
    "q5_a4": {"small-c": 1},
    # Q6: Electric scooter ban
    "q6_a1": {"small-l": 0.5},
    "q6_a2": {"small-c": 1},
    "q6_a3": {"small-l": 1},
    # Q7: Primary source of campus news
    "q7_a1": {"Big-L": 1, "Big-C": 0.5},
    "q7_a2": {"small-l": 0.5},
    "q7_a3": {"small-c": 0.75},
    "q7_a4": {"small-c": 1},
    "q7_a5": {"Big-C": 1},
    "q7_a6": {"Big-L": 1},
}

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/result", methods=["POST"])
def result():
    # Retrieve the selected answers from the form.
    answers = []
    for q in ["q1", "q2", "q3", "q4", "q5", "q6", "q7"]:
        answer = request.form.get(q)
        if answer:
            answers.append(answer)

    # Initialize scores for each category.
    score = {"Big-L": 0, "small-l": 0, "Big-C": 0, "small-c": 0}
    for answer in answers:
        if answer in options:
            for key, value in options[answer].items():
                score[key] += value

    # Compute overall (x, y) using each faction’s contribution.
    angles = {
        "Big-L": math.radians(315),
        "small-c": math.radians(45),
        "Big-C": math.radians(135),
        "small-l": math.radians(225),
    }
    x_total = sum(score[k] * math.cos(angles[k]) for k in score)
    y_total = sum(score[k] * math.sin(angles[k]) for k in score)
    
    # Determine dominant faction.
    dominant_faction = max(score, key=score.get)

    # Dynamically set plot limits.
    margin = 2
    limit = max(5, margin + max(abs(x_total), abs(y_total)) * 1.2)
    
    # Create the compass plot.
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.set_xlim(-limit, limit)
    ax.set_ylim(-limit, limit)
    ax.set_aspect('equal')
    
    # Draw a dashed reference circle.
    circle_radius = limit * 0.2
    circle = plt.Circle((0, 0), circle_radius, fill=False, linestyle='--', color='gray')
    ax.add_artist(circle)
    
    # Draw the four arrows scaled to nearly fill the plot.
    arrow_length = limit - margin
    arrow_data = [
        (315, "Big-L"),
        (45, "small-c"),
        (135, "Big-C"),
        (225, "small-l")
    ]
    for angle_deg, label in arrow_data:
        rad = math.radians(angle_deg)
        dx, dy = arrow_length * math.cos(rad), arrow_length * math.sin(rad)
        ax.arrow(0, 0, dx, dy, head_width=limit*0.05, head_length=limit*0.08, fc='black', ec='black')
        ax.text((arrow_length + margin*0.3) * math.cos(rad),
                (arrow_length + margin*0.3) * math.sin(rad),
                label, ha='center', va='center', fontsize=12, fontweight='bold')
    
    # Plot the user's score as a red dot labeled "YOU".
    ax.plot(x_total, y_total, 'ro', markersize=10)
    ax.text(x_total, y_total, " YOU", color='red', fontsize=12, fontweight='bold')
    plt.title("Campus Political Compass: Your Position")
    
    # Convert plot to PNG and encode in base64.
    buf = BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    image_data = base64.b64encode(buf.getvalue()).decode('utf-8')
    plt.close(fig)
    
    return render_template("result.html", image_data=image_data, score=score,
                           x_total=x_total, y_total=y_total, dominant_faction=dominant_faction)

if __name__ == "__main__":
    app.run(debug=True)