from flask import Flask, request, jsonify, render_template, redirect, session
from flask_cors import CORS
from datetime import datetime, timedelta
import json
import os

# File to store events persistently
EVENTS_FILE = 'events_data.json'

# Global variables for data storage
events = []
engagement_data = {}  # Store engagement data per event
tickets_data = {}     # Store ticket sales per event

# Load events from file
def load_events():
    if os.path.exists(EVENTS_FILE):
        try:
            with open(EVENTS_FILE, 'r') as f:
                return json.load(f)
        except:
            return []
    return []

# Save events to file
def save_events(events_data):
    with open(EVENTS_FILE, 'w') as f:
        json.dump(events_data, f, indent=2)

# In-memory storage for ticket bookings (in production, use a database)
ticket_bookings = []
live_sales_data = {
    'total_sales': 0,
    'total_revenue': 0,
    'recent_bookings': []
}

app = Flask(__name__, template_folder='../templates', static_folder='../static')
app.secret_key = 'your-secret-key-here'  # Change this in production
CORS(app)

# Load events data
events = load_events()

# If no events exist, create some sample data
if not events:
    events = [
        {
            'id': 1,
            'title': 'Tech Conference 2024',
            'description': 'Annual technology conference featuring the latest innovations',
            'date': '2024-03-15',
            'time': '09:00',
            'location': 'Convention Center, Jakarta',
            'capacity': 500,
            'ticketPrice': 250000,
            'currency': 'INR',
            'image': '/static/images/tech-conference.jpg',
            'attendees': 0,
            'status': 'upcoming',
            'created_at': datetime.now().isoformat()
        },
        {
            'id': 2,
            'title': 'Music Festival',
            'description': 'Three-day music festival with international artists',
            'date': '2024-04-20',
            'time': '18:00',
            'location': 'City Park, Jakarta',
            'capacity': 1000,
            'ticketPrice': 450000,
            'currency': 'INR',
            'image': '/static/images/music-festival.jpg',
            'attendees': 0,
            'status': 'upcoming',
            'created_at': datetime.now().isoformat()
        }
    ]
    save_events(events)

@app.route('/', methods=['GET'])
def home():
    """Serve the home page with login"""
    return render_template('home.html')

@app.route('/login', methods=['POST'])
def login():
    """Handle login authentication"""
    data = request.get_json()
    
    # Simple authentication (replace with real authentication in production)
    # Accept multiple valid credentials for testing
    valid_credentials = [
        {'email': 'admin@eventpro.com', 'password': 'admin123'},
        {'email': 'admin@gmail.com', 'password': 'admin'},
        {'email': 'test@test.com', 'password': 'test123'},
        {'email': 'demo@demo.com', 'password': 'demo'}
    ]
    
    user_email = data.get('email', '').lower()
    user_password = data.get('password', '')
    
    # Check if credentials match any valid combination
    for creds in valid_credentials:
        if user_email == creds['email'].lower() and user_password == creds['password']:
            session['logged_in'] = True
            session['user_email'] = user_email
            return jsonify({'success': True})
    
    return jsonify({'success': False, 'message': 'Invalid credentials'}), 401

@app.route('/dashboard')
def dashboard():
    """Redirect dashboard to events page"""
    return redirect('/events')

@app.route('/events')
def events_list():
    """Events list page"""
    return render_template('events.html', events=events)

@app.route('/profile')
def profile():
    """Profile page"""
    return render_template('profile.html')

@app.route('/logout')
def logout():
    """Logout and redirect to home"""
    session.clear()
    return redirect('/')

@app.route('/events/<int:event_id>/pre-event')
def event_pre_analytics(event_id):
    """Pre-event analytics page"""
    event = next((e for e in events if e['id'] == event_id), None)
    if not event:
        return redirect('/events')
    
    return render_template('event_pre_analytics.html', 
                         event_id=event_id, 
                         event_title=event['title'],
                         event_status=event['status'],
                         event=event)

@app.route('/events/<int:event_id>/engagement')
def event_engagement_analytics(event_id):
    """Event engagement analytics page"""
    event = next((e for e in events if e['id'] == event_id), None)
    if not event:
        return redirect('/events')
    
    return render_template('event_engagement.html', 
                         event_id=event_id, 
                         event_title=event['title'],
                         event_status=event['status'],
                         event=event)

@app.route('/events/<int:event_id>/post-event')
def event_post_analytics(event_id):
    """Post-event analytics page"""
    event = next((e for e in events if e['id'] == event_id), None)
    if not event:
        return redirect('/events')
    
    return render_template('event_post_analytics.html', 
                         event_id=event_id, 
                         event_title=event['title'],
                         event_status=event['status'],
                         event=event)

