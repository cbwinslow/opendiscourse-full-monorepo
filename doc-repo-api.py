from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime
import os

app = Flask(__name__)

# Configure PostgreSQL connection
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://doc_user:doc_password123@localhost/doc_repo'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    updated_at = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    metadata = db.Column(JSONB)
    versions = db.relationship('DocumentVersion', backref='document', lazy=True)

class DocumentVersion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey('document.id'), nullable=False)
    version_number = db.Column(db.Integer, nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    metadata = db.Column(JSONB)

@app.route('/api/v1/documents', methods=['POST'])
def create_document():
    data = request.get_json()
    
    if not data or not 'title' in data or not 'content' in data:
        return jsonify({'error': 'Missing required fields'}), 400
    
    document = Document(
        title=data['title'],
        content=data['content'],
        metadata=data.get('metadata', {})
    )
    
    db.session.add(document)
    db.session.commit()
    
    # Create first version
    version = DocumentVersion(
        document_id=document.id,
        version_number=1,
        content=data['content'],
        metadata=data.get('metadata', {})
    )
    db.session.add(version)
    db.session.commit()
    
    return jsonify({
        'id': document.id,
        'title': document.title,
        'created_at': document.created_at.isoformat()
    }), 201

@app.route('/api/v1/documents/<int:doc_id>', methods=['GET'])
def get_document(doc_id):
    document = Document.query.get_or_404(doc_id)
    return jsonify({
        'id': document.id,
        'title': document.title,
        'content': document.content,
        'created_at': document.created_at.isoformat(),
        'updated_at': document.updated_at.isoformat(),
        'metadata': document.metadata
    })

@app.route('/api/v1/documents/<int:doc_id>', methods=['PUT'])
def update_document(doc_id):
    document = Document.query.get_or_404(doc_id)
    data = request.get_json()
    
    if not data or not 'content' in data:
        return jsonify({'error': 'Missing content'}), 400
    
    # Create new version
    version = DocumentVersion(
        document_id=document.id,
        version_number=len(document.versions) + 1,
        content=data['content'],
        metadata=data.get('metadata', {})
    )
    db.session.add(version)
    
    # Update document
    document.content = data['content']
    document.metadata = data.get('metadata', {})
    document.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({'message': 'Document updated successfully'}), 200

@app.route('/api/v1/documents/<int:doc_id>/versions', methods=['GET'])
def get_document_versions(doc_id):
    document = Document.query.get_or_404(doc_id)
    versions = DocumentVersion.query.filter_by(document_id=doc_id).order_by(DocumentVersion.version_number.desc()).all()
    return jsonify([{
        'version_number': v.version_number,
        'created_at': v.created_at.isoformat(),
        'metadata': v.metadata
    } for v in versions])

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000)
