from flask import Flask, render_template, request
import matplotlib.pyplot as plt
import math
from io import BytesIO
import base64

app = Flask(__name__)

# Map each answer option to its scoring in the four categories.
# Keys: "Big-L", "small-l", "Big-C", "small-c"
options = {
    # Question 1: National politics
    "q1_a1": {"small-c": 1, "small-l": 0.5},
    "q1_a2": {"small-l": 1, "small-c": 0.5},
    "q1_a3": {"Big-L": 1, "Big-C": 0.5},
    "q1_a4": {"Big-C": 1},
    # Question 2: New campus architecture
    "q2_a1": {"small-l": 0.5},
    "q2_a2": {"Big-L": 1, "small-l": 0.5},
    "q2_a3": {"Big-C": 1},
    "q2_a4": {"small-c": 1},
    # Question 3: Eating Club mask mandates
    "q3_a1": {"Big-C": 1},
    "q3_a2": {"small-c": 2},
    "q3_a3": {"small-l": 1},
    "q3_a4": {"Big-L": 0.5},
}

@app.route("/", methods=["GET"])
def index():
    # Render the form to ask the questions.
    return render_template("index.html")

@app.route("/result", methods=["POST"])
def result():
    # Retrieve the selected answers from the form.
    q1 = request.form.get("q1")
    q2 = request.form.get("q2")
    q3 = request.form.get("q3")
    
    # Initialize scores for each category.
    score = {"Big-L": 0, "small-l": 0, "Big-C": 0, "small-c": 0}
    for answer in [q1, q2, q3]:
        if answer in options:
            for key, value in options[answer].items():
                score[key] += value

    # Define angles (in radians) for each category.
    angles = {
        "Big-L": math.radians(315),
        "small-c": math.radians(45),
        "Big-C": math.radians(135),
        "small-l": math.radians(225),
    }
    
    # Compute the overall (x, y) by summing each category's contribution.
    x_total = sum(score[k] * math.cos(angles[k]) for k in score)
    y_total = sum(score[k] * math.sin(angles[k]) for k in score)

    # Create the compass plot.
    fig, ax = plt.subplots(figsize=(6, 6))
    # Adjust limits if needed (here we use a wider range to see the user's dot clearly)
    ax.set_xlim(-5, 5)
    ax.set_ylim(-5, 5)
    ax.set_aspect('equal')

    # Draw a dashed circle as a reference.
    circle = plt.Circle((0, 0), 1, fill=False, linestyle='--', color='gray')
    ax.add_artist(circle)

    # Draw the four axes as arrows.
    arrow_data = [
        (315, "Big-L"),
        (45, "small-c"),
        (135, "Big-C"),
        (225, "small-l")
    ]
    for angle_deg, label in arrow_data:
        rad = math.radians(angle_deg)
        dx, dy = math.cos(rad), math.sin(rad)
        ax.arrow(0, 0, dx, dy, head_width=0.2, head_length=0.3, fc='k', ec='k')
        ax.text(1.2 * dx, 1.2 * dy, label, ha='center', va='center', fontsize=12)

    # Plot the user's score as a red dot.
    ax.plot(x_total, y_total, 'ro', markersize=10)
    ax.text(x_total, y_total, f" ({x_total:.1f}, {y_total:.1f})", color='red')

    plt.title("Campus Political Compass: Your Position")
    
    # Convert the plot to a PNG image and encode it in base64.
    buf = BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    image_data = base64.b64encode(buf.getvalue()).decode('utf-8')
    plt.close(fig)
    
    return render_template("result.html", image_data=image_data, score=score, x_total=x_total, y_total=y_total)

if __name__ == "__main__":
    app.run(debug=True)