@app.route('/api/book-ticket', methods=['POST'])
def book_ticket():
    """API endpoint for booking tickets"""
    try:
        data = request.get_json()
        
        booking = {
            'id': len(ticket_bookings) + 1,
            'event_id': data.get('event_id'),
            'attendee_name': data.get('attendee_name'),
            'attendee_email': data.get('attendee_email'),
            'ticket_price': data.get('ticket_price', 250000),
            'currency': data.get('currency', 'INR'),
            'booking_time': datetime.now().isoformat(),
            'status': 'confirmed'
        }
        
        ticket_bookings.append(booking)
        
        # Update live sales data
        live_sales_data['total_sales'] += 1
        live_sales_data['total_revenue'] += booking['ticket_price']
        live_sales_data['recent_bookings'].insert(0, booking)
        
        # Keep only last 10 recent bookings
        if len(live_sales_data['recent_bookings']) > 10:
            live_sales_data['recent_bookings'] = live_sales_data['recent_bookings'][:10]
        
        return jsonify({'success': True, 'booking_id': booking['id']})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/create-event', methods=['POST'])
def create_event_api():
    """Create a new event"""
    try:
        data = request.get_json()
        
        # Generate new event ID
        new_id = max([e['id'] for e in events], default=0) + 1
        
        new_event = {
            'id': new_id,
            'title': data.get('title'),
            'description': data.get('description'),
            'date': data.get('date'),
            'time': data.get('time'),
            'location': data.get('location'),
            'capacity': int(data.get('capacity', 0)),
            'ticketPrice': int(data.get('ticketPrice', 0)),
            'currency': data.get('currency', 'INR'),
            'image': data.get('image', '/static/images/default-event.jpg'),
            'attendees': 0,
            'status': 'upcoming',
            'created_at': datetime.now().isoformat()
        }
        
        events.append(new_event)
        save_events(events)
        
        return jsonify({'success': True, 'event_id': new_id})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/live-sales')
def get_live_sales():
    """Get live sales data"""
    return jsonify(live_sales_data)

@app.route('/api/export-bookings')
def export_bookings():
    """Export booking data as CSV"""
    import csv
    import io
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(['Booking ID', 'Event ID', 'Attendee Name', 'Email', 'Ticket Price', 'Currency', 'Booking Time', 'Status'])
    
    # Write data
    for booking in ticket_bookings:
        writer.writerow([
            booking['id'],
            booking['event_id'],
            booking['attendee_name'],
            booking['attendee_email'],
            booking['ticket_price'],
            booking['currency'],
            booking['booking_time'],
            booking['status']
        ])
    
    output.seek(0)
    csv_data = output.getvalue()
    
    from flask import Response
    return Response(
        csv_data,
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=ticket_bookings.csv'}
    )

@app.route('/create-event')
def create_event():
    """Event creation page"""
    return render_template('create-event.html')

# Sample data initialization for analytics
analytics_data = {
    'revenue': {
        'total': 7852000,
        'change': 8.1,
        'weekly_data': [
            {'day': 'Mon', 'sales': 45, 'revenue': 2300000},
            {'day': 'Tue', 'sales': 32, 'revenue': 1800000},
            {'day': 'Wed', 'sales': 68, 'revenue': 3200000},
            {'day': 'Thu', 'sales': 55, 'revenue': 2900000},
            {'day': 'Fri', 'sales': 89, 'revenue': 4100000},
            {'day': 'Sat', 'sales': 120, 'revenue': 5800000},
            {'day': 'Sun', 'sales': 95, 'revenue': 4500000}
        ]
    },
    'engagement': {
        'live_attendance': 240,
        'active_polls': 3,
        'qa_questions': 47,
        'breakdown': [
            {'name': 'Poll Participation', 'value': 40},
            {'name': 'Q&A Sessions', 'value': 32},
            {'name': 'Survey Responses', 'value': 28}
        ]
    }
}

feedback_data = {
    'total_responses': 2568,
    'avg_rating': 4.6,
    'response_rate': 89,
    'nps': 67,
    'ratings': [
        {'category': 'Overall Satisfaction', 'rating': 85},
        {'category': 'Content Quality', 'rating': 92},
        {'category': 'Organization', 'rating': 78},
        {'category': 'Venue Quality', 'rating': 88}
    ],
    'sentiment': {'positive': 68, 'neutral': 22, 'negative': 10},
    'comments': [
        {
            'rating': 5,
            'comment': 'Excellent conference! Very informative.',
            'attendee': 'Sarah Johnson',
            'session': 'Tech Panel Discussion'
        }
    ]
}

