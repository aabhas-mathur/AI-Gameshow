import socketio
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.utils.security import verify_token
from app.services.room_service import RoomService
from app.services.game_service import GameService
from app.services.ai_service import AIService
from app.utils.logger import get_logger
from app.models.round import RoundStatus

logger = get_logger(__name__)

# Create Socket.IO server
sio = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins='*',
    logger=True,
    engineio_logger=False
)


def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        return db
    finally:
        db.close()


@sio.event
async def connect(sid, environ, auth):
    """Handle client connection with JWT authentication"""
    try:
        token = None

        # Try to get token from auth object first
        if auth and 'token' in auth:
            token = auth['token']
        else:
            # Try to get token from cookies
            cookie_header = environ.get('HTTP_COOKIE', '')
            if cookie_header:
                cookies = {}
                for cookie in cookie_header.split(';'):
                    if '=' in cookie:
                        key, value = cookie.strip().split('=', 1)
                        cookies[key] = value
                token = cookies.get('access_token')

        if not token:
            logger.warning(f"Connection attempt without token: {sid}")
            return False

        payload = verify_token(token)
        user_id = payload.get('sub')

        if not user_id:
            logger.warning(f"Invalid token payload: {sid}")
            return False

        # Save user session
        await sio.save_session(sid, {'user_id': user_id})
        logger.info(f"User {user_id} connected: {sid}")

        return True

    except Exception as e:
        logger.error(f"Connection error: {str(e)}")
        return False


@sio.event
async def disconnect(sid):
    """Handle client disconnection"""
    try:
        session = await sio.get_session(sid)
        user_id = session.get('user_id')
        logger.info(f"User {user_id} disconnected: {sid}")
    except:
        logger.info(f"Client disconnected: {sid}")


@sio.event
async def join_room(sid, data):
    """Join a game room"""
    try:
        session = await sio.get_session(sid)
        user_id = session['user_id']
        room_code = data['room_code']

        db = SessionLocal()
        try:
            room = RoomService.get_room(room_code, db)
            participants = RoomService.get_room_participants(room.id, db)

            # Join Socket.IO room
            await sio.enter_room(sid, room_code)

            # Broadcast to room
            await sio.emit('player_joined', {
                'user_id': user_id,
                'participant_count': len(participants)
            }, room=room_code)

            logger.info(f"User {user_id} joined room {room_code}")

            return {'success': True, 'room': room_code}

        finally:
            db.close()

    except Exception as e:
        logger.error(f"Error joining room: {str(e)}")
        return {'success': False, 'error': str(e)}


@sio.event
async def leave_room(sid, data):
    """Leave a game room"""
    try:
        session = await sio.get_session(sid)
        user_id = session['user_id']
        room_code = data['room_code']

        # Leave Socket.IO room
        await sio.leave_room(sid, room_code)

        # Broadcast to room
        await sio.emit('player_left', {
            'user_id': user_id
        }, room=room_code)

        logger.info(f"User {user_id} left room {room_code}")

        return {'success': True}

    except Exception as e:
        logger.error(f"Error leaving room: {str(e)}")
        return {'success': False, 'error': str(e)}


@sio.event
async def start_game(sid, data):
    """Start the game (host only)"""
    try:
        session = await sio.get_session(sid)
        user_id = session['user_id']
        room_code = data['room_code']

        db = SessionLocal()
        try:
            room = GameService.start_game(room_code, user_id, db)

            # Generate all questions for the game upfront
            questions = await AIService.generate_questions(room.total_rounds)
            room.questions = questions
            db.commit()

            logger.info(f"Generated {len(questions)} questions for room {room_code}: {questions}")

            # Start first round with first question
            round_obj = GameService.start_round(room.id, 1, questions[0], db)

            # Broadcast to all players
            await sio.emit('game_started', {
                'round_number': round_obj.round_number,
                'question': round_obj.question,
                'round_id': str(round_obj.id),
                'time_limit': 60,
                'status': 'answering'
            }, room=room_code)

            logger.info(f"Game started in room {room_code}")

            return {'success': True, 'round_id': str(round_obj.id)}

        finally:
            db.close()

    except Exception as e:
        logger.error(f"Error starting game: {str(e)}")
        return {'success': False, 'error': str(e)}


@sio.event
async def submit_answer(sid, data):
    """Submit answer for current round"""
    try:
        session = await sio.get_session(sid)
        user_id = session['user_id']
        round_id = data['round_id']
        answer_content = data['answer']
        room_code = data['room_code']

        db = SessionLocal()
        try:
            answer = GameService.submit_answer(round_id, user_id, answer_content, db)

            # Get submission count
            answers = GameService.get_round_answers(round_id, db)

            # Notify room (without revealing answer content)
            await sio.emit('answer_submitted', {
                'submitted_count': len(answers)
            }, room=room_code)

            logger.info(f"Answer submitted by user {user_id}")

            return {'success': True, 'answer_id': str(answer.id)}

        finally:
            db.close()

    except Exception as e:
        logger.error(f"Error submitting answer: {str(e)}")
        return {'success': False, 'error': str(e)}


