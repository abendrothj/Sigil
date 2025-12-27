import { NextRequest, NextResponse } from 'next/server';
import { writeFile, readFile, unlink } from 'fs/promises';
import { join } from 'path';
import { spawn } from 'child_process';
import crypto from 'crypto';

export const config = {
  api: {
    bodyParser: {
      sizeLimit: '50mb',
    },
  },
};

// Helper to run Python script
function runPythonScript(scriptPath: string, args: string[]): Promise<string> {
  return new Promise((resolve, reject) => {
    const python = spawn('python3', [scriptPath, ...args]);

    let stdout = '';
    let stderr = '';

    python.stdout.on('data', (data) => {
      stdout += data.toString();
    });

    python.stderr.on('data', (data) => {
      stderr += data.toString();
    });

    python.on('close', (code) => {
      if (code !== 0) {
        reject(new Error(`Python script exited with code ${code}: ${stderr}`));
      } else {
        resolve(stdout);
      }
    });
  });
}

export async function POST(request: NextRequest) {
  try {
    const formData = await request.formData();
    const image = formData.get('image') as File;
    const epsilon = parseFloat(formData.get('epsilon') as string) || 0.01;

    if (!image) {
      return NextResponse.json(
        { error: 'No image provided' },
        { status: 400 }
      );
    }

    // Validate epsilon
    if (epsilon < 0.005 || epsilon > 0.05) {
      return NextResponse.json(
        { error: 'Epsilon must be between 0.005 and 0.05' },
        { status: 400 }
      );
    }

    // Generate unique ID for this request
    const requestId = crypto.randomBytes(16).toString('hex');
    const tmpDir = '/tmp/basilisk';

    // Create temp directory
    await writeFile(join(tmpDir, '.keep'), '').catch(() => {});

    // Save uploaded image
    const bytes = await image.arrayBuffer();
    const buffer = Buffer.from(bytes);

    const inputPath = join(tmpDir, `${requestId}_input${getExtension(image.name)}`);
    const outputPath = join(tmpDir, `${requestId}_output.jpg`);
    const signaturePath = join(tmpDir, `${requestId}_signature.json`);

    await writeFile(inputPath, buffer);

    // Path to poison CLI script
    const poisonScriptPath = join(process.cwd(), '..', 'poison-core', 'poison_cli.py');

    // Run poisoning script
    try {
      await runPythonScript(poisonScriptPath, [
        'poison',
        inputPath,
        outputPath,
        '--epsilon', epsilon.toString(),
        '--device', 'cpu'
      ]);
    } catch (error: any) {
      // Clean up
      await cleanup(inputPath, outputPath, signaturePath);

      return NextResponse.json(
        { error: `Poisoning failed: ${error.message}` },
        { status: 500 }
      );
    }

    // Read results
    const poisonedImageBuffer = await readFile(outputPath);
    const signatureData = JSON.parse(await readFile(signaturePath, 'utf-8'));

    // Convert to base64 for frontend
    const poisonedImageBase64 = `data:image/jpeg;base64,${poisonedImageBuffer.toString('base64')}`;

    // Clean up temp files
    await cleanup(inputPath, outputPath, signaturePath);

    return NextResponse.json({
      success: true,
      poisonedImage: poisonedImageBase64,
      signatureId: signatureData.signature_id || requestId.slice(0, 8),
      signature: signatureData,
    });

  } catch (error: any) {
    console.error('Error in poison API:', error);
    return NextResponse.json(
      { error: error.message || 'Internal server error' },
      { status: 500 }
    );
  }
}

function getExtension(filename: string): string {
  const ext = filename.split('.').pop()?.toLowerCase();
  if (ext === 'jpg' || ext === 'jpeg') return '.jpg';
  if (ext === 'png') return '.png';
  return '.jpg';
}

async function cleanup(...paths: string[]) {
  for (const path of paths) {
    try {
      await unlink(path);
    } catch (e) {
      // Ignore errors
    }
  }
}
