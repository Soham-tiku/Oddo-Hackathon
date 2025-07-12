from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..extensions import db, limiter
from ..models.vote import Vote, VoteType
from ..models.user import User
from ..models.question import Question
from ..models.answer import Answer
from datetime import datetime

votes_bp = Blueprint('votes', __name__)

def calculate_reputation_change(vote_type, is_question=True):
    """Calculate reputation change based on vote type"""
    if vote_type == VoteType.UP:
        return 10 if is_question else 10
    elif vote_type == VoteType.DOWN:
        return -2 if is_question else -2
    return 0

@votes_bp.route('/', methods=['POST'])
@jwt_required()
@limiter.limit("30 per minute")
def cast_vote():
    """Cast or update a vote"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        question_id = data.get('question_id')
        answer_id = data.get('answer_id')
        vote_type = data.get('vote_type')
        
        # Validate vote type
        if vote_type not in ['up', 'down']:
            return jsonify({'error': 'Invalid vote type. Must be "up" or "down"'}), 400
        
        # Validate target
        if not question_id and not answer_id:
            return jsonify({'error': 'Must specify either question_id or answer_id'}), 400
        
        if question_id and answer_id:
            return jsonify({'error': 'Cannot vote on both question and answer'}), 400
        
        # Get the target content and check ownership
        target_author_id = None
        if question_id:
            question = Question.query.get(question_id)
            if not question:
                return jsonify({'error': 'Question not found'}), 404
            target_author_id = question.author_id
            
        if answer_id:
            answer = Answer.query.get(answer_id)
            if not answer:
                return jsonify({'error': 'Answer not found'}), 404
            target_author_id = answer.author_id
        
        # Prevent self-voting
        if target_author_id == current_user_id:
            return jsonify({'error': 'Cannot vote on your own content'}), 403
        
        # Check for existing vote
        existing_vote = Vote.query.filter_by(
            user_id=current_user_id,
            question_id=question_id,
            answer_id=answer_id
        ).first()
        
        vote_type_enum = VoteType.UP if vote_type == 'up' else VoteType.DOWN
        action = None
        reputation_change = 0
        
        if existing_vote:
            if existing_vote.vote_type == vote_type_enum:
                # Remove vote (toggle off)
                old_reputation_change = calculate_reputation_change(existing_vote.vote_type, bool(question_id))
                reputation_change = -old_reputation_change
                db.session.delete(existing_vote)
                action = 'removed'
            else:
                # Change vote type
                old_reputation_change = calculate_reputation_change(existing_vote.vote_type, bool(question_id))
                new_reputation_change = calculate_reputation_change(vote_type_enum, bool(question_id))
                reputation_change = new_reputation_change - old_reputation_change
                
                existing_vote.vote_type = vote_type_enum
                existing_vote.updated_at = datetime.utcnow()
                action = 'changed'
        else:
            # Create new vote
            new_vote = Vote(
                user_id=current_user_id,
                question_id=question_id,
                answer_id=answer_id,
                vote_type=vote_type_enum
            )
            reputation_change = calculate_reputation_change(vote_type_enum, bool(question_id))
            db.session.add(new_vote)
            action = 'created'
        
        # Update target author's reputation
        if reputation_change != 0:
            target_author = User.query.get(target_author_id)
            if target_author:
                target_author.update_reputation(reputation_change)
        
        db.session.commit()
        
        # Get updated vote counts
        vote_counts = Vote.get_vote_counts(question_id=question_id, answer_id=answer_id)
        
        return jsonify({
            'action': action,
            'vote_counts': vote_counts,
            'reputation_change': reputation_change
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to cast vote'}), 500

@votes_bp.route('/question/<int:question_id>', methods=['GET'])
def get_question_votes(question_id):
    """Get vote counts for a question"""
    try:
        question = Question.query.get(question_id)
        if not question:
            return jsonify({'error': 'Question not found'}), 404
        
        vote_counts = Vote.get_vote_counts(question_id=question_id)
        
        return jsonify({
            'question_id': question_id,
            'vote_counts': vote_counts
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get vote counts'}), 500

@votes_bp.route('/answer/<int:answer_id>', methods=['GET'])
def get_answer_votes(answer_id):
    """Get vote counts for an answer"""
    try:
        answer = Answer.query.get(answer_id)
        if not answer:
            return jsonify({'error': 'Answer not found'}), 404
        
        vote_counts = Vote.get_vote_counts(answer_id=answer_id)
        
        return jsonify({
            'answer_id': answer_id,
            'vote_counts': vote_counts
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get vote counts'}), 500

@votes_bp.route('/user-vote', methods=['GET'])
@jwt_required()
def get_user_vote():
    """Get user's vote for specific question or answer"""
    try:
        current_user_id = get_jwt_identity()
        question_id = request.args.get('question_id', type=int)
        answer_id = request.args.get('answer_id', type=int)
        
        if not question_id and not answer_id:
            return jsonify({'error': 'Must specify question_id or answer_id'}), 400
        
        user_vote = Vote.get_user_vote(
            user_id=current_user_id,
            question_id=question_id,
            answer_id=answer_id
        )
        
        if user_vote:
            return jsonify({
                'vote_type': user_vote.vote_type.value,
                'created_at': user_vote.created_at.isoformat()
            }), 200
        else:
            return jsonify({'vote_type': None}), 200
            
    except Exception as e:
        return jsonify({'error': 'Failed to get user vote'}), 500

@votes_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_vote_stats():
    """Get voting statistics for current user"""
    try:
        current_user_id = get_jwt_identity()
        
        # Get user's vote counts
        user_votes = Vote.query.filter_by(user_id=current_user_id).all()
        upvotes_cast = sum(1 for vote in user_votes if vote.vote_type == VoteType.UP)
        downvotes_cast = sum(1 for vote in user_votes if vote.vote_type == VoteType.DOWN)
        
        # Get votes received on user's content
        user_questions = Question.query.filter_by(author_id=current_user_id).all()
        user_answers = Answer.query.filter_by(author_id=current_user_id).all()
        
        votes_received = 0
        for question in user_questions:
            votes_received += len(Vote.query.filter_by(question_id=question.id).all())
        
        for answer in user_answers:
            votes_received += len(Vote.query.filter_by(answer_id=answer.id).all())
        
        return jsonify({
            'votes_cast': {
                'upvotes': upvotes_cast,
                'downvotes': downvotes_cast,
                'total': upvotes_cast + downvotes_cast
            },
            'votes_received': votes_received
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get vote stats'}), 500