@sio.event
async def start_voting(sid, data):
    """Transition to voting phase"""
    try:
        session = await sio.get_session(sid)
        user_id = session['user_id']
        round_id = data['round_id']
        room_code = data['room_code']

        db = SessionLocal()
        try:
            # Verify user is host
            room = RoomService.get_room(room_code, db)
            if str(room.host_id) != user_id:
                return {'success': False, 'error': 'Only host can start voting'}

            round_obj = GameService.start_voting(round_id, db)
            answers = GameService.get_round_answers(round_id, db)

            # Prepare anonymized answers
            answer_list = [
                {
                    'id': str(ans.id),
                    'content': ans.content
                }
                for ans in answers
            ]

            # Broadcast to room
            await sio.emit('voting_started', {
                'round_id': str(round_obj.id),
                'answers': answer_list,
                'time_limit': 45
            }, room=room_code)

            logger.info(f"Voting started for round {round_id}")

            return {'success': True}

        finally:
            db.close()

    except Exception as e:
        logger.error(f"Error starting voting: {str(e)}")
        return {'success': False, 'error': str(e)}


@sio.event
async def submit_vote(sid, data):
    """Submit vote for an answer"""
    try:
        session = await sio.get_session(sid)
        user_id = session['user_id']
        round_id = data['round_id']
        answer_id = data['answer_id']
        room_code = data['room_code']

        db = SessionLocal()
        try:
            vote = GameService.submit_vote(round_id, user_id, answer_id, db)

            # Get updated vote count
            vote_count = GameService.get_answer_vote_count(answer_id, db)

            # Broadcast real-time vote update
            await sio.emit('vote_update', {
                'answer_id': answer_id,
                'vote_count': vote_count
            }, room=room_code)

            logger.info(f"Vote submitted by user {user_id}")

            return {'success': True, 'vote_id': str(vote.id)}

        finally:
            db.close()

    except Exception as e:
        logger.error(f"Error submitting vote: {str(e)}")
        return {'success': False, 'error': str(e)}


@sio.event
async def end_round(sid, data):
    """End current round and show results"""
    try:
        session = await sio.get_session(sid)
        user_id = session['user_id']
        round_id = data['round_id']
        room_code = data['room_code']

        db = SessionLocal()
        try:
            room = RoomService.get_room(room_code, db)

            # Verify user is host
            if str(room.host_id) != user_id:
                return {'success': False, 'error': 'Only host can end round'}

            round_obj = GameService.end_round(round_id, db)
            leaderboard = GameService.get_leaderboard(room.id, db)

            # Broadcast results
            await sio.emit('round_ended', {
                'round_number': round_obj.round_number,
                'leaderboard': leaderboard
            }, room=room_code)

            # Check if game should end
            if room.current_round >= room.total_rounds:
                GameService.end_game(room.id, db)
                await sio.emit('game_ended', {
                    'final_leaderboard': leaderboard
                }, room=room_code)

            logger.info(f"Round {round_id} ended")

            return {'success': True}

        finally:
            db.close()

    except Exception as e:
        logger.error(f"Error ending round: {str(e)}")
        return {'success': False, 'error': str(e)}


@sio.event
async def next_round(sid, data):
    """Start next round"""
    try:
        session = await sio.get_session(sid)
        user_id = session['user_id']
        room_code = data['room_code']

        db = SessionLocal()
        try:
            room = RoomService.get_room(room_code, db)

            # Verify user is host
            if str(room.host_id) != user_id:
                return {'success': False, 'error': 'Only host can start next round'}

            # Get next question from pre-generated questions
            next_round_num = room.current_round + 1
            if room.questions and len(room.questions) >= next_round_num:
                question = room.questions[next_round_num - 1]  # 0-indexed
            else:
                # Fallback if questions weren't generated properly
                logger.warning(f"No pre-generated question for round {next_round_num}, generating new one")
                question = await AIService.generate_question()

            round_obj = GameService.start_round(room.id, next_round_num, question, db)

            # Broadcast to room
            await sio.emit('round_started', {
                'round_number': round_obj.round_number,
                'question': round_obj.question,
                'round_id': str(round_obj.id),
                'time_limit': 60
            }, room=room_code)

            logger.info(f"Round {round_obj.round_number} started in room {room_code}")

            return {'success': True, 'round_id': str(round_obj.id)}

        finally:
            db.close()

    except Exception as e:
        logger.error(f"Error starting next round: {str(e)}")
        return {'success': False, 'error': str(e)}