@app.route('/api/dashboard', methods=['GET'])
def get_dashboard_stats():
    """Get dashboard overview statistics"""
    total_events = len(events)
    total_revenue = sum(event.get('ticketPrice', 0) * event.get('attendees', 0) for event in events)
    total_attendees = sum(event.get('attendees', 0) for event in events)
    avg_rating = feedback_data.get('avg_rating', 4.6)
    
    return jsonify({
        'stats': {
            'total_events': total_events,
            'total_revenue': total_revenue,
            'total_attendees': total_attendees,
            'avg_rating': avg_rating
        },
        'recent_events': events[-4:],  # Last 4 events
        'revenue_trend': analytics_data['revenue']['weekly_data']
    })

@app.route('/api/events', methods=['GET'])
def get_events():
    """Get all events"""
    return jsonify({'events': events})

@app.route('/api/analytics/revenue', methods=['GET'])
def get_revenue_analytics():
    """Get revenue and ticket sales analytics"""
    return jsonify(analytics_data['revenue'])

@app.route('/api/analytics/engagement', methods=['GET'])
def get_engagement_analytics():
    """Get engagement metrics"""
    return jsonify(analytics_data['engagement'])

@app.route('/api/feedback', methods=['GET'])
def get_feedback_analytics():
    """Get post-event feedback analytics"""
    return jsonify(feedback_data)

@app.route('/api/polls', methods=['GET', 'POST', 'DELETE'])
def handle_polls():
    """Manage polls for events"""
    if request.method == 'GET':
        # Return sample polls data
        polls = [
            {'id': 1, 'question': "What's your favorite session topic?", 'responses': 145, 'active': True},
            {'id': 2, 'question': "Rate the venue quality", 'responses': 89, 'active': False}
        ]
        return jsonify({'polls': polls})
    
    elif request.method == 'POST':
        data = request.get_json()
        new_poll = {
            'id': len(polls) + 1 if 'polls' in locals() else 1,
            'question': data.get('question'),
            'responses': 0,
            'active': True
        }
        return jsonify({'message': 'Poll created successfully', 'poll': new_poll}), 201

@app.route('/api/export/<data_type>', methods=['GET'])
def export_data(data_type):
    """Export various data types as CSV/Excel"""
    if data_type == 'revenue':
        # In a real application, generate CSV/Excel file
        return jsonify({'message': f'Revenue data exported successfully', 'download_url': '/downloads/revenue.csv'})
    
    elif data_type == 'feedback':
        return jsonify({'message': f'Feedback data exported successfully', 'download_url': '/downloads/feedback.csv'})
    
    elif data_type == 'engagement':
        return jsonify({'message': f'Engagement data exported successfully', 'download_url': '/downloads/engagement.csv'})
    
    return jsonify({'error': 'Invalid data type'}), 400

@app.route('/api/live-updates', methods=['GET'])
def get_live_updates():
    """Get real-time updates for live events"""
    live_data = {
        'attendance': analytics_data['engagement']['live_attendance'],
        'new_polls': analytics_data['engagement']['active_polls'],
        'qa_questions': analytics_data['engagement']['qa_questions'],
        'timestamp': datetime.now().isoformat()
    }
    return jsonify(live_data)

@app.route('/api/events/<int:event_id>/analytics', methods=['GET'])
def get_event_analytics(event_id):
    """Get analytics for specific event"""
    event = next((e for e in events if e['id'] == event_id), None)
    if not event:
        return jsonify({'error': 'Event not found'}), 404
    
    # Generate mock analytics for the event
    event_analytics = {
        'event': event,
        'revenue': event['ticketPrice'] * event['attendees'],
        'engagement_rate': 75,
        'satisfaction_score': 4.5,
        'attendance_trend': [
            {'time': '10:00', 'attendees': 50},
            {'time': '11:00', 'attendees': 120},
            {'time': '12:00', 'attendees': event['attendees']},
        ]
    }
    return jsonify(event_analytics)

@app.route('/api/events/<int:event_id>/go-live', methods=['POST'])
def go_live_event(event_id):
    """Set event status to live"""
    try:
        # Find the event
        event = next((e for e in events if e['id'] == event_id), None)
        if not event:
            return jsonify({'success': False, 'error': 'Event not found'}), 404
        
        # Update event status to live
        event['status'] = 'live'
        event['live_start_time'] = datetime.now().isoformat()
        
        # Save events data
        save_events(events)
        
        return jsonify({'success': True, 'message': 'Event is now live'})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/events/<int:event_id>/status', methods=['GET'])
