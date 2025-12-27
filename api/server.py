#!/usr/bin/env python3
"""
Basilisk API Server
Flask backend for image poisoning service
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import sys
import json
import hashlib
from pathlib import Path
import tempfile
import base64
from io import BytesIO

# Add poison-core to path
sys.path.append(str(Path(__file__).parent.parent / 'poison-core'))

try:
    from radioactive_poison import RadioactiveMarker
except ImportError as e:
    print(f"Error importing radioactive_poison: {e}")
    print("Make sure poison-core is in the correct location")
    sys.exit(1)

app = Flask(__name__)
CORS(app)

# Configuration
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
TEMP_DIR = Path(tempfile.gettempdir()) / 'basilisk'
TEMP_DIR.mkdir(exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'basilisk-api',
        'version': '0.1.0'
    })


@app.route('/api/poison', methods=['POST'])
def poison_image():
    """
    Poison an uploaded image

    Request:
        - image: File upload
        - epsilon: float (optional, default 0.01)

    Response:
        - success: bool
        - poisoned_image: base64 encoded image
        - signature_id: string
        - signature: signature data (JSON)
    """
    try:
        # Validate request
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400

        file = request.files['image']
        if file.filename == '':
            return jsonify({'error': 'Empty filename'}), 400

        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type. Use PNG or JPG'}), 400

        # Get parameters
        epsilon = float(request.form.get('epsilon', 0.01))
        pgd_steps = int(request.form.get('pgd_steps', 1))

        # Validate epsilon
        if epsilon < 0.005 or epsilon > 0.05:
            return jsonify({'error': 'Epsilon must be between 0.005 and 0.05'}), 400

        # Validate PGD steps
        if pgd_steps < 1 or pgd_steps > 20:
            return jsonify({'error': 'PGD steps must be between 1 and 20'}), 400

        # Generate unique ID
        request_id = hashlib.sha256(os.urandom(32)).hexdigest()[:16]

        # Save uploaded file
        filename = secure_filename(file.filename)
        ext = filename.rsplit('.', 1)[1].lower()
        input_path = TEMP_DIR / f"{request_id}_input.{ext}"
        output_path = TEMP_DIR / f"{request_id}_output.jpg"
        signature_path = TEMP_DIR / f"{request_id}_signature.json"

        file.save(str(input_path))

        # Initialize marker
        print(f"Poisoning image with epsilon={epsilon}, pgd_steps={pgd_steps}")
        marker = RadioactiveMarker(epsilon=epsilon, device='cpu')

        # Generate signature
        marker.generate_signature()

        # Save signature first
        marker.save_signature(str(signature_path))

        # Poison image
        try:
            marker.poison_image(
                str(input_path),
                str(output_path),
                normalize=True,
                pgd_steps=pgd_steps
            )
        except Exception as e:
            # Clean up
            cleanup_files(input_path, output_path, signature_path)
            return jsonify({'error': f'Poisoning failed: {str(e)}'}), 500

        # Read results
        with open(output_path, 'rb') as f:
            poisoned_image_bytes = f.read()

        with open(signature_path, 'r') as f:
            signature_data = json.load(f)

        # Encode image as base64
        poisoned_image_base64 = base64.b64encode(poisoned_image_bytes).decode('utf-8')

        # Generate signature ID
        signature_id = hashlib.sha256(str(signature_data['seed']).encode()).hexdigest()[:16]

        # Clean up temp files
        cleanup_files(input_path, output_path, signature_path)

        return jsonify({
            'success': True,
            'poisoned_image': f'data:image/jpeg;base64,{poisoned_image_base64}',
            'signature_id': signature_id,
            'signature': signature_data
        })

    except ValueError as e:
        return jsonify({'error': f'Invalid input: {str(e)}'}), 400
    except Exception as e:
        print(f"Error in poison_image: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Server error: {str(e)}'}), 500


@app.route('/api/batch', methods=['POST'])
def batch_poison():
    """
    Poison multiple images at once

    Request:
        - images: Multiple file uploads
        - epsilon: float (optional, default 0.01)

    Response:
        - success: bool
        - results: list of poisoning results
        - signature_id: shared signature ID
        - signature: signature data
    """
    try:
        if 'images' not in request.files:
            return jsonify({'error': 'No images provided'}), 400

        files = request.files.getlist('images')
        if len(files) == 0:
            return jsonify({'error': 'No images uploaded'}), 400

        if len(files) > 100:
            return jsonify({'error': 'Maximum 100 images per batch'}), 400

        epsilon = float(request.form.get('epsilon', 0.01))
        pgd_steps = int(request.form.get('pgd_steps', 1))

        # Validate parameters
        if epsilon < 0.005 or epsilon > 0.05:
            return jsonify({'error': 'Epsilon must be between 0.005 and 0.05'}), 400
        if pgd_steps < 1 or pgd_steps > 20:
            return jsonify({'error': 'PGD steps must be between 1 and 20'}), 400

        # Initialize marker with single signature for all images
        print(f"Batch poisoning with epsilon={epsilon}, pgd_steps={pgd_steps}")
        marker = RadioactiveMarker(epsilon=epsilon, device='cpu')
        marker.generate_signature()

        # Generate signature ID
        request_id = hashlib.sha256(os.urandom(32)).hexdigest()[:16]
        signature_path = TEMP_DIR / f"batch_{request_id}_signature.json"
        marker.save_signature(str(signature_path))

        with open(signature_path, 'r') as f:
            signature_data = json.load(f)

        signature_id = hashlib.sha256(str(signature_data['seed']).encode()).hexdigest()[:16]

        # Process each image
        results = []
        temp_files = []

        for idx, file in enumerate(files):
            if not allowed_file(file.filename):
                continue

            try:
                filename = secure_filename(file.filename)
                ext = filename.rsplit('.', 1)[1].lower()
                input_path = TEMP_DIR / f"{request_id}_{idx}_input.{ext}"
                output_path = TEMP_DIR / f"{request_id}_{idx}_output.jpg"

                temp_files.extend([input_path, output_path])

                file.save(str(input_path))
                marker.poison_image(str(input_path), str(output_path), pgd_steps=pgd_steps)

                with open(output_path, 'rb') as f:
                    poisoned_bytes = f.read()

                poisoned_base64 = base64.b64encode(poisoned_bytes).decode('utf-8')

                results.append({
                    'original_name': filename,
                    'success': True,
                    'poisoned_image': f'data:image/jpeg;base64,{poisoned_base64}'
                })

            except Exception as e:
                results.append({
                    'original_name': file.filename,
                    'success': False,
                    'error': str(e)
                })

        # Clean up
        cleanup_files(signature_path, *temp_files)

        return jsonify({
            'success': True,
            'results': results,
            'signature_id': signature_id,
            'signature': signature_data,
            'total': len(files),
            'successful': sum(1 for r in results if r.get('success'))
        })

    except Exception as e:
        print(f"Error in batch_poison: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Server error: {str(e)}'}), 500


def cleanup_files(*paths):
    """Remove temporary files"""
    for path in paths:
        try:
            if isinstance(path, Path):
                path.unlink(missing_ok=True)
            else:
                Path(path).unlink(missing_ok=True)
        except Exception as e:
            print(f"Warning: Failed to clean up {path}: {e}")


if __name__ == '__main__':
    print("=" * 60)
    print("🐍 Basilisk API Server")
    print("=" * 60)
    print("Starting Flask server on http://localhost:5000")
    print("Endpoints:")
    print("  GET  /health          - Health check")
    print("  POST /api/poison      - Poison single image")
    print("  POST /api/batch       - Poison multiple images")
    print("=" * 60)

    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )
