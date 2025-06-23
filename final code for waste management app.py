import os
import logging
from flask import Flask, request, jsonify, render_template
from random import choice
from datetime import date

# Configure logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(_name_)
app.secret_key = os.environ.get("SESSION_SECRET", "eco-waste-management-secret-key")

# Recyclable waste types
recyclables = ['plastic', 'paper', 'metal', 'glass']
decompose_data = {
    "plastic": "Takes 500+ years to decompose",
    "paper": "Takes 2–6 weeks to decompose",
    "metal": "Takes 50–200 years to decompose",
    "glass": "Never decomposes naturally"
}

disposal_instructions = {
    "plastic": "Rinse and put in plastic recycle bin",
    "paper": "Tear and compost or recycle",
    "metal": "Send to metal recycling centers",
    "glass": "Wrap and place in glass bin"
}

eco_ideas = [
    "Switch off lights when not in use 🌿",
    "Use a reusable water bottle 💧",
    "Plant a tree this week 🌱",
    "Avoid fast fashion, choose sustainable clothes 👕",
    "Carry a cloth bag 🛍",
    "Walk or bike instead of driving 🚲",
    "Use both sides of paper 📄",
    "Unplug electronics when not in use ⚡",
    "Start composting organic waste 🍃",
    "Buy local and seasonal produce 🥕"
]

daily_challenges = {
    "2025-06-21": {"text": "Say no to plastic bags today!", "points": 15, "type": "action"},
    "2025-06-22": {"text": "Pick up 3 litter items around you!", "points": 20, "type": "cleanup"},
    "2025-06-23": {"text": "Use public transport or walk today!", "points": 25, "type": "transport"},
    "2025-06-24": {"text": "Recycle at least 3 items properly!", "points": 30, "type": "recycling"},
    "2025-06-25": {"text": "Start a small herb garden!", "points": 35, "type": "gardening"},
    "default": {"text": "Carry your own water bottle today!", "points": 10, "type": "action"}
}

# Weekly challenges for extra engagement
weekly_challenges = [
    {"title": "Plastic-Free Week", "description": "Avoid single-use plastics for 7 days", "points": 100},
    {"title": "Zero Waste Champion", "description": "Minimize waste generation this week", "points": 120},
    {"title": "Eco Explorer", "description": "Try 3 new sustainable practices", "points": 80},
    {"title": "Green Commuter", "description": "Use eco-friendly transport all week", "points": 90}
]

# Fun facts for educational gamification
eco_facts = [
    "🌍 One recycled plastic bottle saves enough energy to power a 60W light bulb for 6 hours!",
    "🌱 A single tree can absorb 48 pounds of CO2 per year!",
    "♻ Recycling one aluminum can saves enough energy to run a TV for 3 hours!",
    "🌊 It takes 1,000 years for a plastic bag to decompose in a landfill!",
    "🌳 Paper recycling reduces methane emissions from landfills by 1 ton per ton of paper!",
    "⚡ LED bulbs use 75% less energy than incandescent bulbs!",
    "🚲 Cycling just 10 miles a week saves 500 pounds of CO2 annually!"
]

@app.route('/')
def home():
    """Main page with daily challenge and eco tip"""
    today = str(date.today())
    challenge = daily_challenges.get(today, daily_challenges["default"])
    idea = choice(eco_ideas)
    weekly_challenge = choice(weekly_challenges)
    eco_fact = choice(eco_facts)
    return render_template('index.html', challenge=challenge, idea=idea, today=today, 
                         weekly_challenge=weekly_challenge, eco_fact=eco_fact)

@app.route('/scan', methods=['POST'])
def scan_waste():
    """API endpoint to check if waste is recyclable"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
            
        waste = data.get("waste", "").lower().strip()
        
        if not waste:
            return jsonify({"error": "Please enter a waste item"}), 400
        
        # Enhanced matching for better gamification
        base_points = 0
        recyclable = False
        
        # Check for exact matches first
        if waste in recyclables:
            recyclable = True
            base_points = 10
        else:
            # Check for partial matches to make it more engaging
            for recyclable_type in recyclables:
                if recyclable_type in waste or waste in recyclable_type:
                    recyclable = True
                    base_points = 10
                    waste = recyclable_type  # Use the standard type for data lookup
                    break
        
        if not recyclable:
            # Check for common non-recyclable items with specific feedback
            non_recyclable_items = {
                'battery': {'points': 3, 'disposal': 'Take to special battery recycling centers'},
                'electronics': {'points': 5, 'disposal': 'Take to e-waste recycling facilities'},
                'food': {'points': 2, 'disposal': 'Compost organic waste or dispose in food waste bin'},
                'fabric': {'points': 3, 'disposal': 'Donate to textile recycling or clothing donation centers'}
            }
            
            for item, info in non_recyclable_items.items():
                if item in waste:
                    return jsonify({
                        "result": f"Special disposal required ⚠",
                        "points": info['points'],
                        "decompose": "Varies by material",
                        "disposal": info['disposal'],
                        "recyclable": False
                    })
            
            # Default non-recyclable
            base_points = 2
            
        if recyclable:
            return jsonify({
                "result": "Recyclable ♻",
                "points": base_points,
                "decompose": decompose_data.get(waste, "Varies by material"),
                "disposal": disposal_instructions.get(waste, "Follow local recycling guidelines"),
                "recyclable": True
            })
        else:
            return jsonify({
                "result": "Non-recyclable ❌",
                "points": base_points,
                "decompose": "Unknown or too long",
                "disposal": "Try to avoid using this type of waste or find specialized disposal methods.",
                "recyclable": False
            })
    except Exception as e:
        app.logger.error(f"Error in scan_waste: {str(e)}")
        return jsonify({"error": "An error occurred while processing your request"}), 500

@app.route('/leaderboard')
def leaderboard():
    """Simple leaderboard page"""
    return render_template('leaderboard.html')

@app.route('/complete-challenge', methods=['POST'])
def complete_challenge():
    """API endpoint to complete daily challenge"""
    try:
        data = request.get_json()
        challenge_type = data.get('type', 'action')
        today = str(date.today())
        
        challenge_data = daily_challenges.get(today, daily_challenges["default"])
        bonus_points = challenge_data.get('points', 10)
        
        return jsonify({
            "success": True,
            "points": bonus_points,
            "message": f"Challenge completed! +{bonus_points} bonus points!",
            "challenge_type": challenge_type
        })
    except Exception as e:
        app.logger.error(f"Error completing challenge: {str(e)}")
        return jsonify({"error": "Failed to complete challenge"}), 500

@app.route('/spin-wheel', methods=['POST'])
def spin_wheel():
    """Lucky wheel for random rewards"""
    try:
        rewards = [
            {"type": "points", "value": 50, "message": "Lucky! +50 bonus points!"},
            {"type": "points", "value": 25, "message": "Great! +25 points!"},
            {"type": "points", "value": 75, "message": "Jackpot! +75 points!"},
            {"type": "fact", "value": choice(eco_facts), "message": "Learn something new!"},
            {"type": "challenge", "value": "Scan 3 more items for double points!", "message": "Special challenge unlocked!"},
            {"type": "points", "value": 100, "message": "MEGA BONUS! +100 points!"}
        ]
        
        reward = choice(rewards)
        return jsonify(reward)
    except Exception as e:
        app.logger.error(f"Error spinning wheel: {str(e)}")
        return jsonify({"error": "Wheel spin failed"}), 500

if _name_ == '_main_':
    app.run(host='0.0.0.0', port=5000, debug=True)