def get_event_status(event_id):
    """Get event status"""
    try:
        event = next((e for e in events if e['id'] == event_id), None)
        if not event:
            return jsonify({'error': 'Event not found'}), 404
        
        return jsonify({
            'status': event.get('status', 'upcoming'),
            'live_start_time': event.get('live_start_time')
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/events/<int:event_id>/end-event', methods=['POST'])
def end_event(event_id):
    """End event and set status to completed"""
    try:
        # Find the event
        event = next((e for e in events if e['id'] == event_id), None)
        if not event:
            return jsonify({'success': False, 'error': 'Event not found'}), 404
        
        # Update event status to completed
        event['status'] = 'completed'
        event['end_time'] = datetime.now().isoformat()
        
        # Save events data
        save_events(events)
        
        return jsonify({'success': True, 'message': 'Event ended successfully'})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

def load_engagement_data():
    """Load engagement data from JSON file"""
    global engagement_data
    try:
        if os.path.exists('data/engagement_data.json'):
            with open('data/engagement_data.json', 'r') as f:
                engagement_data = json.load(f)
    except Exception as e:
        print(f"Error loading engagement data: {e}")
        engagement_data = {}

def save_engagement_data():
    """Save engagement data to JSON file"""
    try:
        os.makedirs('data', exist_ok=True)
        with open('data/engagement_data.json', 'w') as f:
            json.dump(engagement_data, f, indent=2)
    except Exception as e:
        print(f"Error saving engagement data: {e}")

def load_tickets_data():
    """Load tickets data from JSON file"""
    global tickets_data
    try:
        if os.path.exists('data/tickets_data.json'):
            with open('data/tickets_data.json', 'r') as f:
                tickets_data = json.load(f)
    except Exception as e:
        print(f"Error loading tickets data: {e}")
        tickets_data = {}

def save_tickets_data():
    """Save tickets data to JSON file"""
    try:
        os.makedirs('data', exist_ok=True)
        with open('data/tickets_data.json', 'w') as f:
            json.dump(tickets_data, f, indent=2)
    except Exception as e:
        print(f"Error saving tickets data: {e}")

@app.route('/api/events/<int:event_id>/polls', methods=['GET', 'POST'])
def manage_polls(event_id):
    """Get or create polls for an event"""
    try:
        if request.method == 'GET':
            # Get polls for this event
            event_engagement = engagement_data.get(str(event_id), {})
            polls = event_engagement.get('polls', [])
            return jsonify({'success': True, 'polls': polls})
        
        elif request.method == 'POST':
            # Create new poll
            poll_data = request.get_json()
            
            # Initialize engagement data for event if not exists
            if str(event_id) not in engagement_data:
                engagement_data[str(event_id)] = {
                    'polls': [],
                    'qa_questions': [],
                    'live_attendance': 0,
                    'engagement_rate': 0
                }
            
            # Create new poll
            new_poll = {
                'id': len(engagement_data[str(event_id)]['polls']) + 1,
                'question': poll_data.get('question'),
                'options': poll_data.get('options', []),
                'responses': poll_data.get('responses', 0),
                'option_votes': {option: 0 for option in poll_data.get('options', [])},  # Track votes per option
                'active': poll_data.get('active', True),
                'created': datetime.now().isoformat()
            }
            
            engagement_data[str(event_id)]['polls'].append(new_poll)
            save_engagement_data()
            
            return jsonify({'success': True, 'poll': new_poll})
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/events/<int:event_id>/polls/<int:poll_id>/vote', methods=['POST'])
def vote_poll(event_id, poll_id):
    """Submit vote for a poll option"""
    try:
        vote_data = request.get_json()
        selected_option = vote_data.get('option')
        
        event_engagement = engagement_data.get(str(event_id), {})
        polls = event_engagement.get('polls', [])
        
        # Find the poll
        poll = next((p for p in polls if p['id'] == poll_id), None)
        if not poll:
            return jsonify({'success': False, 'error': 'Poll not found'}), 404
        
        # Add vote
        if selected_option in poll['option_votes']:
            poll['option_votes'][selected_option] += 1
            poll['responses'] += 1
            save_engagement_data()
            
            return jsonify({'success': True, 'poll': poll})
        else:
            return jsonify({'success': False, 'error': 'Invalid option'}), 400
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/events/<int:event_id>/qa-questions', methods=['GET', 'POST'])
def manage_qa_questions(event_id):
    """Get or create Q&A questions for an event"""
    try:
        if request.method == 'GET':
            # Get Q&A questions for this event
            event_engagement = engagement_data.get(str(event_id), {})
            questions = event_engagement.get('qa_questions', [])
            return jsonify({'success': True, 'questions': questions})
        
        elif request.method == 'POST':
            # Create new Q&A question
            question_data = request.get_json()
            
            # Initialize engagement data for event if not exists
            if str(event_id) not in engagement_data:
                engagement_data[str(event_id)] = {
                    'polls': [],
                    'qa_questions': [],
                    'live_attendance': 0,
                    'engagement_rate': 0
                }
            
            # Create new question
            new_question = {
                'id': len(engagement_data[str(event_id)]['qa_questions']) + 1,
                'question': question_data.get('question'),
                'answered': question_data.get('answered', False),
                'votes': question_data.get('votes', 0),
                'timestamp': datetime.now().isoformat()
            }
            
            engagement_data[str(event_id)]['qa_questions'].append(new_question)
            save_engagement_data()
            
            return jsonify({'success': True, 'question': new_question})
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/events/<int:event_id>/engagement', methods=['GET', 'POST'])
def get_engagement_data(event_id):
    """Get or update engagement data for an event"""
    try:
        if request.method == 'GET':
            # Get engagement data for this event
            event_engagement = engagement_data.get(str(event_id), {
                'polls': [],
                'qa_questions': [],
                'live_attendance': 240,  # Default attendance
                'engagement_rate': 0
            })
            
            # Calculate engagement metrics
            total_polls = len(event_engagement['polls'])
            active_polls = len([p for p in event_engagement['polls'] if p.get('active', False)])
            total_questions = len(event_engagement['qa_questions'])
            
            # Calculate engagement rate based on activity
            total_responses = sum(p.get('responses', 0) for p in event_engagement['polls'])
            engagement_rate = min(75 + (total_responses + total_questions) // 10, 95) if (total_polls > 0 or total_questions > 0) else 0
            
            return jsonify({
                'success': True,
                'live_attendance': event_engagement['live_attendance'],
                'active_polls': active_polls,
                'qa_questions': total_questions,
                'engagement_rate': engagement_rate,
                'polls': event_engagement['polls'],
                'questions': event_engagement['qa_questions'],
                'breakdown': [
                    {'name': 'Poll Participation', 'value': 40},
                    {'name': 'Q&A Sessions', 'value': 32},
                    {'name': 'Chat Activity', 'value': 28}
                ]
            })
        
        elif request.method == 'POST':
            # Update engagement data
            update_data = request.get_json()
            
            if str(event_id) not in engagement_data:
                engagement_data[str(event_id)] = {
                    'polls': [],
                    'qa_questions': [],
                    'live_attendance': 240,
                    'engagement_rate': 0
                }
            
            # Update the data
            engagement_data[str(event_id)].update(update_data)
            save_engagement_data()
            
            return jsonify({'success': True})
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/events/<int:event_id>/tickets', methods=['GET', 'POST'])
def manage_tickets(event_id):
    """Get or update ticket sales for an event"""
    try:
        if request.method == 'GET':
            # Get ticket data for this event
            event_tickets = tickets_data.get(str(event_id), {
                'total_sold': 0,
                'revenue': 0,
                'ticket_types': {}
            })
            return jsonify({'success': True, 'tickets': event_tickets})
        
        elif request.method == 'POST':
            # Update ticket sales
            ticket_data = request.get_json()
            
            if str(event_id) not in tickets_data:
                tickets_data[str(event_id)] = {
                    'total_sold': 0,
                    'revenue': 0,
                    'ticket_types': {}
                }
            
            # Update ticket data
            tickets_data[str(event_id)].update(ticket_data)
            
            # Update live attendance based on ticket sales
            if str(event_id) in engagement_data:
                engagement_data[str(event_id)]['live_attendance'] = ticket_data.get('total_sold', 0)
                save_engagement_data()
            
            save_tickets_data()
            return jsonify({'success': True})
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

# Initialize and load all data on startup
if __name__ == '__main__':
    load_events()
    load_engagement_data()
    load_tickets_data()
    
    print("🚀 COUSREVITA 2 Event Management System")
    print(f"📊 Loaded {len(events)} events")
    print(f"🎯 Loaded engagement data for {len(engagement_data)} events")
    print(f"🎫 Loaded ticket data for {len(tickets_data)} events")
    print("🌐 Server running on http://localhost:5000")
    
    app.run(debug=True, port=5000, host='0.0.0.0')